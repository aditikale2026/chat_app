import os
import shutil
from fastapi import UploadFile, HTTPException

UPLOAD_FOLDER = "/home/my/Desktop/Chatapp/data"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def save_uploaded_file(file: UploadFile):

    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files allowed"
        )

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file.filename