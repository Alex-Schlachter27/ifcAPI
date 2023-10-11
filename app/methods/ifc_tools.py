import sys
# print(sys.platform)
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

def get_ifcos_version():
    return ifcopenshell.version

async def openIfcFile(file_path):
    return ifcopenshell.open(file_path)



# Functions
def ifcProductTypes(ifc_file):
    return sorted({product.is_a() for product in ifc_file.by_type('IfcProduct')})

def getPsetsFromId(model, global_id):
    element = model.by_guid(global_id)
    psets = getPsetsUtil(element)
    return psets

def getPsetsUtil(element):
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

def getPsetFromId(model, global_id, property_set):
    element = model.by_guid(global_id)
    pset = getPsetUtil(element, property_set)
    return pset

def getPsetUtil(element, property_set):
    pset = ifcopenshell.util.element.get_pset(element, property_set)
    return pset

def editPset(model, pset, props):
    ifcopenshell.api.run("pset.edit_pset", model, pset=model.by_id(pset["id"]), properties=props)
    # ifcopenshell.api.run("pset.edit_pset", ifc, pset=ifc.by_id(psets["Pset_Name"]["id"]), properties={"foo": "changed"})
    

    