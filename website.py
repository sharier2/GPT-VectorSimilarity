from flask import Flask, render_template, request
import openai
import answer_questions
from decouple import config

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    text = request.form['text']
    # Call your Python function here and pass in the text
    summary, answers = my_python_function(text)
    return render_template('result.html', summary=summary, answers=answers)

def my_python_function(text):
    # Add your Python code here
    openai.api_key = config("APIKEY")
    return answer_questions.queryGPT(text)

if __name__ == '__main__':
    app.run(debug=True)
