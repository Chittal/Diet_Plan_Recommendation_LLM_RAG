import os

from flask import Flask, render_template, request, jsonify, session
from llama2_chat import initialize_llm, get_llm_response

from dotenv import load_dotenv
from huggingface_hub import login

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Accessing environment variables
app.config['HUGGING_FACE_API_TOKEN'] = os.getenv('HUGGING_FACE_API_TOKEN')
login(token=os.getenv('HUGGING_FACE_API_TOKEN'))

session['llm'] = initialize_llm()

# A simple function to generate responses
def chatbot_response(user_input):
    # # You can customize this function to be more intelligent
    # if 'hello' in user_input.lower():
    #     return "Hello! How can I help you today?"
    # elif 'bye' in user_input.lower():
    #     return "Goodbye! Have a nice day!"
    # else:
    #     return "I'm not sure how to respond to that."
    return get_llm_response(query=user_input, llm=llm)

# Home route to render the chatbot interface
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle user input and generate a chatbot response
@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.form['message']
    response = chatbot_response(user_input)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
