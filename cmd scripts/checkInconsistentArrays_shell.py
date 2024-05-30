import sys
import ifcopenshell
from ifcopenshell.util import element
import os
import csv

# Check if the script is being run with an argument
if len(sys.argv) != 2:
    print("Usage: python script.py <IFC_FILE_PATH>")
    sys.exit(1)

# Get the IFC file path from the command-line argument
ifc_file_path = sys.argv[1]

# Open the IFC file
ifc = ifcopenshell.open(ifc_file_path)

# Get the directory of the input IFC file to save the output files there
output_directory = os.path.dirname(ifc_file_path)

bld_elems_classes = [
    "IfcBeam", "IfcBuildingElementProxy", "IfcChimney", "IfcColumn", "IfcCovering",
    "IfcCurtainWall", "IfcDoor", "IfcFooting", "IfcMember", "IfcPile", "IfcPlate",
    "IfcRailing", "IfcRamp", "IfcRampFlight", "IfcRoof", "IfcShadingDevice", "IfcSlab",
    "IfcStairFlight", "IfcWall", "IfcWindow", "IfcStair", "IfcBuildingElementPart"
]

present_classes = []
bld_elems = []
for elem_class in bld_elems_classes:
    cl_elems = ifc.by_type(elem_class)
    if cl_elems:
        present_classes.append(elem_class)
        bld_elems.append(cl_elems)

inconsistent_elements = []
lst_text = []
inconsistent_elements_guids = []
present_elems_ids = []

for elems, cls in zip(bld_elems, present_classes):
    lst_text_cl = []
    for elem in elems:
        present_elems_ids.append(elem.GlobalId)
        pset_recycle = element.get_psets(elem).get("CDWMgmt_Pset")
        if pset_recycle:
            pr1 = pset_recycle.get("MatQtoPerRefUnit", "").split(";")
            pr2 = pset_recycle.get("MatComposition", "").split(";")
            pr3 = pset_recycle.get("WasteCode", "").split(";")
            pr4 = pset_recycle.get("CanBeRecycled", "").split(";")

            lengths_pr = {len(pr1), len(pr2), len(pr3), len(pr4)}
            if len(lengths_pr) != 1 and sum(len(pr) for pr in [pr1, pr2, pr3, pr4]) >= 4:
                inconsistent_elements.append((elem.GlobalId, cls))
                inconsistent_elements_guids.append(elem.GlobalId)
                lst_text_cl.append(
                    f"{cls} - inconsistency in array properties. GUID: {elem.GlobalId}. "
                    f"Check values: {' | '.join([str(pr1), str(pr2), str(pr3), str(pr4)])}"
                )
    if lst_text_cl:
        lst_text.append(lst_text_cl)

# Define output file paths
txt_file_path = os.path.join(output_directory, 'checkInconsistentArrays_output.txt')
csv_file_path = os.path.join(output_directory, 'checkInconsistentArrays_output.csv')

# Write text output
with open(txt_file_path, 'w') as txt_file:
    for item in lst_text:
        txt_file.write('\n'.join(item) + '\n\n')

# Write CSV output
with open(csv_file_path, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Element GUID", "Element Class"])
    for guid, cls in inconsistent_elements:
        csv_writer.writerow([guid, cls])
