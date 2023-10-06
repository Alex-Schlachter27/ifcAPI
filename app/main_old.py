from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import List
import ifcopenshell

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
    
    print(file)
    print(file.filename)
    print(file.size)
    file_content = await file.read()
    # print(file_content[-20:]) # prints from ifc file as text
    # print(file_content[:20])

    # Save the file
    # temp_file_path = f"temp/{file.filename}"
    # with open(temp_file_path, "wb") as buffer:
    #         # bytes = await file.read()
    #         # print(bytes)
    #         buffer.write(file_content)

    with open(file.filename, "wb") as buffer:
        buffer.write(file_content)
    
    # # Read the content of the uploaded file
    # file_content = await file.read()
    # print(file_content)

    # Use ifcopenshell to analyze the content
    ifc_file = ifcopenshell.open(file.filename)

    # Perform analysis
    product_types = ifcProductTypes(ifc_file)
    # results.append(product_types)

    # results.append(f"Analysis completed for {file.filename}")
    
    return product_types


async def openIfcFile(file):
    # Read file
    file_content = await file.read()

    # Save file locally with "file.filename"
    with open(file.filename, "wb") as buffer:
        buffer.write(file_content)

    # Open ifc file
    ifc_file = ifcopenshell.open(file.filename)

    return ifc_file

def ifcProductTypes(ifcFile):
    return sorted({product.is_a() for product in ifcFile.by_type('IfcProduct')})