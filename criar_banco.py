from cinelib import database, app
from cinelib.models import Usuario, Catalogo

with app.app_context():
    database.create_all()