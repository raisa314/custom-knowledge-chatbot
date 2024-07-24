from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from prompts.question_rephrase_prompt import regeneration_template
from utils.helper import model

regeneration_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", regeneration_template),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ]
)

contextualize_q_chain = regeneration_prompt | model|StrOutputParser()