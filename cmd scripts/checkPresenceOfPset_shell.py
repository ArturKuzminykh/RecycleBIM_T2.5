import math
import ifcopenshell
import ifcopenshell.util.element
import os
import sys
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

bld_elems = []
present_classes = []

elems_wo_pset_ids = []
present_elems_ids = []

lst_text = []

for i in range(len(bld_elems_classes)):  # filtering present classes and populating list of present classes
    cl_elems = ifc.by_type(bld_elems_classes[i])
    if len(cl_elems) != 0:
        present_classes.append(bld_elems_classes[i])
        bld_elems.append(cl_elems)

for i in range(len(bld_elems)):
    have_pset = 0
    donthave_pset = 0
    num_of_elem_with_parents = 0
    parent_donthave_pset = 0
    parent_have_pset = 0

    parent_elements = []
    lst_text_cl = []

    for elem in bld_elems[i]:
        pset_recycle = ifcopenshell.util.element.get_psets(elem).get("CDWMgmt_Pset")
        present_elems_ids.append(elem.GlobalId)
        if pset_recycle is None or pset_recycle == 0:
            donthave_pset += 1
            elems_wo_pset_ids.append(elem.GlobalId)
            if len(elem.Decomposes) != 0:
                pel = elem.Decomposes[0].RelatingObject
                pel_prop = ifcopenshell.util.element.get_psets(pel).get("CDWMgmt_Pset")
                if pel_prop is None or pel_prop == 0 and elem.GlobalId not in elems_wo_pset_ids:
                    elems_wo_pset_ids.append(elem.GlobalId)
        else:
            have_pset += 1

        # find if there are parent elements that hold properties
        if len(elem.Decomposes) != 0:
            parent_element = elem.Decomposes[0].RelatingObject
            num_of_elem_with_parents += 1
            if parent_element not in parent_elements:
                parent_elements.append(parent_element)
                parent_pset_recycle = ifcopenshell.util.element.get_psets(parent_element).get("CDWMgmt_Pset")
                if parent_pset_recycle is None or parent_pset_recycle == 0:
                    parent_donthave_pset += 1
                    elems_wo_pset_ids.append(elem.GlobalId)
                else:
                    parent_have_pset += 1

    ratio = math.ceil(have_pset * 100 / (have_pset + donthave_pset))

    lst_text_cl.append(f"{present_classes[i]} - {len(bld_elems[i])} element(s). CDWMgmt_Pset is present: {ratio}%")
    if len(parent_elements) != 0:
        ratio_parents = math.ceil(100 * parent_have_pset / (parent_have_pset + parent_donthave_pset))
        lst_text_cl.append(
            f"NOTE: For the class {present_classes[i]} {num_of_elem_with_parents} elements ({math.ceil(100 * num_of_elem_with_parents / len(bld_elems[i]))}% ) have parent elements, {ratio_parents}% of them have Circularity properties")
    lst_text.append(lst_text_cl)

# Define output file paths
txt_file_path = os.path.join(output_directory, 'checkPresenceOfPset_output.txt')
csv_file_path = os.path.join(output_directory, 'checkPresenceOfPset_output.csv')

# Write text output
with open(txt_file_path, 'w') as txt_file:
    for item in lst_text:
        for line in item:
            txt_file.write(line + '\n')
        txt_file.write('\n')

# Write CSV output
with open(csv_file_path, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['Element ID', 'Ifc Class'])
    for id in elems_wo_pset_ids:
        element = ifc.by_guid(id)
        element_class = element.is_a()
        csv_writer.writerow([id, element_class])
