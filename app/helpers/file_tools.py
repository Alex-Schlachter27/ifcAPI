from pathlib import Path
import shutil
from tempfile import NamedTemporaryFile
from fastapi import UploadFile

def save_upload_file_tmp(upload_file: UploadFile) -> Path:
    try:
        suffix = Path(upload_file.filename).suffix
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(upload_file.file, tmp)
            tmp_path = Path(tmp.name)
    finally:
        upload_file.file.close()
    return tmp_path

### UTIL ###

# async def openIfcFile(file):
#     # Read file
#     file_content = await file.read()

#     # Save file locally with to temp folder
#     # Save the file
#     # temp_file_path = f"temp/{file.filename}"
#     # with open(temp_file_path, "wb") as buffer:
#     #         # bytes = await file.read()
#     #         # print(bytes)
    
#     with open(file.filename, "wb") as buffer:
#         buffer.write(file_content)

#     # Open ifc file
#     ifc_file = ifcopenshell.open(file.filename)

#     return ifc_file

# async def openIdsFile(file):
#     # Read file
#     file_content = await file.read()
#     # print(file_content)

#     # Save file locally with "file.filename"
#     with open(file.filename, "wb") as buffer:
#         buffer.write(file_content)

#     # Open ifc file
#     ids_file = ids.open(file.filename)

#     return ids_file