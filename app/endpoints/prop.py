from fastapi import FastAPI, File, Form, Path, Query, UploadFile, HTTPException
from fastapi.responses import FileResponse
import copy

from ..helpers import file_tools, ifc_tools

app = FastAPI()

@app.get("/")
async def prop():
    return {"message": f"Property endpoint works"}

@app.post("/{global_id}/get-properties/")
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


@app.post("/{global_id}/add-property/")
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
    # model.write(r"{}".format(file.filename))
    model.write(r"{}".format(temp_file_path))

    # Download?
    if download == True:
        return FileResponse(temp_file_path)

    # Return text
    # If the property is already in the model, ifcopenshell empties the props objects (={})
    # Therefore a copy is created: props_copied
    message = f"Added the following properties to the pset {property_set}"
    out = {"Result": {
        "Message": message,
        "properties": props_copied
    }}
    return out

# TODO: How to add several properties? With JSON body?
@app.post("/{global_id}/add-properties/")
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

# Update is the same as Add (ifcopenshell.api will update a property if the property already exists)
@app.post("/{global_id}/update-property/")
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

