from fastapi import FastAPI, File, Form, Path, Query, UploadFile, HTTPException
from fastapi.responses import FileResponse
from typing import List
import sys
import os
import copy

from .helpers import file_tools, ifc_tools, ids_tools
from .endpoints import ids, prop, sim

app = FastAPI()


@app.get("/")
async def root():
    version = ifc_tools.get_ifcos_version()    
    return {"message": f"This is the ifcAPI (running on ifcopenshell {version}). Choose between te following endpoints"}

@app.post("/main/get-ifc-products/")
async def get_ifc_products(file: UploadFile = File(...)):
    if not file.filename.endswith('.ifc'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an IFC file")
    
    # print(file)
    # print(file.filename)
    # print(file.size)

    # save model locally
    temp_file_path = file_tools.save_upload_file_tmp(file)
    
    # open IFC file
    ifc_file = await ifc_tools.openIfcFile(temp_file_path)

    # Perform analysis
    product_types = ifc_tools.ifcProductTypes(ifc_file)
    
    return product_types

# ENDPOINTS
# app.mount("/", sim.app)
app.mount("/ids/", ids.app)
app.mount("/sim/", sim.app)
app.mount("/prop/", prop.app)
