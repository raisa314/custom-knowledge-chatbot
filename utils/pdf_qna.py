import json
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableSerializable
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from dotenv import dotenv_values
from langchain_openai import OpenAIEmbeddings
from pathlib import Path
from datetime import datetime
from langchain_community.callbacks import get_openai_callback
from utils.helper import model, embedding, translate, format_docs, dict_question
from utils.chat_history_helper import set_chat_history
from prompts.pdf_qa_prompt import qa_system_prompt
from utils.pdf_utils import load_pdf_database
config = dotenv_values(".env")
openai_api_key=config['OPENAI_API_KEY'] 

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ]
)

pdf_db=load_pdf_database()

retriever = pdf_db.as_retriever(search_type="similarity_score_threshold", 
                            search_kwargs={"score_threshold": 0.5})

rag_chain = (
            RunnablePassthrough.assign(context=dict_question | retriever | format_docs)
        | qa_prompt
        | model
    )

def pdf_chain_call(session_id, question, chat_history):
      generic_feedback= None
      output=""
      print(openai_api_key[:5])
      
      with get_openai_callback() as cb:
            query_time = datetime.now()
            formatted_time = query_time.strftime('%Y-%m-%d %H:%M:%S')
            for chunk in rag_chain.stream({"question": question, "chat_history": chat_history, "target_language": translate(question)}):
                  output+=chunk.content
                  chunk_content=chunk.content
                  if len(chunk_content) > 0:
                        yield f"data: {json.dumps(chunk_content, ensure_ascii=False)}\n\n"
            cost = cb.total_cost 
      set_chat_history(session_id, question, output, formatted_time, cost, generic_feedback,"pdf","stream")