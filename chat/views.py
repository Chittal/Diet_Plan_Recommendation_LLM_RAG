import json

from flask import session

from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from chat.llama3 import get_llm_response, get_llm_response_history_aware, get_llm_response_no_context
from vectordb_code.vectorstore import retrieve_index_with_folder, retrieve_index
from postgres.views import get_nutrients_data


def get_diet_plan_prompt():
    raw_prompt = PromptTemplate.from_template(
        """ 
        You are a diet plan recommendation AI assistant. Question is enclosed in <input>{input}</input>
        Important: Use context only to generate your output from. The context is enclosed in <context>{context}</context>

        Output: 
        Your output should be in JSON format containg following elements with specified key.
        1. nutrients_recommended - Recommend nutrients for the patient to include in their diet in the form of a list. It should include all possible nutrients only and each nutrient should be a separate list element. Provide nutrients in singular term. Example - Protein, carbohydrate, etc. If none is found just return empty list. (List of strings)
        2. diet_plan_summary - Provide diet plan for user based on the disease provided. First line should say what disease user has and then provide diet plan. Include recommended foods, and foods to avoid. Provide everything in paragraph. (Text)
        3. foods_avoid - List with foods to avoid if any. (List of strings)

        

        Important: Respond directly with the JSON output, without any additional text or introductions. Format the output as mentioned in sample output, including "nutrients_recommended", "diet_plan_summary", and "foods_avoid".
        """
    )
    return raw_prompt


def get_disease_prompt():
    raw_prompt = PromptTemplate.from_template(
        """ 
        You are a chronic disease prediction AI assistant. Your task is to predict whether the user has one of the following conditions using context provided: 'Thyroid', 'Heart disease', 'Diabetes', or 'None', based on symptoms.
        Question is enclosed in <input>{input}</input>
        Use context only to generate your output. The context is enclosed in <context>{context}</context>

        Output:
        Respond with a single word indicating the condition: one of 'Thyroid', 'Heart', 'Diabetes', or 'None'.
        If the user does not have any of these diseases or there is no context, always respond with 'None'.
        
        Important:
        - Do not infer or assume information that is not explicitly stated in the context.
        - Respond directly with the output word, without any additional text, symbols, punctuations, explanations, or introductions.
        """
    )
    return raw_prompt


def plan_query_prompt():
    raw_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a diet plan recommendation AI assistant. Answer the questions related to healthcare, nutrition, diet plan, and food. You can only help with dietary advice. If the question is not from any of this, don't answer. "),
            ("system", "If the question is related to healthcare, nutrition, diet plan, and food industry, answer user question based on context provided. If you cannot find in context, answer professionally on your own. Keep in mind about user health condition provided. The context is enclosed in <context>{context}</context>"),
            ("system", "Provide 100 words text. Surround titles/bold text in <strong></strong> instead of **. Don't add any unrelated content, tags, or string. Respond directly with output."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ]
    )
    return raw_prompt


def beautify_text_prompt(input):
    prompt = f"""
    Your task is to enhance and refine the input provided below for clarity, style, and flow. Focus on improving readability, and ensuring it maintains a professional and polished tone. 
    - Do not change the meaning of sentences. Format the text in user understandable format.
    - Include only unique foods in the list of recommended foods and avoid repetition across categories. 
    - Surround titles/bold text in <strong></strong> instead of **. Add bold only when it is required.
    - Ensure a clean, formatted, and structured layout. Do not add any unrelated content, symbols, tags, or strings. 
    - Respond directly with the output, without any additional text, explanations, or introductions.
    Input:
    {input}
    """
    return prompt


def get_foods_to_avoid(data):
    try:
        foods_avoid = data["foods_avoid"]
        is_list = isinstance(foods_avoid, list) and all(isinstance(item, str) for item in foods_avoid)
        if not is_list:
            raise TypeError
        return foods_avoid
    except:
        return []
    

def get_food_recommended(data):
    try:
        nutrients_recommended = data["nutrients_recommended"]
        # for key, value in nutrients_recommended:
        # nutrients_list = [item['nutrient'] for item in nutrients_recommended]
        food = get_nutrients_data(nutrients_recommended)
        return ",".join(food)
    except:
        return None


def create_plan_text(disease, resp, llm):
    data = json.loads(resp)
    diet_plan_summary = data["diet_plan_summary"]
    dis_line = f"If you have {disease} disease, it is essential to consult with your doctor. Follow these diet plans to stay healthy." 
    inp = f"{disease} Disease Diet plan Recommendation\n{dis_line}\n{diet_plan_summary}\n"
    foods = get_food_recommended(data)
    if foods:
        inp += f"\n Foods to include: {foods}"
    foods_avoid = get_foods_to_avoid(data)
    if foods_avoid:
        inp += f"\n Foods to avoid: {foods_avoid}"
    txt = get_llm_response_no_context(query=beautify_text_prompt(inp), llm=llm)
    return txt


def get_no_llm_response():
    return '{"nutrients_recommended": [{"nutrient": "protein", "amount": "10", "unit": "g"}, {"nutrient": "carbohydrate", "amount": "20", "unit": "g"}], "diet_plan_summary": "Reduce carbohydrate intake for individuals with Type 2 Diabetes (T2D) has been shown to improve blood glucose. Emphasize consumption of non-starchy vegetables, minimal added sugars, fruits, whole grains, and dairy products.", "foods_avoid": ["Sugar", "Starchy food"]}'


def get_disease(llm_response):
    try:
        if llm_response in ["Thyroid", "Heart", "Diabetes"]:
            return 200, llm_response
        else:
            return 400, None
    except:
        return 400, None


def find_disease(query, llm):
    # query = "I have {symptoms}. What disease might I have?".format(symptoms=symptoms)
    retriever = retrieve_index(name='disease')
    prompt = get_disease_prompt()
    llm_response = get_llm_response(raw_prompt=prompt, query=query, retriever=retriever, llm=llm)
    status, disease = get_disease(llm_response)
    return status, disease


def chatbot_response(user_input, llm, option):
    if option == "plan_query":
        retriever = retrieve_index(name='diet_plan')
        prompt = plan_query_prompt()
        resp = get_llm_response_history_aware(raw_prompt=prompt, query=user_input, retriever=retriever, llm=llm)
        # resp = get_no_llm_response()
    else:
        retriever = retrieve_index_with_folder(name='diet_plan', folder=user_input)
        query = "The user has a {user_input} disease. Can you suggest some diet plans for this disease?".format(user_input=user_input)
        print(query)
        prompt = get_diet_plan_prompt()
        llm_response = get_llm_response(raw_prompt=prompt, query=query, retriever=retriever, llm=llm)
        # llm_response = get_no_llm_response() 
        resp = create_plan_text(user_input, llm_response, llm) 
    return resp