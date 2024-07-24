from langchain_openai import ChatOpenAI
from dotenv import dotenv_values
from langchain_community.utilities import SQLDatabase
from langchain_openai import OpenAIEmbeddings
from langdetect import detect
from sqlalchemy import create_engine
from deep_translator import GoogleTranslator
from utils.logger import logger
import ast
from utils.classification_chain import classification_q_chain

config = dotenv_values(".env")
openai_api_key=config['OPENAI_API_KEY'] 
mysql_connector=config['MYSQL_CONNECTOR']

translator = GoogleTranslator(source='auto')
lang = config['SUPPORTED_LANG']
supported_languages = ast.literal_eval(lang)

model = ChatOpenAI(
    model_name="gpt-3.5-turbo-0125",
    streaming=True,
    temperature=0.05, 
    api_key=openai_api_key
)

db = SQLDatabase.from_uri(mysql_connector)

embedding = OpenAIEmbeddings(api_key=openai_api_key)

engine = create_engine(mysql_connector)

def translate(question):
    target_language= detect(question)
    return target_language

def translate_text(text, target_language):
    source_lang= translate(text)
    print("source_lang: ",source_lang)
    target_language = target_language.lower()
    print("target_language", target_language)
    translator = GoogleTranslator(source=source_lang, target=target_language)
    if target_language in supported_languages.values():
        logger.info("Performing the translation")
        translated_text = translator.translate(text, target= target_language)
        logger.info(f"translation completed: {translated_text}")
        return translated_text
    else:
        logger.info(f"{text}")
        return text

# def info_process(info):
#     parts = info.split('\n')
#     data = {}
#     for part in parts:
#         if part.startswith("Standalone question:"):
#             data['standalone_q'] = part[len("Standalone question: "):]
#         elif part.startswith("Classification:"):
#             data['topic'] = part[len("Classification: "):]
#     return data

def info_process(info):
    parts = info.split('\n')
    data = {}
    for part in parts:
        if part.startswith("Standalone question:"):
            data['standalone_q'] = part[len("Standalone question: "):]
            data['standalone_q'] = data['standalone_q'].replace("'", "")
            data['standalone_q'] = data['standalone_q'].replace('"', "")
    return data

def kb_process(kb_source):
    parts = kb_source.split('\n')
    data = {}
    for part in parts:
            if  part.startswith("Classification:"):
               data['topic'] = part[len("Classification: "):]
    return data

def kbclassification(question, chat_history):
    kb_source = classification_q_chain.invoke({"question": question, "chat_history": chat_history})
    kb_source= kb_process(kb_source)['topic'].lower()
    if "pdf" in kb_source:
        return "pdf"
    else:
        return "sql"


def format_docs(documents):
    return "\n\n".join(doc.page_content for doc in documents)

def dict_question(input: dict):
        return input["question"]

