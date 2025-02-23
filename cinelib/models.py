from cinelib import database

class Usuario(database.Model):
    id = database.Column(database.Integer, primary_key = True)
    username = database.Column(database.String, nullable=False)
    email = database.Column(database.String, nullable=False, unique=True)
    senha = database.Column(database.String, nullable=False)
    filme = database.relationship("Filmes", backref="usuario", lazy=True)
    serie = database.relationship("Series", backref="usuario", lazy=True)

class Filmes(database.Model):
    id = database.Column(database.Integer, primary_key = True)
    titulo_filme = database.Column(database.String, nullable=False)
    sinopse = database.Column(database.String, nullable=False)
    ano = database.Column(database.DateTime, nullable=False)
    genero = database.Column(database.String, nullable=False)
    duracao = database.Column(database.Integer, nullable=False)
    foto = database.Column(database.String)
    id_usuario = database.Column(database.Integer, database.ForeignKey("usuario.id") ,nullable=False)

class Series(database.Model):
    id = database.Column(database.Integer, primary_key = True)
    titulo = database.Column(database.String, nullable=False)
    sinopse = database.Column(database.String, nullable=False)
    ano = database.Column(database.DateTime, nullable=False)
    genero = database.Column(database.String, nullable=False)
    duracao = database.Column(database.Integer, nullable=False)
    foto = database.Column(database.String)
    id_usuario = database.Column(database.Integer, database.ForeignKey("usuario.id") ,nullable=False)