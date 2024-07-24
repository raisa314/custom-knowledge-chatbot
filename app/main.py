from typing import List
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, Form, HTTPException, status
from fastapi.responses import StreamingResponse
from models.question import Question
from utils.logger import logger
from utils.manuals_ingest import save_file, set_manual_data
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from utils.create_db import create_tables, product_data
from fastapi import UploadFile, File  
from typing import List
from utils.pdf_utils import process_pdf_files
from utils.chat_history_helper import get_chat_history,check_memory
from utils.helper import translate, info_process,kb_process,kbclassification
from utils.q_rephrase import contextualize_q_chain
from utils.pdf_qna import pdf_chain_call
from utils.chat_history_helper import set_chat_history
from utils.sql_qna import sql_chain_call, check_query_type, process_query_output, text_streamer
from utils.pdf_utils import pdf_to_retriever, check_for_updates
from utils.classify_routes import rl,rl1
from utils.manual_fetcher import response_manual

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,    
    allow_origins=origins,    
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Health Checker
@app.get("/health")
async def health():
    logger.info("Health check requested")
    return {"status": "ok"}

#initializing link to run if product data is updated...
@app.get("/initialize")
async def initialize():
    try:
        create_tables()
        logger.info("Tables are successfully created")
        filename = product_data()
        logger.info(f"Product table populated and pdf from product data are created successfully. File Name: {filename}")

        data_pdf_dir = "./data/pdf/"

        logger.info("Running data processing.")    
        if check_for_updates(filename):
            logger.info("Updates found. Creating new retriever.")
            pdf_to_retriever(data_pdf_dir)
            logger.info("New retriever created successfully")
            return {"status": "Retriever created with pdf product data."}
        else:
            logger.info("No updates found. No need to create a new retriever.")
            return {"status": "No updates found. No need to create a new retriever."}
    except Exception as e:
        logger.error(f"Error during sql data processing: {str(e)}")
        return{"status":"An error occured during data processing."}

#link to chat with the chatbot
st = "Sorry, can you ask me the question again or try with a different question please?"
hi_message = "Hi there! How can I help you? Let me know if you have any queries about Nikles or our products."
bye_message = "Goodbye! If you have any more questions in the future, feel free to reach out. Have a great day!"


@app.post("/chat")
async def pdf_qa(input_data:Question):
    question= input_data.question
    session_id = input_data.session_id
    
    check_message=rl(question).name 
    
    logger.info(f"Message Type: {check_message}")
    
    if check_message=="hi":
        logger.error(f"Hi Messgae")
        return StreamingResponse(text_streamer("en", hi_message), media_type='text/event-stream')   
    elif check_message=='bye':
        logger.error(f"Bye Message")
        return StreamingResponse(text_streamer("en", bye_message), media_type='text/event-stream')   
    
    if not question or not session_id:
        logger.warning("Invalid input. Question or session id not provided.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid input. Please provide a question")
    try:
        logger.info(f"Received question for QA: {question}, Session id: {session_id}")
        chat_history= get_chat_history(session_id)
        logger.info("Got the existing chat history")
        info= contextualize_q_chain.invoke({"question": question, "chat_history": chat_history, "target_language": translate(question)})
        new_question = info_process(info)['standalone_q']
        logger.info(f"Recieved the processed question: {new_question}")
        
        check_message=rl1(new_question).name 
        
        if check_message=="instruction_manuals":
             logger.info("Answering from instruction Mannuals")
             return StreamingResponse(response_manual(new_question), media_type='text/event-stream')
        
        #check in memory
        logger.info(f"check memory start")
        past_resp= check_memory(new_question, session_id)
        logger.info(f"check memory end")
        if past_resp:
            logger.info(f"Answering from memory: {past_resp}") 
            dl= (translate(new_question))
            print("detected language of past resp",dl)
            return StreamingResponse(text_streamer(dl, past_resp), media_type='text/event-stream')       
        
        #kb classification
        logger.info(f"classification start")
        kb= kbclassification(new_question, chat_history)
        logger.info(f"classification end")
        query_time = datetime.now()
        formatted_time = query_time.strftime('%Y-%m-%d %H:%M:%S')
        cost=0
        generic_feedback= None
        
        if "pdf" in kb:
           logger.info("Answering from pdf")
           return StreamingResponse(pdf_chain_call(session_id, new_question, chat_history), media_type="text/event-stream")
        
        else:
          # 3 types of sql call
          check_type, df = check_query_type(new_question)
          #case 1     
          if df.empty:
                  logger.info("sql case 1")
                  output="Sorry, Your query does not match any available information. Please try again with a different question."
                  set_chat_history(session_id, new_question, output, formatted_time, cost, generic_feedback,"sql","stream") 
                  logger.info("Going to the text streaming function...")
                  dl= (translate(new_question))
                  print("detected language of question", dl)
                  return StreamingResponse(text_streamer(dl, output), media_type='text/event-stream')       
          #case 2
          elif not df.empty and check_type == True:            
            logger.info("sql case 2")
            output = process_query_output(df)
            # set_chat_history(session_id, new_question, output, formatted_time, cost, generic_feedback,"sql","card") 
            return output  
          #case 3
          else:
                 logger.info("sql case 3")
                 return StreamingResponse(sql_chain_call(session_id, new_question, df), media_type="text/event-stream")
    
    except HTTPException as e: 
        logger.error(f"HTTPException during QA request: {e.detail}")
        return StreamingResponse(text_streamer("en", st), media_type='text/event-stream')
    except Exception as e:
        logger.error(f"An error occurred during QA request: {str(e)}")
        return StreamingResponse(text_streamer("en", st), media_type='text/event-stream')         
    
    # except HTTPException as e: 
    #     logger.error(f"HTTPException during QA request: {e.detail}")
    #     raise e
    # except Exception as e:
    #     logger.error(f"An error occurred during QA request: {str(e)}")
    #     raise HTTPException(status_code=500, detail="An error occurred during processing the question")

#link to prepare the pdf data, if any file updated (except the sql data based pdf)
@app.post("/data_prep/")
async def data_prep(categories: List[str], files: List[UploadFile] = File(...)):
     return await process_pdf_files(categories, files)

#link for updating the manuals (currently not in use)
@app.post("/index_update")
async def index_update(installation_file: UploadFile = File(...), 
                        maintenance_file: UploadFile = File(...),
                        code: str = Form(...),
                        name: str = Form(...),
                        yt_link: str = Form(...)):
    installation_file_path = await save_file(installation_file, './data/installation_manual')
    maintenance_file_path = await save_file(maintenance_file, './data/maintenance_manual')

    set_manual_data(installation_file_path, maintenance_file_path, code, name, yt_link)

    return JSONResponse(status_code=200, content={"message": "Data successfully updated"})



