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
        <s>[INST] You are a technical assistant good at searching docuemnts. If you do not have an answer from the provided information say so. [/INST] </s>
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
    session['chat_history'].append(HumanMessage(content=query))
    session['chat_history'].append(AIMessage(content=result["answer"]))

    sources = []
    for doc in result["context"]:
        sources.append(
            {"source": doc.metadata["source"], "page_content": doc.page_content}
        )

    response_answer = {"answer": result["answer"], "sources": sources}
    return response_answer["answer"]
