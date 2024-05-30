import sys
import ifcopenshell
import ifcopenshell.util
import ifcopenshell.util.element
import ifcopenshell.util.selector
import ifcopenshell.geom
import json

import ifcopenshell.util.pset

# Version to check with a web-based tool:
phpinput = str(sys.argv[1])
ifc = ifcopenshell.open('uploads/'+str(phpinput))

# Version to check with a console:
# ifc = ifcopenshell.open('FILEPATH')

# IFC4
# bld_elems_classes = ["IfcBeam", "IfcBuildingElementProxy", "IfcChimney", "IfcColumn", "IfcCovering", "IfcCurtainWall", "IfcDoor", "IfcFooting", "IfcMember","IfcPile", "IfcPlate", "IfcRailing", "IfcRamp", "IfcRampFlight", "IfcRoof", "IfcShadingDevice", "IfcSlab",
# "IfcStairFlight", "IfcWall", "IfcWindow", "IfcStair", "IfcBuildingElementPart"]

# IFC2x3
bld_elems_classes = ["IfcBeam", "IfcColumn", "IfcCovering", "IfcCurtainWall", "IfcDoor", "IfcFooting", "IfcMember","IfcPile", "IfcPlate", "IfcRailing", "IfcRamp", "IfcRampFlight", "IfcRoof", "IfcSlab",
"IfcStairFlight", "IfcWall", "IfcWindow", "IfcStair", "IfcBuildingElementPart"]

bld_elems = []
present_classes = []
present_elems_ids = []
lst_text =[]
for elem_class in bld_elems_classes:
    cl_elems = ifc.by_type(elem_class)
    if cl_elems:
        present_classes.append(elem_class)
        bld_elems.append(cl_elems)

inconsistent_elements = []
for i in range(len(bld_elems)):
    lst_text_cl =[]
    for elem in bld_elems[i]:
        present_elems_ids.append(elem.GlobalId)
        pset_recycle = ifcopenshell.util.element.get_psets(elem).get("CDWMgmt_Pset")
        if pset_recycle:
            pr1 = pset_recycle.get("MatQtoPerRefUnit", "")
            pr2 = pset_recycle.get("MatComposition", "")
            pr3 = pset_recycle.get("WasteCode", "")
            pr4 = pset_recycle.get("CanBeRecycled", "")

            pr1_list = pr1.split(";")
            pr2_list = pr2.split(";")
            pr3_list = pr3.split(";")
            pr4_list = pr4.split(";")

            lengths_pr = {len(pr1_list), len(pr2_list), len(pr3_list), len(pr4_list)}
            if len(lengths_pr) != 1 and sum(len(pr) for pr in [pr1_list, pr2_list, pr3_list, pr4_list]) >= 4:
                inconsistent_elements.append(elem.GlobalId)
                lst_text_cl.append(str(present_classes[i]) + " - inconsistency in array properties. GUID: " + str(elem.GlobalId) + ". Check values: " + pr1 + " | " + pr2 + " | " + pr3 +  " | " + pr4)
    if len(lst_text_cl) != 0:
        lst_text.append(lst_text_cl)

# Version to check with a web-based tool:
print(json.dumps([inconsistent_elements, [item for item in present_elems_ids if item not in inconsistent_elements],lst_text]))

# print(lst_text)

# Version to check with a console:
# txt_file_path = 'checkInconsistentArrays_output.txt'
# with open(txt_file_path, 'w') as txt_file:
#     for item in lst_text:
#         txt_file.write('\n'.join(item) + '\n\n')

# import csv
# csv_file_path = 'inconsistent_elements_output.csv'
# with open(csv_file_path, 'w', newline='') as csv_file:
#     csv_writer = csv.writer(csv_file)
#     csv_writer.writerow(["Element GUID", "Element Class"])
#     for guid in inconsistent_elements:
#         csv_writer.writerow([guid, ifc.by_guid(guid).is_a()])
