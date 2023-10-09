from fastapi import FastAPI, File, Form, Path, Query, UploadFile, HTTPException
from fastapi.responses import FileResponse
from typing import List
import sys
import copy

print(sys.platform)

# import ifcopenshell_linux as ifcopenshell
if sys.platform == 'win32':
    print(sys.platform)
    import ifcopenshell
    import ifcopenshell.api
elif sys.platform == 'win64':
    print(sys.platform)
    import ifcopenshell
elif sys.platform == 'linux':
    print(sys.platform)
    import ifcopenshell
    #import ifcopenshell_linux as ifcopenshell

from ifctester import ids, reporter

app = FastAPI()


@app.get("/")
async def root():
    version = ifcopenshell.version    
    return {"message": f"This is the ifcAPI (running on ifcopenshell {version}). Choose between te following endpoints"}

@app.post("/main/get-ifc-products/")
async def get_ifc_products(file: UploadFile = File(...)):
    # results = []
    if not file.filename.endswith('.ifc'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an IFC file")
    
    # print(file)
    # print(file.filename)
    # print(file.size)
    
    # open IFC file
    ifc_file = await openIfcFile(file)

    # Perform analysis
    product_types = ifcProductTypes(ifc_file)
    
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
    
    # open IFC file
    my_ifc = await openIfcFile(ifc)
    my_ids = await openIdsFile(ids)
    # print(my_ids)

    # Perform validation
    my_ids.validate(my_ifc)

    # Save report as json
    json = reporter.Json(my_ids).report()

    return json



@app.post("/prop/{global_id}/get-properties/")
async def get_ifc_products(global_id, file: UploadFile = File(...)):

    if not file.filename.endswith('.ifc'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an IFC file")
    
    # open IFC file
    model = await openIfcFile(file)
    element = model.by_guid(global_id)

    # Get psets and properties from all psets
    psets = []
    # for definition in product.IsDefinedBy:
    #     if definition.is_a('IfcRelDefinesByProperties'):
    #         property_set = definition.RelatingPropertyDefinition
    #         psets.append(property_set)
    # for pset in psets:
    #     pset.HasProperties # Not working --> pset is IFC-line (but working in Jupyter!)
    #     print(pset)
    psets = ifcopenshell.util.element.get_psets(element)

    return psets


@app.post("/prop/{global_id}/add-property/")
async def get_ifc_products(
        global_id = Path(...), 
        property_set: str = Form(...),
        property_name: str = Form(...),
        property_value: str = Form(...),        
        file: UploadFile = File(...),
        download: bool = Query(False),
    ):

    if not file.filename.endswith('.ifc'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an IFC file")
    
    # open IFC file
    model = await openIfcFile(file)

    owner_history = model.by_type("IfcOwnerHistory")[0]
    element = model.by_guid(global_id)

    # Get pset
    pset = ifcopenshell.util.element.get_pset(element, property_set)

    # Add property
    props = {property_name: property_value}
    props_copied = copy.deepcopy(props)
    ifcopenshell.api.run("pset.edit_pset", model, pset=model.by_id(pset["id"]), properties=props)
    # ifcopenshell.api.run("pset.edit_pset", ifc, pset=ifc.by_id(psets["Pset_Name"]["id"]), properties={"foo": "changed"})

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
    
    # open IFC file
    model = await openIfcFile(file)

    owner_history = model.by_type("IfcOwnerHistory")[0]
    element = model.by_guid(global_id)

    # Get pset
    pset = ifcopenshell.util.element.get_pset(element, property_set)
    # print(pset)

    # Add property
    props = {property_name: property_value}
    ifcopenshell.api.run("pset.edit_pset", model, pset=model.by_id(pset["id"]), properties=props)
    # ifcopenshell.api.run("pset.edit_pset", ifc, pset=ifc.by_id(psets["Pset_Name"]["id"]), properties={"foo": "changed"})

    # Update temp model
    model.write(r"{}".format(file.filename))

    # Return text
    message = f"Added the following properties to the pset {property_set}"
    out = {"Result": {
        "Message": message,
        "properties": props
    }}
    return out

@app.post("/prop/{global_id}/update-property/")
async def get_ifc_products(
        global_id, 
        file: UploadFile = File(...),
        property_id: str = Form(...),
        value: str = Form(...),
    ):

    if not file.filename.endswith('.ifc'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an IFC file")
    
    # open IFC file
    model = await openIfcFile(file)

    owner_history = model.by_type("IfcOwnerHistory")[0]
    element = model.by_guid(global_id)

    # Get psets and properties from all psets
    psets = ifcopenshell.util.element.get_psets(element)

    return psets

### UTIL ###

async def openIfcFile(file):
    # Read file
    file_content = await file.read()

    # Save file locally with to temp folder
    # Save the file
    # temp_file_path = f"temp/{file.filename}"
    # with open(temp_file_path, "wb") as buffer:
    #         # bytes = await file.read()
    #         # print(bytes)
    
    with open(file.filename, "wb") as buffer:
        buffer.write(file_content)

    # Open ifc file
    ifc_file = ifcopenshell.open(file.filename)

    return ifc_file

async def openIdsFile(file):
    # Read file
    file_content = await file.read()
    # print(file_content)

    # Save file locally with "file.filename"
    with open(file.filename, "wb") as buffer:
        buffer.write(file_content)

    # Open ifc file
    ids_file = ids.open(file.filename)

    return ids_file

def ifcProductTypes(ifcFile):
    return sorted({product.is_a() for product in ifcFile.by_type('IfcProduct')})