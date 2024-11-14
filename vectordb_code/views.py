from vectordb_code.vectorstore import query_sentence_transormer_collection

def find_disease(symptoms):
    query = "I have {symptoms}. What disease might I have?".format(symptoms=symptoms)
    print(query)
    response = query_sentence_transormer_collection("disease", query, n_results=1)
    print(response)
    disease = response[0][0]['category']
    return disease
