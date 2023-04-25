from flask import Flask, render_template, request, send_file
import openai
import answer_questions
from decouple import config

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def result():
    text = request.form['text']
    summary, answers = GPTfromWebsite(text)
    return render_template('index.html', summary=summary, answers=answers, prompt=text)


def GPTfromWebsite(text):
    openai.api_key = config("APIKEY")
    return answer_questions.queryGPT(text)


@app.route('/logo')
def logo():
    return send_file('Images/ETL_logo.png', mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=True)
