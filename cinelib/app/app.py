from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
import requests  # requests deve ser importado separadamente


#Lib para banco de dados
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sqlite3  # Ou qualquer outro banco de dados que você esteja usando

#Lib auteticação
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash


app = Flask(__name__)

app.secret_key = 'sua_chave_super_secreta'  # Substitua por algo único e seguro

# Sua chave de API do TMDb (substitua pela sua)
TMDB_API_KEY = "3b653dd935ec9fc21b679170f3bff41a"
TMDB_BASE_URL = "https://api.themoviedb.org/3"



# Configurar a URI do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cinelib.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
migrate = Migrate(app, db)


login_manager = LoginManager(app)


#Modelos
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

    # Validação de nota (opcional, dependendo da biblioteca que você está usando)
    def set_nota(self, nota):
        if 0 <= nota <= 10:
            self.nota = nota
        else:
            raise ValueError("A nota deve estar entre 0 e 10.")

    def __repr__(self):
        return f'<Catalogo {self.titulo}>'




""" Rota inicial """

#Login
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


#Home
@app.route('/home')
@login_required  # Usuário precisa estar logado para acessar
def home():
    return render_template('home.html')  # Certifique-se de ter um home.html no templates

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


#cadastro
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


#Pagina de recomendacao
@app.route('/recomedacao', methods=['GET', 'POST'])
@login_required
def pageRecomedacao(): 
    return render_template('recomendacao.html')

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


















#Tratando a api
""" @app.route('/search', methods=['GET'])
def search_movie():
    query = request.args.get('query')  # Obtém o termo da pesquisa do input
    if not query:
        return jsonify({"error": "Nenhuma pesquisa foi fornecida"}), 400

    # Fazendo a requisição à API do TMDb
    url = f"{TMDB_BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={query}"
    response = requests.get(url)
    
    if response.status_code != 200:
        return jsonify({"error": "Erro ao buscar filmes"}), 500

    data = response.json()
    return jsonify(data)  """ # Retorna os dados da API como JSON

@app.route('/search', methods=['GET'])
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




@app.route('/adicionar_catalogo', methods=['POST'])
def adicionar_catalogo():
    data = request.get_json()
    
    # Verificar se os dados necessários estão presentes
    if not data.get('id') or not data.get('titulo') or not data.get('tipo'):
        return jsonify({"error": "Dados incompletos."}), 400

    # Criar um novo objeto Catalogo
    novo_item = Catalogo(
        titulo=data['titulo'],
        sinopse=data['sinopse'],
        ano=int(data['ano']),
        genero='Desconhecido',  # Você pode ajustar isso conforme a resposta da API
        duracao=120,  # Aqui também você pode ajustar conforme a resposta da API (exemplo de duração de 120 minutos)
        foto = f"https://image.tmdb.org/t/p/w200{data.get('poster_path', '')}",

       # https://image.tmdb.org/t/p/w200/3onmLeu48mY87UclP3fk2x7YPqw.jpg
 # Usa o get() para evitar erro se a chave não existir
  # Altere 'foto' para 'poster_path'
 # Adicione a foto do filme/série
        tipo=data['tipo'],
        assistido=data['assistido'],
        id_usuario=current_user.id  # Supondo que você tenha um sistema de autenticação para pegar o usuário atual
    )

    # Adicionar no banco de dados
    db.session.add(novo_item)
    db.session.commit()

    return jsonify({"success": True})





# Conectando ao banco de dados e recuperando os filmes
def get_filmes_para_assistir():
    # Conecte-se ao banco de dados (substitua pelo seu banco de dados)
    conn = sqlite3.connect('instance/cinelib.db')
    cursor = conn.cursor()
    cursor.execute("SELECT titulo, ano, sinopse, duracao, foto FROM Catalogo WHERE assistido = 0")  # 0 significa não assistido
    obras = cursor.fetchall()
    conn.close()
    return obras

@app.route('/lista-para-assistir')
def lista_para_assistir():
    obras = get_filmes_para_assistir()
    return render_template('lista_para_assistir.html', obras=obras)



# Conectando ao banco de dados e recuperando os filmes
def get_filmes_ja_assistidos():
    # Conecte-se ao banco de dados (substitua pelo seu banco de dados)
    conn = sqlite3.connect('instance/cinelib.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id,titulo, ano, sinopse, duracao, foto FROM Catalogo WHERE assistido = 1")  # 0 significa não assistido
    obras = cursor.fetchall()
    conn.close()
    return obras

@app.route('/lista-ja-assitidos')
def lista_ja_assistidos():
    obras = get_filmes_ja_assistidos()
    return render_template('lista_ja_assistidos.html', obras=obras)


@app.route('/salvar_nota/<int:obra_id>', methods=['POST'])
def salvar_nota(obra_id):
    nota = request.form.get('nota')
    if nota:
        # Salvar a nota no banco de dados para o filme com ID `obra_id`
        # Adapte esse código conforme sua lógica de banco de dados
        obra = Catalogo.query.get(obra_id)  # Exemplo com SQLAlchemy
        obra.nota = nota
        db.session.commit()
        return redirect(url_for('lista_ja_assistidos'))  # Redireciona para a lista de filmes
    return "Nota não salva", 400












if __name__ == '__main__':
    app.run(debug=True)


# Criar as tabelas no banco de dados
""" with app.app_context():
    db.create_all()
    print("Tabelas criadas com sucesso!") """

