import requests, os 
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify

#Lib para banco de dados
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sqlite3 

#Lib auteticação
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = 'sua_chave_super_secreta'  # Substitua por algo único e seguro

# Sua chave de API do TMDb (substitua pela sua)
TMDB_API_KEY = os.getenv('FLASK_API_KEY_TMDB')
TMDB_BASE_URL = "https://api.themoviedb.org/3/"

# Configurar a URI do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cinelib.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)

# ---------------------------------------------------------------------------------Modelos - BANCO DE DADOS -------------------------------------------------------------
class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    catalogos = db.relationship("Catalogo", backref="usuario", lazy=True)  # Relacionamento 1:N

    def __repr__(self):
        return f'<Usuario {self.nome}>'

class Catalogo(db.Model):
    __tablename__ = "catalogo"
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    sinopse = db.Column(db.String(500), nullable=False)
    ano = db.Column(db.Integer, nullable=False)  # Ano de lançamento
    genero = db.Column(db.String(100), nullable=False)
    duracao = db.Column(db.Integer, nullable=False)  # Minutos para filmes / episódios para séries
    foto = db.Column(db.String(255))
    tipo = db.Column(db.String(50), nullable=False)  # Pode ser "Filme" ou "Série"
    assistido = db.Column(db.Boolean, default=False, nullable=False)  # Indica se já foi assistido
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)  # Chave estrangeira

    # Novo campo de nota, com valor entre 0 e 10
    nota = db.Column(db.Float, nullable=True)  # Pode ser nulo ou com valores entre 0 e 10

    
    def set_nota(self, nota):
        if 0 <= nota <= 10:
            self.nota = nota
        else:
            raise ValueError("A nota deve estar entre 0 e 10.")

    def __repr__(self):
        return f'<Catalogo {self.titulo}>'



# -------------------------------------------------------------------------------ROTAS  INICIAIS

# Rota inicial - Login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.senha == senha:
            login_user(usuario)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('home'))
        else:
            flash('E-mail ou senha incorretos.', 'danger')

    return render_template('login.html')

#pagina sobre
@app.route('/sobre')
def sobre():
    return render_template('sobre.html')



#Rota para Sair da aplicação
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login'))

    
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


