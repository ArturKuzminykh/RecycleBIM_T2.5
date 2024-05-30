import ifcopenshell
from ifcopenshell.util import element


# Version to check with a web-based tool:
# phpinput = str(sys.argv[1])
# ifc = ifcopenshell.open('uploads/' + str(phpinput))

# Version to check with a console:
ifc = ifcopenshell.open('D:/YandexDisk/04_Dev/UMinho_RecycleBIM/03_May 2024 Delivery/D2.6/TestIFC/17071996.ifc')

bld_elems_classes = ["IfcBeam", "IfcBuildingElementProxy", "IfcChimney", "IfcColumn", "IfcCovering", "IfcCurtainWall", "IfcDoor", "IfcFooting", "IfcMember","IfcPile", "IfcPlate", "IfcRailing", "IfcRamp", "IfcRampFlight", "IfcRoof", "IfcShadingDevice", "IfcSlab",
"IfcStairFlight", "IfcWall", "IfcWindow", "IfcStair", "IfcBuildingElementPart"]

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

# Version to check with a web-based tool:
# print(json.dumps([
#     inconsistent_elements_guids,
#     [item for item in present_elems_ids if item not in inconsistent_elements_guids],
#     lst_text
# ]))

# Version to check with a console:
import csv

txt_file_path = 'checkInconsistentArrays_output.txt'
with open(txt_file_path, 'w') as txt_file:
    for item in lst_text:
        txt_file.write('\n'.join(item) + '\n\n')

csv_file_path = 'checkInconsistentArrays_output.csv'
with open(csv_file_path, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Element GUID", "Element Class"])
    for guid, cls in inconsistent_elements:
        csv_writer.writerow([guid, cls])
