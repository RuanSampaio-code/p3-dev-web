from cinelib import database
from cinelib import database

class Usuario(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String, nullable=False)
    email = database.Column(database.String, nullable=False, unique=True)
    senha = database.Column(database.String, nullable=False)
    midias = database.relationship("Midia", backref="usuario", lazy=True)  # Relacionamento 1:N

class Catalogo(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    titulo = database.Column(database.String, nullable=False)
    sinopse = database.Column(database.String, nullable=False)
    ano = database.Column(database.Integer, nullable=False)  # Ano de lançamento
    genero = database.Column(database.String, nullable=False)
    duracao = database.Column(database.Integer, nullable=False)  # Minutos para filmes / episódios para séries
    foto = database.Column(database.String)
    tipo = database.Column(database.String, nullable=False)  # Pode ser "Filme" ou "Série"
    assistido = database.Column(database.Boolean, default=False, nullable=False)  # Indica se já foi assistido
    id_usuario = database.Column(database.Integer, database.ForeignKey("usuario.id"), nullable=False)  # Chave estrangeira
