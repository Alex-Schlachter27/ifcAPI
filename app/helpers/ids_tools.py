import sys
# print(sys.platform)

from ifctester import ids, reporter

async def openIdsFile(file_path):
    return ids.open(file_path)




# Functions
def validate_to_json(ifc, ids):
    # Perform validation
    ids.validate(ifc)

    # Save report as json
    json = reporter.Json(ids).report()
    return json
    