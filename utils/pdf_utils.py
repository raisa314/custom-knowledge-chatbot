from typing import List
from fastapi import UploadFile
from datetime import datetime
import os
from sqlalchemy import create_engine
from models.cb import Cbkbindex as Cb
from sqlalchemy.orm import sessionmaker
import logging
from pathlib import Path
from fastapi import  HTTPException
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from utils.logger import logger
from langchain_community.document_loaders import PyPDFDirectoryLoader
from utils.helper import embedding, mysql_connector
from pathlib import Path
import os
from utils.logger import logger
from datetime import datetime

pdf_folder = "data/pdf"
timestamp_file = Path("data/last_update_timestamp.txt")
# Database connection string - update with your actual credentials
DATABASE_URL = mysql_connector
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
logger = logging.getLogger(__name__)

async def process_pdf_files(categories: List[str], files: List[UploadFile]): #Categories is for document type like company info/warranty etc.
    session = SessionLocal()
    try:
        for category, uploaded_file in zip(categories[0].split(','), files):
            safe_file_name = "".join(char for char in uploaded_file.filename if char.isalnum() or char in "._-")
            safe_file_name = safe_file_name[:-4]  # Remove extension
            file_extension = uploaded_file.filename.split('.')[-1]
            file_directory = "./data/pdf"
            os.makedirs(file_directory, exist_ok=True)
            file_location = os.path.join(file_directory, f"{safe_file_name}.{file_extension}")
            # Save the uploaded file
            with open(file_location, "wb") as out_file:
                content = await uploaded_file.read() 
                out_file.write(content)
            logger.info(f"File {safe_file_name}.{file_extension} uploaded successfully.")
            # Update database record with the file link
            existing_record = session.query(Cb).filter_by(category=category).first()
            if existing_record:
                existing_record.pdf_link = safe_file_name
                existing_record.upload_time = datetime.now()
                session.commit()
            else:
                new_record = Cb(category=category, pdf_link=safe_file_name, upload_time=datetime.now())
                session.add(new_record)
                session.commit()
        # Query all pdf_link values from the database
        pdf_links = session.query(Cb.category, Cb.pdf_link).all()
        # Create a dictionary to store pdf_links retrieved from the database
        db_pdf_links = {link.category: link.pdf_link for link in pdf_links}                
        for category, pdf_link in db_pdf_links.items():
            db_pdf_links[category] = f"{pdf_link}.pdf"
        data_pdf_dir = "./data/pdf/"
        # Delete other pdfs
        for file_name in os.listdir(data_pdf_dir):
            if file_name not in db_pdf_links.values():
                file_path = os.path.join(data_pdf_dir, file_name)
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
        pdf_to_retriever(data_pdf_dir)
        logger.info(f"PDF Folder processed successfully.")
        return {"message": f"PDF Folder processed successfully."}
    except Exception as e:
        logger.error(f"Error during data processing: {str(e)}")
        return {"message": f"Error during processing PDF Folder: {str(e)}", "status": "failed"}
    

def pdf_to_retriever(file_path: str):
    embedding_function = embedding
    persist_directory = Path(f"./data/pdf_retriver")
    logger.info(f"Loading, chunking, and indexing the contents of the PDF: {file_path}...")
    loader = PyPDFDirectoryLoader(file_path)
    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)

    logger.info(f"Persist directory '{persist_directory}' does not exist. Creating and saving to disk...")
    persist_directory.mkdir(parents=True, exist_ok=True)
    pdf_db =FAISS.from_documents(texts, embedding_function)
    pdf_db.save_local(str(persist_directory))
    logger.info("Database saved to disk and loaded successfully!")

    return pdf_db


# Load the Faiss database from disk
def load_pdf_database():
    embedding_function = embedding
    persist_directory = Path(f"./data/pdf_retriver")
    if persist_directory.exists():
        logger.info(f"Loading Uploaded PDF FAISS database from disk (Directory: {persist_directory})...")
        db = FAISS.load_local(str(persist_directory), embedding_function, allow_dangerous_deserialization=True)
        # db = FAISS.load_local(str(persist_directory), embedding_function)
        logger.info("Database loaded successfully!")
        return db
    else:
        logger.error(f"FAISS database not found for the specified file name")
        raise HTTPException(status_code=404, detail="FAISS database not found for the specified file name")    

def check_for_updates(file_name: str) -> bool:
    logger.info("inside the update checking function")
    create_embedding= False
    current_timestamp = datetime.now().timestamp()
    file_path = file_name #os.path.join(pdf_folder, file_name)  # Use os.path.join for compatibility
    file_timestamp = os.path.getmtime(file_path)

    timestamps = {}

    if timestamp_file.exists() and timestamp_file.read_text().strip():
        with open(timestamp_file, "r") as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    name, time = parts
                    timestamps[name] = float(time)

    # Determine if a new embedding needs to be created
    if file_name not in timestamps or file_timestamp > timestamps.get(file_name, 0):
        create_embedding = True
        timestamps[file_name] = current_timestamp  # Update with the current time

    # Rewrite the timestamp file with updated info
    with open(timestamp_file, "w") as f:
        for name, time in sorted(timestamps.items()):
            f.write(f"{name},{time}\n")

    return create_embedding    