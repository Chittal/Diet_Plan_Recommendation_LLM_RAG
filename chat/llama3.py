from flask import session

from langchain_community.llms import Ollama

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever

from langchain.prompts import PromptTemplate

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from vectordb_code.vectorstore import get_vector_store_retriever


def initialize_llm():
    print('here')
    llm = Ollama(model="llama3.1:8b")
    return llm

def get_llm_response(query, llm):
    raw_prompt = PromptTemplate.from_template(
        """ 
        <s>[INST] You are a nutrition AI assistant and your task is to suggest only diet plans. Below are the rules you need to follow:
            - The input query will contain user disease explained in a paragraph.
            - Consider disease and suggest diet plans to user using the context provided.
            NO PREAMBLE. [/INST] </s>
        [INST] {input}
            Context: {context}
            Answer:
        [/INST]
    """
    )
    retriever = get_vector_store_retriever(name='diet_plan')
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

    # result = chain.invoke({"input": query})
    result = retrieval_chain.invoke({"input": query})
    print(result["answer"])
    session['chat_history'].append({"role": "human", "content": query})
    session['chat_history'].append({"role": "ai", "content": result["answer"]})

    sources = []
    for doc in result["context"]:
        sources.append(
            {"source": doc.metadata["source"], "page_content": doc.page_content}
        )

    response_answer = {"answer": result["answer"], "sources": sources}
    return response_answer["answer"]
