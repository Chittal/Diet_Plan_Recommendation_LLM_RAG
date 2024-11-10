import json
from flask import session

from langchain_community.llms import Ollama

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def initialize_llm():
    llm = Ollama(model="llama3.1:8b")
    return llm

def get_llm_response_history_aware(raw_prompt, query, retriever, llm):
    retriever_prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            (
                "human",
                "Given the above conversation, generation a search query to lookup in order to get information relevant to the conversation",
            ),
        ]
    )
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
    # print(query, "query")
    # print(retrieval_chain, "retrieval chain")

    # result = chain.invoke({"input": query})
    result = retrieval_chain.invoke({"input": query})
    # print("=============================================")
    # print(result["answer"])
    # print(result["context"])
    session['chat_history'].append({"role": "human", "content": query})
    session['chat_history'].append({"role": "ai", "content": result["answer"]})

    sources = []
    # for doc in result["context"]:
    #     sources.append(
    #         {"source": doc.metadata["source"], "page_content": doc.page_content}
    #     )

    response_answer = {"answer": result["answer"], "sources": sources}
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
    # print(result)
    print("=============================================")
    print('ANSWER: ',result["answer"])
    # print(result["context"])
    session['chat_history'].append({"role": "human", "content": query})
    session['chat_history'].append({"role": "ai", "content": result["answer"]})

    sources = []
    # for doc in result["context"]:
    #     sources.append(
    #         {"source": doc.metadata["source"], "page_content": doc.page_content}
    #     )

    response_answer = {"answer": result["answer"], "sources": sources}
    return response_answer["answer"]