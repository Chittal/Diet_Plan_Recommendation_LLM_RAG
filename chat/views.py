import json

from flask import session

from langchain.prompts import PromptTemplate

from chat.llama3 import get_llm_response, get_llm_response_history_aware
from vectordb_code.vectorstore import retrieve_index


def get_diet_plan_prompt():
    
    # raw_prompt = PromptTemplate.from_template(
    #     """ 
    #     <s>[INST] You are a nutrition AI assistant. Analyze the user's health condition provided and suggest a personalized diet plan based on context provided. Follow these rules:

    #         Diet Plan: Provide a tailored diet plan in paragraph form, emphasizing foods and habits beneficial for the condition.
    #         Nutrient Requirements: Include a JSON object listing the key nutrients needed with quantities in grams, considering the condition's dietary guidelines.
    #         Foods to Avoid: Specify foods or ingredients to avoid in a list format.
            
    #         Sample Output:
    #         <Diet plan paragraph>
    #         Nutrients_required = {{
    #         'protein': 20g,
    #         'carbohydrate': 10g
    #         }}
    #         Avoid = ['Sugar']

    #         Sample Input:
    #         The user has a diabetes disease. Can you suggest some diet plans for this disease?

    #         NO PREAMBLE. [/INST] </s>
    #     [INST] {input}
    #         Context: {context}
    #         Answer:
    #     [/INST]
    # Your output should be professional summary for the patient in JSON format. 
    # """
    # )
    raw_prompt = PromptTemplate.from_template(
        """ 
        You are a nutrition AI assistant. Question is enclosed in <input>{input}</input>
        Use context only to generate your answer from. The context is enclosed in <context>{context}</context>
        - Respond directly with the JSON output, without any additional text or introductions.
        - Format the output as specified, including "nutrients_recommended", "diet_plan_summary", and "foods_avoid".
        Output: 
        Your output should be in JSON format containg following elements with specified key.
        1. rutrients_recommended - Recommend nutrients for the patient. Example - Protein - 20g, carbohydrate - 10g etc. 
        2. diet_plan_summary - Create a detailed professional summary for diet plan of the patient. 
        3. foods_avoid - Include foods to avoid if any.
        
        """
    )
    
    return raw_prompt


def plan_query_prompt():
    raw_prompt = PromptTemplate.from_template(
        """ 
        You are a nutrition AI assistant and your task is to answer followup questions on diet plan which you provided already. Below are the rules you need to follow:
            - The input query will contain user query regarding the diet plan provided by you.
            - You need to answer the query based on context provided and diet plan provided by you already.
         Question is enclosed in <input>{input}</input>
         The context is enclosed in <context>{context}</context>
        NO PREAMBLE
    """
    )
    return raw_prompt


def chatbot_response(user_input, llm, option):
    # return "diet plan"
    retriever = retrieve_index(name='diet_plan')
    if option == "plan_query":
        prompt = plan_query_prompt()
        resp = get_llm_response_history_aware(raw_prompt=prompt, query=user_input, retriever=retriever, llm=llm)
    else:
        # with open('disease_description.json', 'r') as f:
        #     disease_description = json.load(f)  # Load the JSON data into a Python dictionary
        # query = disease_description[user_input.lower()]
        query = "The user has a {user_input} disease. Can you suggest some diet plans for this disease?".format(user_input=user_input)
        prompt = get_diet_plan_prompt()
        resp = get_llm_response(raw_prompt=prompt, query=query, retriever=retriever, llm=llm)
        # get nutrient from resp, diet from resp, foods to avoid from resp
        diet = resp
        food_nutrients = ['Apple', 'Orange', 'Banana']
        avoid = ['Sugar']
        # foods = collect_food(nutrient)
        resp = "{diet}\nFoods to include: {foods}\nFoods to avoid: {avoid}".format(diet=diet, foods=','.join(food_nutrients), avoid=','.join(avoid))
    return resp