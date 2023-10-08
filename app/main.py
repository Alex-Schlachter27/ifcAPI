from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import List
import sys

print(sys.platform)

# import ifcopenshell_linux as ifcopenshell
if sys.platform == 'win32':
    print(sys.platform)
    import ifcopenshell
elif sys.platform == 'win64':
    print(sys.platform)
    import ifcopenshell
elif sys.platform == 'linux':
    print(sys.platform)
    import ifcopenshell_linux as ifcopenshell
else:
    import ifcopenshell

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
async def validate_ifc_with_ids(files: List[UploadFile] = File(...)):
    # results = []
    for file in files:
        if file.filename.endswith('.ifc'):
            ifcFile = file
        elif file.filename.endswith('.ids'):
            idsFile = file
        else:
            raise HTTPException(status_code=400, detail="Invalid file format. Please upload an IFC file")
    
    print(idsFile.filename, ifcFile.filename)
    
    # open IFC file
    my_ifc = await openIfcFile(ifcFile)
    my_ids = await openIdsFile(idsFile)
    # print(my_ids)

    # Perform validation
    my_ids.validate(my_ifc)

    # Save report as json
    json = reporter.Json(my_ids).report()

    return json

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