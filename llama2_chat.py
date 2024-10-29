import torch

from llama_index.llms.huggingface import HuggingFaceLLM
from langchain.embeddings.huggingface import HuggingFaceEmbeddings

from llama_index.core.prompts.prompts import SimpleInputPrompt
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings

from llama2_vectorstore import create_or_retrieve_index



def initialize_llm():
    system_prompt = """
    You are tasks are to predict disease from user input and provide diet plans. Your goal is to answer questions as
    accurately as possible based on the instructions and context provided.
    """
    ## Default format supportable by LLama2
    query_wrapper_prompt = SimpleInputPrompt("<|USER|>{query_str}<|ASSISTANT|>{index_response}")
 
    # meta-llama/Meta-Llama-3.1-8B
    llm = HuggingFaceLLM(
        context_window=4096,
        max_new_tokens=256,
        generate_kwargs={"temperature": 0.0, "do_sample": False},
        system_prompt=system_prompt,
        query_wrapper_prompt=query_wrapper_prompt,
        tokenizer_name="meta-llama/Llama-2-7b-chat-hf",
        model_name="meta-llama/Llama-2-7b-chat-hf",
        device_map="auto",
        model_kwargs={"torch_dtype": torch.float16 , "load_in_8bit":True}
    )
    embed_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    Settings.llm = llm
    Settings.embed_model = embed_model
    Settings.node_parser = SentenceSplitter(chunk_size=1024)
    return llm

def query_index(query):
    index = create_or_retrieve_index(name='disease')
    query_engine=index.as_query_engine()
    response=query_engine.query(query)
    return response.response

def get_llm_response(query, llm):
    index_response = query_index(query)
    # Append index response to the LLM query to provide context
    llm_input = f"<|USER|>{query}<|ASSISTANT|>{index_response}"

    # Call the LLM to generate a response
    try:
        llm_response = llm.generate(llm_input)
    except Exception as e:
        return f"Error generating response: {str(e)}"

    return llm_response