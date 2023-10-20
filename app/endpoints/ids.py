from fastapi import FastAPI, File, Form, Path, Query, UploadFile, HTTPException
from fastapi.responses import FileResponse
from typing import List
import sys
import os
import copy

from ..helpers import file_tools, ifc_tools, ids_tools

app = FastAPI()

@app.get("/")
async def ids():
    return {"message": f"IDS endpoint works"}

@app.post("/validate/")
async def validate_ifc_with_ids(
        ifc: UploadFile = File(...),
        ids: UploadFile = File(...)
    ):
    if not ifc.filename.endswith('.ifc'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an IFC file")
    if not ids.filename.endswith('.ids'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an IDS file")

    print("IDS Validation started")

    # save files locally
    temp_ifc_path = file_tools.save_upload_file_tmp(ifc)
    temp_ids_path = file_tools.save_upload_file_tmp(ids)
    
    # open files
    my_ifc = await ifc_tools.openIfcFile(temp_ifc_path)
    my_ids = await ids_tools.openIdsFile(temp_ids_path)
    # print(my_ids)

    json_report = ids_tools.validate_to_json(my_ifc, my_ids)

    return json_report

