import json
from datetime import datetime
from langchain_community.callbacks import get_openai_callback
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sqlalchemy import text
from utils.helper import model, engine, translate_text
from utils.chat_history_helper import set_chat_history
from prompts.sql_qa_prompt import sql_template, nlp_prompt
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from prompts.sql_qa_prompt import nlp_prompt
from utils.logger import logger
from sqlalchemy import text
from utils.helper import translate

query_prompt = ChatPromptTemplate.from_template(sql_template)
nlp_prompt = ChatPromptTemplate.from_messages([("system", nlp_prompt)])

query_chain = (
    query_prompt
    | model
    | StrOutputParser()
)

def check_query_type(question):
     print("Question language: ",translate(question))
     question = translate_text(question, 'en')
     print("translated q for querying", question)
     query_string = query_chain.invoke({"question": question})
     check_type, df = process_query(query_string)
     return check_type, df

def df_to_string(df):
     df_string = "\n".join(', '.join(f"{col}: {row[col]}" for col in df.columns) for _, row in df.iterrows())
     return df_string
    
def sql_chain_call(session_id, question,df,generic_feedback=None):
        output=""
        with get_openai_callback() as cb:
                    query_time = datetime.now()
                    formatted_time = query_time.strftime('%Y-%m-%d %H:%M:%S')
                    new_chain = nlp_prompt | model | StrOutputParser()
                    for chunk in new_chain.stream({"question": question, "context" : df_to_string(df), "target_language":translate(question)}):
                          output+=chunk
                          if len(chunk) > 0:
                            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                    cost = cb.total_cost
        set_chat_history(session_id, question, output, formatted_time, cost, generic_feedback,"sql","stream") 

def process_query_output(df):
    included_columns = ['code', 'name', 'description', 'url', 'image_url']
    df_filtered = df[included_columns]
    df_filtered['description']='; '.join([value.strip() for value in (str(df_filtered['description'].values[0])).split('•')[1:4]]) + '.'
    df_filtered.fillna('', inplace=True)

    df_filtered.insert(0, 'flag', True)

    json_output = df_filtered.to_json(orient='records')
    print("json output: \n", json_output)
    return json_output

def process_query(query_string):
    logger.info(f"The generated query: {query_string}")
    query_string= text(query_string)
    df = pd.read_sql_query(query_string, engine)
    if all(column in df.columns and not df[column].empty for column in ['name', 'url']):
        return True, df
    else:
        return False,df        

def text_streamer(detected_language, msg):
    if detected_language=='en':
        print("in the english sectionn...")
        translated_text=msg
    else:
        translated_text = translate_text(msg, detected_language)
    
    logger.info("starting streaming the message.")
    words = translated_text.split(' ')
    for word in words:
        word= word+' '
        yield f'data: {json.dumps(word, ensure_ascii=False)}\n\n'