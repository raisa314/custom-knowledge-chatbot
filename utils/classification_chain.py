# from utils.helper import model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from prompts.classification_prompt import classification_template
from langchain_openai import ChatOpenAI
from dotenv import dotenv_values


config = dotenv_values(".env")
openai_api_key=config['OPENAI_API_KEY'] 
mysql_connector=config['MYSQL_CONNECTOR']


model = ChatOpenAI(
    model_name="gpt-3.5-turbo-0125",
    streaming=True,
    temperature=0.05, 
    api_key=openai_api_key
)

classification_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", classification_template),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ]
)

classification_q_chain = classification_prompt | model | StrOutputParser()