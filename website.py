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
    # Call your Python function here and pass in the text
    summary, answers = GPTfromWebsite(text)
    send_file
    return render_template('index.html', summary=summary, answers=answers)

def GPTfromWebsite(text):
    # Add your Python code here
    openai.api_key = config("APIKEY")
    return answer_questions.queryGPT(text)

@app.route('/logo')
def logo():
    return send_file('Images/ETL_logo.png', mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
