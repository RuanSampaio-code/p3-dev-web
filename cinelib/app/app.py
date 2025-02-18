from flask import Flask

app = Flask(__name__)

#teste

@app.route('/')
def home():
    return "Olá, Flask!"

if __name__ == '__main__':
    app.run(debug=True)