# Pagina de cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()

        # Validações básicas
        if not nome or not email or not senha:
            flash('Todos os campos são obrigatórios.', 'warning')
            return redirect(url_for('register'))

        if Usuario.query.filter_by(email=email).first():
            flash('E-mail já registrado!', 'danger')
            return redirect(url_for('register'))

        try:
            hashed_password = generate_password_hash(senha)
            novo_usuario = Usuario(nome=nome, email=email, senha=hashed_password)
            db.session.add(novo_usuario)
            db.session.commit()
            flash('Conta criada com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
        except Exception:
            db.session.rollback()
            flash('Erro ao criar conta. Tente novamente.', 'danger')

    return render_template('cadastro.html')


#Pagina Home
@app.route('/home')
@login_required  # Usuário precisa estar logado para acessar
def home():
    genres = {
        "Ação": 28,
        "Comédia": 35,
        "Drama": 18,
        "Ficção Científica": 878,
        "Terror": 27
    }

    movies = {genre: get_unique_items_by_genre(genre_id, media_type="movie") for genre, genre_id in genres.items()}
    series = {genre: get_unique_items_by_genre(genre_id, media_type="tv") for genre, genre_id in genres.items()}

    return render_template('home.html', movies=movies, series=series)


#Pagina da biblioteca
@app.route('/biblioteca', methods=['GET', 'POST'])
@login_required
def pageBiblioteca(): 
    return render_template('biblioteca.html')





#Pagina de lista de filmes e series para assitir
@app.route('/biblioteca/ListaParaAssitir', methods=['GET', 'POST'])
@login_required
def pageListaParaAssistir(): 
    return render_template('filmeSerieParaAssistir.html')


#Pagina de lista de filmes e series já assistidos
@app.route('/biblioteca/ListaJaAssitido', methods=['GET', 'POST'])
@login_required
def pageListaJaAssistido(): 
    return render_template('filmeSerieAssistido.html')


#pagina de perfil
@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def pagePerfil():
    if request.method == 'POST':
        # Captura os dados do formulário
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')

        # Atualiza os dados do usuário logado
        current_user.nome = nome
        current_user.email = email
        if senha:  # Atualiza a senha apenas se o usuário inseriu uma nova
            current_user.senha = generate_password_hash(senha)

        # Salva no banco
        db.session.commit()
        flash("Perfil atualizado com sucesso!", "success")
        return redirect(url_for('pagePerfil'))

    return render_template('perfil.html', usuario=current_user)



def get_tmdb_data(endpoint, params={}):
    """Função para buscar dados da API TMDb"""
    base_url = TMDB_BASE_URL
    params['api_key'] = TMDB_API_KEY
    params['language'] = 'pt-BR'
    
    response = requests.get(base_url + endpoint, params=params)
    
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

#Pagina de recomendacao
@app.route('/recomedacao', methods=['GET', 'POST'])
@login_required
def pageRecomedacao(): 
    # Filmes e séries populares
    filmes_populares = get_tmdb_data('movie/popular', {'page': 1})[:5]
    series_populares = get_tmdb_data('tv/popular', {'page': 1})[:5]

    # Filmes e séries mais bem avaliados
    filmes_top = get_tmdb_data('movie/top_rated', {'page': 1})[:5]
    series_top = get_tmdb_data('tv/top_rated', {'page': 1})[:5]

    # Misturando os filmes e séries em grupos
    recomendacoes_populares = filmes_populares + series_populares
    recomendacoes_top = filmes_top + series_top

    return render_template('recomendacao.html', 
                           recomendacoes_populares=recomendacoes_populares, 
                           recomendacoes_top=recomendacoes_top)


#Tratando a api

@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query')

    if not query:
        return jsonify({"error": "Nenhum termo de busca fornecido"}), 400

    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
    
    response = requests.get(url)
    data = response.json()

    print("Resultados da pesquisa:", data)  # Verifique se os resultados estão corretos

    # Passando os resultados para a página de resultados
    return render_template('pesquisaCatalogo.html', movies=data.get('results', []))



def get_unique_items_by_genre(genre_id, num_items=5, media_type="movie"):
    """Busca itens únicos de um gênero específico"""
    url = f"https://api.themoviedb.org/3/discover/{media_type}?api_key={TMDB_API_KEY}&language=pt-BR&sort_by=popularity.desc&with_genres={genre_id}"
    response = requests.get(url)
    data = response.json()
    
    unique_items = []
    seen_ids = set()

    for item in data.get("results", []):
        item_id = item.get("id")
        if item_id not in seen_ids and item.get("poster_path"):  # Evita repetições e imagens vazias
            seen_ids.add(item_id)
            unique_items.append(item)
        if len(unique_items) == num_items:
            break  # Para quando alcançar o limite
    
    return unique_items


#Funcionalidade de adcionar ao catalogo
@app.route('/adicionar_catalogo', methods=['POST'])
@login_required
def adicionar_catalogo():
    data = request.get_json()
    
    # Verificação simplificada dos dados obrigatórios
    required_fields = ['id', 'titulo', 'tipo', 'poster_path']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Campo obrigatório faltando: {field}"}), 400
    
    # Construir URL da imagem corretamente (poster_path já inclui a barra)
    foto_url = f"https://image.tmdb.org/t/p/w200{data['poster_path']}"
    
    novo_item = Catalogo(
        titulo=data['titulo'],
        sinopse=data['sinopse'],
        ano=int(data['ano']),
        genero='Desconhecido',  # Você pode buscar o gênero da API se necessário
        duracao=120,  # Ajuste conforme os dados da API
        foto=foto_url,  # Usando a URL construída
        tipo=data['tipo'],
        assistido=data['assistido'],
        id_usuario=current_user.id
    )
    
    db.session.add(novo_item)
    db.session.commit()
    
    return jsonify({"success": True})


# Conectando ao banco de dados e recuperando os filmes cadastrados para ver futuramente
def get_filmes_para_assistir():
    # Conecte-se ao banco de dados (substitua pelo seu banco de dados)
    conn = sqlite3.connect('instance/cinelib.db')
    cursor = conn.cursor()
    cursor.execute("SELECT titulo, ano, sinopse, duracao, foto FROM Catalogo WHERE assistido = 0")  # 0 significa não assistido
    obras = cursor.fetchall()
    conn.close()
    return obras

@app.route('/lista-para-assistir')
@login_required
def lista_para_assistir():
    obras = get_filmes_para_assistir()
    return render_template('lista_para_assistir.html', obras=obras)


# Conectando ao banco de dados e recuperando os filmes
def get_filmes_ja_assistidos():
    # Conecte-se ao banco de dados (substitua pelo seu banco de dados)
    conn = sqlite3.connect('instance/cinelib.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id,titulo, ano, sinopse, duracao, foto, nota FROM Catalogo WHERE assistido = 1")  # 0 significa não assistido
    obras = cursor.fetchall()
    conn.close()
    return obras

#Lista de filmes ja assitidos
@app.route('/lista-ja-assitidos')
@login_required
def lista_ja_assistidos():
    obras = get_filmes_ja_assistidos()
    return render_template('lista_ja_assistidos.html', obras=obras)


#Funcionalide de adcionar uma nota a um filme ja assitido
@app.route('/salvar_nota/<int:obra_id>', methods=['GET', 'POST'])
@login_required
def salvar_nota(obra_id):
    # Obtenha o filme do banco de dados pelo id
    obra = db.session.get(Catalogo, obra_id) 

    if request.method == 'POST':
        # Obtenha a nota enviada pelo formulário
        nova_nota = request.form.get('nota')
        
        if nova_nota:
            # Converta para float e atribua à obra
            obra.nota = float(nova_nota)
            
            # Salve a alteração no banco de dados
            db.session.commit()

            # Redirecione de volta para a página do filme (ou onde preferir)
            return redirect(url_for('lista_ja_assistidos', obra_id=obra.id))

    # Renderize o template com as informações do filme
    return render_template('lista_ja_assistidos.html', obra=obra)


if __name__ == '__main__':
    app.run(debug=True)


# Criar as tabelas no banco de dados
""" with app.app_context():
    db.create_all()
    print("Tabelas criadas com sucesso!") """

