from chat.llama3 import get_llm_response
from flask import session

def chatbot_response(user_input, llm):
    return get_llm_response(user_input, llm)
    # # Manage state based responses
    # state = session['current_state']
    # print(state)
    # if state == 'disease':
    #     age, height, weight, disease = user_input.split(',')
    #     # Here you would add logic to generate the diet plan based on the disease
    #     session['current_state'] = 'questions'
    #     return f"[Diet Plans for {disease}] Do you have any questions about this diet plan?"

    # elif state == 'symptoms':
    #     age, height, weight, symptoms = user_input.split(',')
    #     # Here you would add logic to generate the diet plan based on symptoms
    #     session['current_state'] = 'questions'
    #     return f"[Diet Plans for symptoms: {symptoms}] Do you have any questions about this diet plan?"

    # elif state == 'questions':
    #     if user_input.lower() == 'yes':
    #         session['current_state'] = 'ask_query'
    #         return "Please enter your query."
    #     elif user_input.lower() == 'no':
    #         session['current_state'] = 'start'
    #         return "Do you want to create another diet plan?"

    # elif state == 'ask_query':
    #     # Logic to handle user queries could go here
    #     return "Your query has been received. Thank you!"

    # return "I'm not sure how to respond to that."