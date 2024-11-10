from vectordb_code.vectorstore import query_sentence_transormer_collection

def find_disease(symptoms):
    # age, height, weight, 
    # query = "My age is {age}, height is {height}, and weight is {weight}. I have {symptoms}. What disease might I have?".format(age=age, height=height, weight=weight, symptoms=symptoms)
    query = "I have {symptoms}. What disease might I have?".format(symptoms=symptoms)
    print(query)
    # query = "My age is 66years, height is 5.7ft and weight is 120 pounds. I have vomiting and loss of appetite. Suggest some diet plans."
    response = query_sentence_transormer_collection("disease", query, n_results=1)
    print(response)
    disease = response[0][0]['category']
    return disease
