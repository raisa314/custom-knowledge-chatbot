from dotenv import dotenv_values
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.utilities import SQLDatabase
import ast
from sqlalchemy import create_engine, text
from utils.logger import logger

config = dotenv_values(".env")

openai_api_key=config['OPENAI_API_KEY'] 
mysql_connector=config['MYSQL_CONNECTOR']

engine = create_engine(mysql_connector)
db = SQLDatabase.from_uri(mysql_connector)

def get_chat_history(session_id):
    
    query= f"SELECT user_question, bot_response FROM brnicag_wordpress.cb_history WHERE session_id='{session_id}' ORDER BY query_time DESC LIMIT 5 ;"

    df_ch = db.run(query)
    
    if not df_ch:  # If df_ch is empty
        return []

    chat_history_list = ast.literal_eval(df_ch)
    chat_history = []
    
    for user_question, bot_response in chat_history_list:
        chat_history.append(HumanMessage(content=user_question))
        chat_history.append(AIMessage(content=bot_response))
    logger.info(f"chat_history: \n {chat_history}")
    return chat_history

def set_chat_history(session_id, question, output,query_time, cost, feedback,response_source,response_type):
    query = text("""
INSERT INTO brnicag_wordpress.cb_history
(session_id, user_question, bot_response, query_time, cost, feedback, response_source, response_type)
VALUES (:session_id, :user_question, :bot_response, :query_time, :cost, :feedback, :response_source, :response_type);
""")

    data = {
        'session_id': session_id,
        'user_question': question,
        'bot_response': output,
        'query_time': query_time,
        'cost': cost,
        'feedback': feedback,
        'response_source': response_source,
        'response_type': response_type
    }
    logger.info(f"data: {data}")

    try:
       with engine.connect() as connection:
            connection.execute(query, data)
            connection.commit() #save in database
            logger.info(f"chat history query ran successfully.")
    except Exception as e:
        logger.info(f"Error during data inserting: {str(e)}")
        
        
def check_memory(question, session_id): #check for responding
    #db = SQLDatabase.from_uri(mysql_connector)
    query = f"SELECT bot_response FROM brnicag_wordpress.cb_history WHERE session_id='{session_id}' AND user_question = '{question}' LIMIT 1;"

    df_ch = db.run(query)

    if not df_ch:  # If df_ch is empty
        return []
    else:
        print("the type of df_ch", type(df_ch))
        df_ch_list = ast.literal_eval(df_ch)
        message = df_ch_list[0][0]        
        return message
    
            
# from dotenv import dotenv_values
# from langchain_core.messages import AIMessage, HumanMessage
# from langchain_community.utilities import SQLDatabase
# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.pool import QueuePool
# import logging

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Load configuration from .env
# config = dotenv_values(".env")
# openai_api_key = config['OPENAI_API_KEY'] 
# mysql_connector = config['MYSQL_CONNECTOR']

# # Create engine with connection pooling
# engine = create_engine(mysql_connector, pool_size=10, max_overflow=20,pool_timeout=30)

# # Create a session factory
# Session = sessionmaker(bind=engine)

# def get_chat_history(session_id):
#     db = SQLDatabase.from_uri(mysql_connector)
#     query = text("SELECT user_question, bot_response FROM brnicag_wordpress.cb_history WHERE session_id=:session_id ORDER BY query_time DESC LIMIT 5")
    
#     with Session() as session:
#         result = session.execute(query, {'session_id': session_id}).fetchall()
    
#     chat_history = []
#     for user_question, bot_response in result:
#         chat_history.append(HumanMessage(content=user_question))
#         chat_history.append(AIMessage(content=bot_response))
    
#     logger.info(f"chat_history: \n {chat_history}")
#     return chat_history

# def set_chat_history(session_id, question, output, query_time, cost, feedback, response_source, response_type):
#     query = text("""
#         INSERT INTO brnicag_wordpress.cb_history
#         (session_id, user_question, bot_response, query_time, cost, feedback, response_source, response_type)
#         VALUES (:session_id, :user_question, :bot_response, :query_time, :cost, :feedback, :response_source, :response_type)
#     """)

#     data = {
#         'session_id': session_id,
#         'user_question': question,
#         'bot_response': output,
#         'query_time': query_time,
#         'cost': cost,
#         'feedback': feedback,
#         'response_source': response_source,
#         'response_type': response_type
#     }
#     logger.info(f"data: {data}")

#     try:
#         with Session() as session:
#             session.execute(query, data)
#             session.commit()
#             logger.info(f"chat history query ran successfully.")
#     except Exception as e:
#         logger.error(f"Error during data inserting: {str(e)}")

# def check_memory(question, session_id):
#     db = SQLDatabase.from_uri(mysql_connector)
#     query = text("SELECT bot_response FROM brnicag_wordpress.cb_history WHERE session_id=:session_id AND user_question=:question LIMIT 1")
    
#     with Session() as session:
#         result = session.execute(query, {'session_id': session_id, 'question': question}).fetchone()
    
#     if result:
#         return result[0]
#     else:
#         return None
            