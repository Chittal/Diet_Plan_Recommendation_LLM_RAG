import os

from flask import Flask, render_template, request, jsonify, session, g
from chat.views import chatbot_response
from vectordb_code.vectorstore import create_collection
from vectordb_code.views import find_disease
from langchain_community.llms import Ollama

from dotenv import load_dotenv
import chromadb
# from huggingface_hub import login



# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# chat_history = []
app.secret_key = os.getenv('SECRET_KEY')
llm = Ollama(model="llama3.1:8b")

# Accessing environment variables
# app.config['HUGGING_FACE_API_TOKEN'] = os.getenv('HUGGING_FACE_API_TOKEN')
# login(token=os.getenv('HUGGING_FACE_API_TOKEN'))

@app.before_request
def before_request():
    print(session, "session============")
    if 'chat_history' not in session:
        print("here")
        session['chat_history'] = []
        session.modified = True
    # if 'current_state' not in session:
    #     session['current_state'] = 'start'  # Initial state
    # g.chat_history = chat_history


@app.route('/')
def home():
    chat_history = []
    session["chat_history"] = chat_history
    print("g updated", session["chat_history"])
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    print("Chat history=====>", session["chat_history"])
    option = request.form.get('option')
    if option == 'plan_query':
        user_input = request.form['message']
        response = chatbot_response(user_input, llm, option)
    else:
        # age = request.form.get('age')
        # weight = request.form.get('weight')
        # height = request.form.get('height')
        
        condition = request.form.get('condition')
        if option == 'disease':
            disease = condition
        else:
            # disease = find_disease(age, height, weight, condition)
            disease = find_disease(condition)
        print(disease, "diseaase")
        # session['current_state'] = 'question'
        response = chatbot_response(disease, llm, option)
        # print(response)
    # if session['current_state'] == 'start':
    # else:
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)