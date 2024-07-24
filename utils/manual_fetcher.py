# from langchain_community.document_loaders.csv_loader import CSVLoader
# from langchain_openai import OpenAIEmbeddings
# from langchain_community.vectorstores import FAISS
# from dotenv import load_dotenv
# import os
# from langchain_openai import ChatOpenAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain.schema import StrOutputParser
# from langchain_core.runnables import RunnableParallel, RunnablePassthrough
# import pandas as pd
# import json
# import logging
# from utils.helper import model
# logging.basicConfig(filename="newfile.log",
#                     format='%(asctime)s %(message)s',
#                     filemode='w')
# # Creating an object
# logger = logging.getLogger()
 
# # Setting the threshold of logger to DEBUG
# logger.setLevel(logging.DEBUG)

# load_dotenv()
# os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
# # ## Langmith tracking
# # os.environ["LANGCHAIN_TRACING_V2"]="true"
# # os.environ["LANGCHAIN_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")


# def response_manual(input, file='./data/maintenance_manual/Nikles_Instruction_Manual_cleaned.csv'):
#     loader = CSVLoader(file_path=file, encoding='utf-8')
#     data = loader.load()
#     db = FAISS.from_documents(data, OpenAIEmbeddings(model="text-embedding-3-small"))

#     retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 1})
#     llm=ChatOpenAI(model="gpt-3.5-turbo",temperature=0.05)
    

#     template="""
#     You are an assistant for fetching urls of Installation Instructions or Maintanace Instructions of products 
#     Use the following pieces of retrieved context to answer the question. The question will contain NAME and/or CODE
#     context: {context}
#     question: {question}
    
#     Follow the following instructions:
#     - If Installation Instruction or Maintainance Instruction is 'NO', say that instruction of that product is not available.
#     - If the question does not exactly match the context, suggest that instructions for that product is not available, parhaps they are searching for the product that you got in the context.
#     - Provide Installation instructions and Mainance instructions in seperate lines if available.
#     - Never mention the word 'context' in the answer. Say 'system' instead.
#     """
#     print(retriever.invoke(input))

#     prompt = ChatPromptTemplate.from_template(template)
#     chain = (
#         RunnableParallel(
#             {"context": retriever, "question": RunnablePassthrough()}
#         )
#         | prompt
#         | llm
#         | StrOutputParser()
#     )
#     for chunk in chain.stream(input):
#         chunk_content=chunk
#         if len(chunk_content) > 0:
#             yield f"data: {json.dumps(chunk_content, ensure_ascii=False)}\n\n" 

# if __name__ == "__main__":
#     response_manual("How do I set up Toilet brush matte black")

import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain.schema import StrOutputParser
import json


def fetch_from_csv(user_input, file='./data/maintenance_manual/Nikles_Instruction_Manual_cleaned.csv'):
    df = pd.read_csv(file, encoding='utf-8')
    reponse = """
            Information not available
        """
    flag=False
    for i, row in df.iterrows():
        if row['NAME'] in user_input or row['CODE'] in user_input:
            reponse = f"""
                    NAME: {row['NAME']} 
                    CODE: {row['CODE']} 
                    installation instructions: {row['Installation Instructions']} 
                    maintanance instructions: {row['Maintenance Instructions']} """
            flag=True 
            break         
    if not flag:
        reponse = """
            Input again.
        """
    return reponse


def response_manual(user_input):
    llm=ChatOpenAI(model="gpt-3.5-turbo",temperature=0.05)

    data = fetch_from_csv(user_input)
    prompt=f"""
        You are a natural language maker. Based on the context, generate a natural language response in no more that three sentances.

        Follow these rules:
        - You have to provide every information available in the context.
        - If context says Input again, say that 'Enter the Item/Product number please.'.
        - If the context only says information not available, say that information about this product is not available.
        - If installation instructions: NO, say that installation instructions are not available.
        - If maintanance instructions: NO, say that maintanance instructions are not available.
        {data}
    """
    chain = RunnablePassthrough() | llm | StrOutputParser()

    for chunk in chain.stream(prompt):
        chunk_content=chunk
        if len(chunk_content) > 0:
            yield f"data: {json.dumps(chunk_content, ensure_ascii=False)}\n\n" 


 