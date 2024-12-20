import warnings
warnings.filterwarnings("ignore")

import os
import chromadb

from dotenv import load_dotenv
from langchain_community.llms import Ollama
from flask import Flask, render_template, request, jsonify, session, g

from chat.views import chatbot_response, find_disease
# from vectordb_code.vectorstore import create_collection
# from vectordb_code.views import find_disease
from chat.validate_input import validate_symptoms, check_questions
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
    # print(session, "session============")
    if 'chat_history' not in session:
        print("here")
        session['chat_history'] = []
        session.modified = True


@app.route('/')
def home():
    chat_history = []
    session["chat_history"] = chat_history
    return render_template('home.html')


@app.route('/chatbot')
def chatbot():
    chat_history = []
    session["chat_history"] = chat_history
    # print("g updated", session["chat_history"])
    return render_template('chatbot.html')


@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')


@app.route('/get_disease_response', methods=['POST'])
def get_disease_response():
    try:
        option = request.form.get('option')
        condition = request.form.get('condition')
        status, disease = find_disease(condition, llm)
        print("DISEASE:", disease)
        if status != 200:
            return jsonify({"status": 400, "response": "As per our data, you don't have any health conditions to worry about. Focus on a balanced diet with fruits, vegetables, whole grains, lean proteins, and adequate hydration to maintain overall wellness."})
        return jsonify({'status': 200, 'response': disease})
    except:
        return jsonify({"status": 400, "response": "We are facing some issues. Please try again after sometime."})


@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        option = request.form.get('option')
        if option == 'plan_query':
            user_input = request.form['message']
            status, user_input = check_questions(user_input)
            if status == 200:
                response = chatbot_response(user_input, llm, option)
            else:
                return jsonify({"status": 400, "response": user_input})
        else:
            condition = request.form.get('condition')
            disease = condition
            print("DISEASE:", disease)
            response = chatbot_response(disease, llm, option)
        return jsonify({'status': 200, 'response': response})
    except:
        return jsonify({"status": 400, "response": "We are facing some issues. Please try again after sometime."})

if __name__ == '__main__':
    app.run(debug=True)