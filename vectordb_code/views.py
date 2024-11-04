from vectordb_code.vectorstore import query_sentence_transormer_collection

def find_disease(age, height, weight, symptoms):
    query = "My age is {age}, height is {height}, weight is {weight} and symptoms are {symptoms}. What disease might I have?".format(age=age, height=height, weight=weight, symptoms=symptoms)
    response = query_sentence_transormer_collection("disease", query, n_results=5)
    print(response)
    disease = response[0][0]['category']
    return disease
