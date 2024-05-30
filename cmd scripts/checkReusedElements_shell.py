import sys
import ifcopenshell
import ifcopenshell.util
import ifcopenshell.util.element
import ifcopenshell.util.selector
import ifcopenshell.geom
import json
import os
import csv
import ifcopenshell.util.pset


def get_property_value(data, property_name, default_value=None):
    property_value = None
    for key, value in data.items():
        if isinstance(value, dict):
            property_value = get_property_value(value, property_name, default_value)
            if property_value is not None:
                break
        elif key == property_name:
            property_value = value 
    return property_value if property_value is not None else default_value

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

# IFC4
bld_elems_classes = ["IfcBeam", "IfcBuildingElementProxy", "IfcChimney", "IfcColumn", "IfcCovering", "IfcCurtainWall", "IfcDoor", "IfcFooting", "IfcMember","IfcPile", "IfcPlate", "IfcRailing", "IfcRamp", "IfcRampFlight", "IfcRoof", "IfcShadingDevice", "IfcSlab",
"IfcStairFlight", "IfcWall", "IfcWindow", "IfcStair", "IfcBuildingElementPart"]

# IFC2x3
# bld_elems_classes = ["IfcBeam", "IfcColumn", "IfcCovering", "IfcCurtainWall", "IfcDoor", "IfcFooting", "IfcMember","IfcPile", "IfcPlate", "IfcRailing", "IfcRamp", "IfcRampFlight", "IfcRoof", "IfcSlab",
# "IfcStairFlight", "IfcWall", "IfcWindow", "IfcStair", "IfcBuildingElementPart"]

bld_elems = []
present_classes = []
present_elems_ids = []
lst_text =[]
for elem_class in bld_elems_classes:
    cl_elems = ifc.by_type(elem_class)
    if cl_elems:
        present_classes.append(elem_class)
        bld_elems.append(cl_elems)


list_of_reused_elems = []
list_of_other_elems = []


for i in range(len(bld_elems)):
    lst_text_cl =[]
    for elem in bld_elems[i]:
        present_elems_ids.append(elem.GlobalId)
        elem_props = ifcopenshell.util.element.get_psets(elem)
        can_be_reused = get_property_value(elem_props, "CanBeReused")
        if can_be_reused is not None and (can_be_reused is True or str(can_be_reused).lower() in ["true", "yes"]):
            list_of_reused_elems.append(elem.GlobalId)
            lst_text_cl.append(str(present_classes[i]) + " - Element can be reused. GUID: " + str(elem.GlobalId) + ". Ensure correct definition.")
        else:
            list_of_other_elems.append(elem.GlobalId)

    else:
        list_of_other_elems.append(elem.GlobalId)     
    if len(lst_text_cl) != 0:
        lst_text.append(lst_text_cl)

# Define output file paths
txt_file_path = os.path.join(output_directory, 'checkReusedElements_output.txt')
csv_file_path = os.path.join(output_directory, 'checkReusedElements_output.csv')

# Write text output
with open(txt_file_path, 'w') as txt_file:
    for item in lst_text:
        txt_file.write('\n'.join(item) + '\n\n')

# Write CSV output
with open(csv_file_path, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Element GUID", "Element Class"])
    for guid in list_of_reused_elems:
        csv_writer.writerow([guid, ifc.by_guid(guid).is_a()])
