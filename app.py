import os

from flask import Flask, render_template, request, jsonify, session
from chat.views import chatbot_response
from vectordb_code.views import find_disease
from langchain_community.llms import Ollama

from dotenv import load_dotenv
# from huggingface_hub import login



# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
llm = Ollama(model="llama3.1:8b")

# Accessing environment variables
# app.config['HUGGING_FACE_API_TOKEN'] = os.getenv('HUGGING_FACE_API_TOKEN')
# login(token=os.getenv('HUGGING_FACE_API_TOKEN'))

@app.before_request
def before_request():
    if 'chat_history' not in session:
        session['chat_history'] = []
    if 'current_state' not in session:
        session['current_state'] = 'start'  # Initial state


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    if session['current_state'] == 'start':
        age = request.form.get('age')
        weight = request.form.get('weight')
        height = request.form.get('height')
        option = request.form.get('option')
        condition = request.form.get('condition')
        if option == 'disease':
            disease = condition
        else:
            disease = find_disease(age, height, weight, condition)
        print(disease, "diseaase")
        session['current_state'] = 'question'
        response = chatbot_response(disease, llm)
        print(response)
    else:
        user_input = request.form['message']
        response = chatbot_response(user_input, llm)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)