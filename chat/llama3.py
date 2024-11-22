import json
from flask import session, g

from langchain_community.llms import Ollama

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage


def initialize_llm():
    llm = Ollama(model="llama3.1:8b")
    return llm

def get_llm_response_history_aware(raw_prompt, query, retriever, llm):
    chat_history = session["chat_history"]
    retriever_prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            (
                "human", "Given the above conversation, generate a search query to lookup in order to get information relevant to the conversation",
            ),
        ]
    )
    # print("====================")
    # print(retriever_prompt.format_messages(chat_history=chat_history, input=query))
    # print("====================")
    history_aware_retriever = create_history_aware_retriever(
        llm=llm, retriever=retriever, prompt=retriever_prompt
    )

    document_chain = create_stuff_documents_chain(llm, raw_prompt)
    # chain = create_retrieval_chain(retriever, document_chain)

    retrieval_chain = create_retrieval_chain(
        # retriever,
        history_aware_retriever,
        document_chain,
    )
    # print(history_aware_retriever)
    # print("retriever prompt", retriever_prompt)
    # print(query, "query")
    # print(retrieval_chain, "retrieval chain")

    # result = chain.invoke({"input": query})
    result = retrieval_chain.invoke({"input": query, "chat_history": chat_history})
    print("=============================================")
    print('ANSWER: ',result["answer"])
    # print(result["context"])
    session['chat_history'].append({"role": "human", "content": query})
    session['chat_history'].append({"role": "ai", "content": result["answer"]})
    # g.chat_history.append(HumanMessage(content=query))
    # g.chat_history.append(AIMessage(content=result["answer"]))
    # print(session["chat_history"], "updated")
    session.modified = True

    sources = []
    for doc in result["context"]:
        sources.append(
            {"source": doc.metadata["file_name"], "page_content": doc.page_content}
        )

    response_answer = {"answer": result["answer"], "sources": sources}
    with open('response.json', 'w') as file:
        json.dump(response_answer, file, indent=4)
    return response_answer["answer"]


def get_llm_response(raw_prompt, query, retriever, llm):
    document_chain = create_stuff_documents_chain(llm, raw_prompt)

    chain = create_retrieval_chain(
        retriever,
        document_chain,
    )
    # print(query, "query")
    # print(chain, "retrieval chain")

    # result = chain.invoke({"input": query})
    result = chain.invoke({"input": query})
    print("=============================================")
    print('ANSWER: ',result["answer"])
    # print(result["context"])
    session['chat_history'].append({"role": "human", "content": query})
    session['chat_history'].append({"role": "ai", "content": result["answer"]})
    # g.chat_history.append(HumanMessage(content=query))
    # g.chat_history.append(AIMessage(content=result["answer"]))
    # print(session["chat_history"], "updated")
    # print("meta data", result)
    session.modified = True

    sources = []
    for doc in result["context"]:
        sources.append(
            {"source": doc.metadata["file_name"], "page_content": doc.page_content}
        )

    response_answer = {"answer": result["answer"], "sources": sources}
    # print("================================================")
    # print(response_answer)
    # with open('response.json', 'w') as file:
    #     json.dump(response_answer, file, indent=4)
    return response_answer["answer"]


def get_llm_response_no_context(query, llm):
    print("INPUT QUERY TO BEAUTIFY")
    print(query)

    result = llm.invoke(query)

    print("=============================================")
    print('ANSWER: ',result)

    return result