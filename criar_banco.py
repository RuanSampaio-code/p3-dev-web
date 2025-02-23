from cinelib import database, app
from cinelib.models import Usuario, Filmes, Series

with app.app_context():
    database.create_all()