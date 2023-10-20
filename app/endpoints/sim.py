from fastapi import FastAPI, File, Form, Path, Query, UploadFile, HTTPException
from fastapi.responses import FileResponse
import copy

# Imports
import ifcopenshell
import ifcopenshell.api
import pandas as pd
import os

from ..helpers import file_tools, ifc_tools

app = FastAPI()


@app.get("/")
async def sim():
    return {"message": f"Simulation endpoint works"}


@app.post("/add-schedule-params/")
async def add_schedule_information(
        ifc: UploadFile = File(...),
        schedule: UploadFile = File(...),
        schedule_sheet: str = Form(...),
        mapping_column: str = Form(...),    
        task_type_column: str = Form(...),    
        target_pset: str = Form(...),
        identity_prop: str = Form(...),   
        group_prop: str = Form(...),
        download: bool = Query(False),
    ):

    if not ifc.filename.endswith('.ifc'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an IFC file")
    if not schedule.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an Excel file")

    print("Adding schedule parameters started!")

    # save files locally
    temp_ifc_path = file_tools.save_upload_file_tmp(ifc)
    temp_schedule_path = file_tools.save_upload_file_tmp(schedule)
    
    # open files
    if os.path.exists(temp_schedule_path):
        dfSchedule = pd.ExcelFile(temp_schedule_path)
        print("Found the schedule!")
        
    else:
        print("Path {} do not exists".format(temp_schedule_path))

    # Load the model
    model = await ifc_tools.openIfcFile(temp_ifc_path)

    owner_history = model.by_type("IfcOwnerHistory")[0]

    products = model.by_type("IfcProduct") # Also furniture, voids, etc.

    # Get all rows with Mark values from schedule
    fdRows = []
    dataSheet = pd.read_excel(dfSchedule, schedule_sheet)
    for index, row in dataSheet.iterrows():
        if not pd.isna(row[mapping_column]):
            #markList = row[identity_prop].replace(" ","").split("+")
            #print(markList)
            fdRows.append(row)
            
    print(fdRows[0])

    prodMissingPset = []
    prodMissingMark = []
    prodMultipleActivities = []

    assignedDemProducts = []
    assignedConProducts = []
    notAssignedProducts = []

    for product in products:
        
        # Reset for each element
        psets = []
        propValue = ""
        groupValue = ""
        consActivityId = ""
        consActivityName = ""
        demActivityId = ""
        demActivityName = ""
        consBaselineStart = ""
        consBaselineFinish = ""
        consActualStart = ""
        consActualFinish = ""
        demBaselineStart = ""
        demBaselineFinish = ""
        demActualStart = ""
        demActualFinish = ""
        taskType4D = ""
        taskTypes4D = ""
        usedGroupId = False
        
        # Get all propertysets of element
        for definition in product.IsDefinedBy:
            if definition.is_a('IfcRelDefinesByProperties'):
                property_set = definition.RelatingPropertyDefinition
                psets.append(property_set)
                
        psetNames = [pset.Name for pset in psets]
        
        # PSet  "Identity Data"
        if not target_pset in psetNames:
            prodMissingPset.append(product)
        else:
            myPset = psets[psetNames.index(target_pset)]
            #myPset = [pset for pset in psets if pset.Name == "Identity Data"]
            #print(myPset)

            props = myPset.HasProperties
            #print(props)
            propNames = [prop.Name for prop in props]
            #print(propNames)
            if not identity_prop in propNames and not group_prop in propNames:
                prodMissingMark.append(product)
                #print(product)
            else:
                # Use group identification for elements that are grouped in simulation (e.g. temp works or technical installations)
                if group_prop in propNames:
                    groupProp = props[propNames.index(group_prop)]
                    if not groupProp.NominalValue==None:
                        groupValue = groupProp.NominalValue.wrappedValue
                        usedGroupId = True
                if identity_prop in propNames:
                    markProp = props[propNames.index(identity_prop)]
                    if not markProp.NominalValue==None:
                        propValue = markProp.NominalValue.wrappedValue
                
                #print(propValue)
                #print(groupValue)
                
                # match mark value with activity row from schedule
                constructCount = 0
                demolishCount = 0
                for row in fdRows:
                    markList = row[identity_prop].replace(" ","").split("+")
                    propValue = propValue.replace(" ","")
                    groupValue = groupValue.replace(" ","")
                    #print(markList, groupValue)
                        
                    # Check for each row if mark or group value matches the markList of the activity
                    if propValue in markList or groupValue in markList:
                        #print(propValue, "found in", row[identity_prop], "of row", row["Task_Name"])
                        taskType4D = row[task_type_column]
                        if taskType4D == "Construct":                        
                            consActivityId = row["GUID"]
                            consActivityName = row["Task_Name"]
                            consBaselineStart = row["Baseline_Start"]
                            consBaselineFinish = row["Baseline_Finish"]
                            consActualStart = row["Start_Date"]
                            consActualFinish = row["Finish_Date"]
                            constructCount+=1
                        elif taskType4D == "Demolish":                      
                            demActivityId = row["GUID"]
                            demActivityName = row["Task_Name"]
                            demBaselineStart = row["Baseline_Start"]
                            demBaselineFinish = row["Baseline_Finish"]
                            demActualStart = row["Start_Date"]
                            demActualFinish = row["Finish_Date"]
                            demolishCount+=1
                        
                if constructCount > 1 or demolishCount > 1:
                    # print(constructCount)
                    # print("Element was assigned to more than one activity. Please check the schedule.")
                    # if constructCount > 1: print("The element was assigned to", str(constructCount) + ",construction activities")
                    # if demolishCount > 1: print("The element was assigned to", str(demolishCount) + ",demolish activities")
                    prodMultipleActivities.append(product)
                    # print(product)
                
                # Not assigned elements
                if consActivityId == "" and demActivityId == "": print("propValue:", propValue, "groupValue:", groupValue, "\n", product, "\n")
                
                # if activity could be matched, add property to element in new Pset PAA_4D
                #fdPset = ifcopenshell.api.run("pset.add_pset", model, product=product, name="PAA_4D")
                #fdPset = psets[psetNames.index("PAA")]
                
                if not consActivityId == "" or not demActivityId == "":
                    # Add GUID and name of the activity
                    #ifcopenshell.api.run("pset.edit_pset", model, pset=fdPset, properties={"PAA_4D-Name": activityName, "PAA_4D": activityId})
                    if not consActivityId == "" and not demActivityId == "": taskTypes4D = "Construct + Demolish"
                    elif not consActivityId == "" : taskTypes4D = "Construct"
                    elif not demActivityId == "": taskTypes4D = "Demolish"
                    
                    props = {"PAA_ActivityTypes": taskTypes4D}
                    if not consActivityId == "": props.update({
                        "PAA_4D-Name": consActivityName, "PAA_4D": consActivityId,
                        "PAA_4D_Actual Start": str(consActualStart), "PAA_4D_Actual Finish": str(consActualFinish),
                        "PAA_4D_Baseline Start": str(consBaselineStart), "PAA_4D_Baseline Finish": str(consBaselineFinish),
                    })
                    if not demActivityId == "": props.update({
                        "PAA_4D_Demolish-Name": demActivityName, "PAA_4D_Demolish": demActivityId,
                        "PAA_4D_Actual Start Demolish": str(demActualStart), "PAA_4D_Actual Finish Demolish": str(demActualFinish),
                        "PAA_4D_Baseline Start Demolish": str(demBaselineStart), "PAA_4D_Baseline Finish Demolish": str(demBaselineFinish)
                    })
                    #print(props)
                    ifcopenshell.api.run("pset.edit_pset", model, pset=myPset, properties=props)
                    
                # Results
                if constructCount == 0 and demolishCount == 0:
                    notAssignedProducts.append(product)
                if constructCount > 0:
                    assignedConProducts.append(product)
                if demolishCount > 0:
                    assignedDemProducts.append(product)
                
    # Update temp model
    model.write(r"{}".format(temp_ifc_path))

    # Summary
    message = f"{str(len(assignedConProducts))} elements were assigned to construction activities \n"
    message += f"{str(len(assignedDemProducts))} elements were assigned to demolish activities \n"
    message += f"{str(len(notAssignedProducts))} elements were not assigned to activities \n"
    message += f"{str(len(prodMultipleActivities))} elements exist on multiple activities and were only assigned to the last one \n"
    if len(prodMissingPset) > 0:
        message += str(len(prodMissingPset)) + " elements are missing the correct PropertySet, e.g. \n"
    if len(prodMissingMark) > 0 :
        message += str(len(prodMissingMark)) + " elements are missing the property to link them to an activity, e.g. \n"
    
    summary = {"Result": {
        "Message": message,
        "multiple_activities": prodMultipleActivities,
        "not_assigned": notAssignedProducts,
        "missing_Pset": prodMissingPset,
        "missing_Prop": prodMissingMark
    }}
    print(summary)
    
    # Download?
    if download == True:
        return FileResponse(temp_ifc_path)

    
    # Return summary if not downloaded
    return summary

