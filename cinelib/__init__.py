from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cinelib.db"

database = SQLAlchemy(app)

@app.route('/')
def home():
    return render_template('index.html')