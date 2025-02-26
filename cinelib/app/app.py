from flask import Flask, render_template, redirect, url_for, request, flash

#Lib para banco de dados
from flask_sqlalchemy import SQLAlchemy

#Lib auteticação
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash


app = Flask(__name__)

app.secret_key = 'sua_chave_super_secreta'  # Substitua por algo único e seguro


# Configurar a URI do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cinelib.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


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

if __name__ == '__main__':
    app.run(debug=True)


# Criar as tabelas no banco de dados
""" with app.app_context():
    db.create_all()
    print("Tabelas criadas com sucesso!") """