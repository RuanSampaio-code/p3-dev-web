from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError


class FormLogin(FlaskForm):
    usuario = StringField("Usuario", validators=[DataRequired()])
    senha = PasswordField("Senha", validators=[DataRequired()])
    botao_submit = SubmitField("Entrar")

class FormCadastro(FlaskForm):
    usuario = StringField("Usuario", validators=[DataRequired()])
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    senha =  PasswordField("Senha", validators=[DataRequired(), Length(6, 20)])
    confirmar_senha = PasswordField("Confirmar senha", DataRequired(), EqualTo("senha"))
    botao_submit = SubmitField("Entrar")
