from flask import Flask, render_template, request
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
    # Call your Python function here and pass in the text
    summary, answers = GPTfromWebsite(text)
    return render_template('index.html', summary=summary, answers=answers)

def GPTfromWebsite(text):
    # Add your Python code here
    openai.api_key = config("APIKEY")
    return answer_questions.queryGPT(text)

if __name__ == '__main__':
    app.run(debug=True)
