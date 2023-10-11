from fastapi import FastAPI, File, Form, Path, Query, UploadFile, HTTPException
from fastapi.responses import FileResponse
from typing import List
import sys
import os
import copy

from .helpers import file_tools
from .methods import ifc_tools, ids_tools


app = FastAPI()

print("test")


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


@app.post("/ids/validate/")
async def validate_ifc_with_ids(
        ifc: UploadFile = File(...),
        ids: UploadFile = File(...)
    ):
    if not ifc.filename.endswith('.ifc'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an IFC file")
    if not ids.filename.endswith('.ids'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an IDS file")
    
    # save files locally
    temp_ifc_path = file_tools.save_upload_file_tmp(ifc)
    temp_ids_path = file_tools.save_upload_file_tmp(ids)
    
    # open files
    my_ifc = await ifc_tools.openIfcFile(temp_ifc_path)
    my_ids = await ids_tools.openIdsFile(temp_ids_path)
    # print(my_ids)

    json_report = ids_tools.validate_to_json(my_ifc, my_ids)

    return json_report



@app.post("/prop/{global_id}/get-properties/")
async def get_properties_of_element(global_id, file: UploadFile = File(...)):

    if not file.filename.endswith('.ifc'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an IFC file")
    
    # save model locally
    temp_file_path = file_tools.save_upload_file_tmp(file)

    # open IFC file
    model = await ifc_tools.openIfcFile(temp_file_path)

    # Get psets and properties from all psets
    psets = ifc_tools.getPsetsFromId(model, global_id)

    return psets


@app.post("/prop/{global_id}/add-property/")
async def add_property_of_element(
        global_id = Path(...), 
        property_set: str = Form(...),
        property_name: str = Form(...),
        property_value: str = Form(...),        
        file: UploadFile = File(...),
        download: bool = Query(False),
    ):

    if not file.filename.endswith('.ifc'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an IFC file")
    
    # save model locally
    temp_file_path = file_tools.save_upload_file_tmp(file)

    # open IFC file
    model = await ifc_tools.openIfcFile(temp_file_path)

    owner_history = model.by_type("IfcOwnerHistory")[0]

    # Get pset
    pset = ifc_tools.getPsetFromId(model, global_id, property_set)

    # Add property
    props = {property_name: property_value}
    props_copied = copy.deepcopy(props)
    
    # Update Pset
    ifc_tools.editPset(model, pset, props)

    # Update temp model
    model.write(r"{}".format(file.filename))

    # Download?
    if download == True:
        return FileResponse(file.filename)

    # Return text
    # If the property is already in the model, ifcopenshell empties the props objects (={})
    # Therefore a copy is created: props_copied
    message = f"Added the following properties to the pset {property_set}"
    out = {"Result": {
        "Message": message,
        "properties": props_copied
    }}
    return out


@app.post("/prop/{global_id}/add-properties/")
async def get_ifc_products(
        global_id = Path(...), 
        property_set: str = Form(...),
        property_name: str = Form(...),
        property_value: str = Form(...),        
        file: UploadFile = File(...),
        download: bool = False,
    ):

    if not file.filename.endswith('.ifc'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an IFC file")
    
    # save model locally
    temp_file_path = file_tools.save_upload_file_tmp(file)

    # open IFC file
    model = await ifc_tools.openIfcFile(temp_file_path)

    owner_history = model.by_type("IfcOwnerHistory")[0]

    # Get pset
    pset = ifc_tools.getPsetFromId(model, global_id, property_set)

    # Add property
    props = {property_name: property_value}
    props_copied = copy.deepcopy(props)
    
    # Update Pset
    ifc_tools.editPset(model, pset, props)

    # Update temp model
    model.write(r"{}".format(file.filename))

    # Download?
    if download == True:
        return FileResponse(file.filename)

    # Return text
    message = f"Added the following properties to the pset {property_set}"
    out = {"Result": {
        "Message": message,
        "properties": props_copied
    }}
    return out

@app.post("/prop/{global_id}/update-property/")
async def update_property_of_element(
        global_id = Path(...), 
        property_set: str = Form(...),
        property_name: str = Form(...),
        property_value: str = Form(...),        
        file: UploadFile = File(...),
        download: bool = Query(False),
    ):

    if not file.filename.endswith('.ifc'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an IFC file")
    
    # save model locally
    temp_file_path = file_tools.save_upload_file_tmp(file)

    # open IFC file
    model = await ifc_tools.openIfcFile(temp_file_path)

    owner_history = model.by_type("IfcOwnerHistory")[0]

    # Get pset
    pset = ifc_tools.getPsetFromId(model, global_id, property_set)

    # Add property
    props = {property_name: property_value}
    props_copied = copy.deepcopy(props)
    
    # Update Pset
    ifc_tools.editPset(model, pset, props)

    # Update temp model
    model.write(r"{}".format(file.filename))

    # Download?
    if download == True:
        return FileResponse(file.filename)

    # Return text
    # If the property is already in the model, ifcopenshell empties the props objects (={})
    # Therefore a copy is created: props_copied
    message = f"Added the following properties to the pset {property_set}"
    out = {"Result": {
        "Message": message,
        "properties": props_copied
    }}
    return out

