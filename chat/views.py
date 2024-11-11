import json

from flask import session

from langchain.prompts import PromptTemplate

from chat.llama3 import get_llm_response, get_llm_response_history_aware
from vectordb_code.vectorstore import retrieve_index
from postgres.views import get_nutrients_data


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
    #  along with recommended foods, foods to avoid, and specific nutrient levels
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
        1. nutrients_recommended - Recommend nutrients for the patient. Example - Protein - 20g, carbohydrate - 10g etc. It has to be list of objects with nutrient, amount, and unit.
        2. diet_plan_summary - Provide a very detailed explanation of diet plan for user in a paragraph. Also, include recommended foods, foods to avoid, and specific nutrient levels.
        3. foods_avoid - List with foods to avoid if any.

        Strictly follow the datatypes and structure of the below sample output format enclosed in <sample_output>
        {{
            "nutrients_recommended": [
            {
            "nutrient": "protein", 
            "amount": "10", 
            "unit": "g"
            }, 
            {
            "nutrient": "carbohydrate", 
            "amount": "20", 
            "unit": "g"
            }
            ],
            "diet_plan_summary": "Reduce carbohydrate intake for individuals with Type 2 Diabetes (T2D) has been shown to improve blood glucose. Emphasize consumption of non-starchy vegetables, minimal added sugars, fruits, whole grains, and dairy products.",
            "foods_avoid": ["sugar"]
        }}</sample_output>
        
        """
    )
    
    return raw_prompt


def plan_query_prompt():
    raw_prompt = PromptTemplate.from_template(
        """ 
        You are a nutrition AI assistant and your task is to answer followup questions on diet plan which you provided already. Below are the rules you need to follow:
            - The input query will contain user query regarding the diet plan provided by you in the conversation.
            - You need to answer the query based on context provided and diet plan provided by you already. If cannot find in context, answer professionally on your own. Keep in mind about user health condition.
         Question is enclosed in <input>{input}</input>
         The context is enclosed in <context>{context}</context>
         Respond directly with output.
    """
    )
    return raw_prompt


def get_foods_to_avoid(data):
    try:
        foods_avoid = data["foods_avoid"]
        is_list = isinstance(foods_avoid, list) and all(isinstance(item, str) for item in foods_avoid)
        if not is_list:
            raise TypeError
    except:
        return []
    

def get_food_recommended(data):
    try:
        nutrients_recommended = data["nutrients_recommended"]
        # for key, value in nutrients_recommended:
        nutrients_list = [item['nutrient'] for item in nutrients_recommended]
        food = get_nutrients_data(nutrients_list)
        return ",".join(food)
    except:
        return None


def create_plan_text(resp):
    try:
        data = json.loads(resp)
        diet_plan_summary = data["diet_plan_summary"]
        foods_avoid = get_foods_to_avoid(data)
        foods = get_food_recommended(data)
        response = f"{diet_plan_summary}\n\n Foods to include: {foods}\n\n Foods to avoid: {foods_avoid}"
        return response
    except:
        return "We are facing some issues. Please try again after sometime."


def get_no_llm_response():
    return '{"nutrients_recommended": [{"nutrient": "protein", "amount": "10", "unit": "g"}, {"nutrient": "carbohydrate", "amount": "20", "unit": "g"}], "diet_plan_summary": "Reduce carbohydrate intake for individuals with Type 2 Diabetes (T2D) has been shown to improve blood glucose. Emphasize consumption of non-starchy vegetables, minimal added sugars, fruits, whole grains, and dairy products.", "foods_avoid": ["Sugar", "Starchy food"]}'


def chatbot_response(user_input, llm, option):
    # return "diet plan"
    retriever = retrieve_index(name='diet_plan')
    if option == "plan_query":
        prompt = plan_query_prompt()
        resp = get_llm_response_history_aware(raw_prompt=prompt, query=user_input, retriever=retriever, llm=llm)
        # resp = get_no_llm_response()
    else:
        # with open('disease_description.json', 'r') as f:
        #     disease_description = json.load(f)  # Load the JSON data into a Python dictionary
        # query = disease_description[user_input.lower()]
        query = "The user has a {user_input} disease. Can you suggest some diet plans for this disease?".format(user_input=user_input)
        prompt = get_diet_plan_prompt()
        llm_response = get_llm_response(raw_prompt=prompt, query=query, retriever=retriever, llm=llm)
        # llm_response = get_no_llm_response()
        resp = create_plan_text(llm_response) 
    return resp