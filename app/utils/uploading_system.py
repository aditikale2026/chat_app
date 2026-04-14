import os
import shutil
from fastapi import UploadFile, HTTPException

UPLOAD_FOLDER = "/home/my/Desktop/Chatapp/data"

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".md",
    ".docx",
    ".csv",
}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def save_uploaded_file(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"'{ext}' is not supported. "
                f"Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )
        )

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buf:
        shutil.copyfileobj(file.file, buf)

    return file.filename