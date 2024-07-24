from fastapi import UploadFile
import os
import shutil
from sqlalchemy import create_engine, text
from dotenv import dotenv_values

config = dotenv_values(".env")
mysql_connector=config['MYSQL_CONNECTOR']

# Ensure the directories exist
os.makedirs('./data/installation_manual', exist_ok=True)
os.makedirs('./data/maintenance_manual', exist_ok=True)

async def save_file(file: UploadFile, folder: str) -> str:
    file_location = f"{folder}/{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    return file_location

def set_manual_data(installation_file_path: str, maintenance_file_path: str, code: str, name: str, yt_link: str):
    
    DATABASE_URL = mysql_connector
    engine = create_engine(DATABASE_URL)
    
    insert_stmt = text(
        "INSERT INTO brnicag_wordpress.cb_manuals (code, name_description, installation_file, maintenance_file, yt_link) "
        "VALUES (:code, :name, :installation_file, :maintenance_file, :yt_link)"
    )
    
    # Execute the insert statement with parameters
    with engine.connect() as connection:
        connection.execute(insert_stmt, {
            "code": code,
            "name": name,
            "installation_file": installation_file_path,
            "maintenance_file": maintenance_file_path,
            "yt_link": yt_link
        })