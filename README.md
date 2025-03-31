# CineLib - Gerenciador de Filmes e Séries

## Descrição
CineLib é uma aplicação web desenvolvida para a disciplina **Desenvolvimento Web de Sistemas**. O objetivo do projeto é oferecer um gerenciador de filmes e séries, permitindo aos usuários catalogar, avaliar e visualizar informações detalhadas sobre suas obras favoritas. A aplicação utiliza a API **TMDB** para fornecer dados atualizados sobre filmes e séries.

## Tecnologias Utilizadas
- **Flask** - Framework web para backend em Python
- **SQLAlchemy** - ORM para gerenciamento do banco de dados
- **Jinja2** - Template engine para renderização de páginas dinâmicas
- **Bootstrap** - Framework CSS para estilização
- **TMDB API** - Para obtenção de informações sobre filmes e séries

## Funcionalidades
- 📌 **Cadastro e Login de Usuários**  
- 🎬 **Busca de Filmes e Séries via API TMDB**  
- ⭐ **Avaliação de Filmes e Séries (Nota de 1 a 10)**  
- 📋 **Gerenciamento de Filmes/Séries Assistidos**  
- 🔍 **Filtragem e Ordenação de Conteúdo**  
- 💾 **Persistência de Dados no Banco SQLITE**  

## Como Executar o Projeto

### 1. Clonar o Repositório
```bash
  git clone [https://github.com/seu-usuario/cinelib.git](https://github.com/RuanSampaio-code/p3-dev-web.git)
  cd cinelib
```

### 2. Criar e Ativar o Ambiente Virtual
```bash
  python -m venv venv
  source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 3. Instalar as Dependências
```bash
  pip install -r requirements.txt
```

### 5. Executar a Aplicação
```bash
  cd app
  python app.py
```
Acesse no navegador: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Estrutura do Projeto
```
/
|-- static/         # Arquivos CSS, JS, imagens
|-- templates/      # Templates HTML (Jinja2)
|-- app.py          # Arquivo principal do Flask
|-- requirements.txt # Dependências do projeto

```


---
Feito com ❤️ para a disciplina de **Desenvolvimento Web de Sistemas** 🚀

