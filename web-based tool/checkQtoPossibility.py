import ifcopenshell
import ifcopenshell.util.element
import uuid
import sys
import json

def generate_guid():
    return str(uuid.uuid4())

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



# Version to check with a web-based tool:
phpinput = str(sys.argv[1])
model = ifcopenshell.open('uploads/'+str(phpinput))

# Version to check with a console:
# model = ifcopenshell.open('FILEPATH')


material_guid_dict = {}

quantifiable_elements = []
non_quantifiable_elements = []
non_quantifiable_notes = []

props_req = ["CanBeReused", "CanBeRecycled", "Density"]
if not isinstance(props_req, list):
    props_req = [props_req]

for product in model.by_type("IfcBuildingElement"):
    elem_props = ifcopenshell.util.element.get_psets(product)
    mat_alphanum_qto = get_property_value(elem_props, "MatQtoPerRefUnit")
    if len(product.IsDecomposedBy) > 0 and mat_alphanum_qto is None:
        parts = product.IsDecomposedBy[0].RelatedObjects
        if parts is not None:
            mats_of_parts = []
            part_volumes = []
            for part in parts:
                part_props = ifcopenshell.util.element.get_psets(part)
                if part.HasAssociations:
                    part_volumes.append(get_property_value(ifcopenshell.util.element.get_psets(part), "Volume"))
                    material_association = part.HasAssociations[0]
                    if material_association.is_a("IfcRelAssociatesMaterial"):
                        material = material_association.RelatingMaterial
                        matprops_values = {}
                        for matprop in props_req:
                            prop_value = "NO VALUE"
                            if material.is_a("IfcMaterial"):
                                material_props = ifcopenshell.util.element.get_psets(material)
                                prop_value = get_property_value(material_props, matprop, "NO VALUE")
                            matprops_values[matprop] = prop_value

                        element_id = product.GlobalId
                        mat_name = material.Name
                        mats_of_parts.append((element_id, mat_name, matprops_values))

            for product_id, material_name, properties in mats_of_parts:
                if material_name not in material_guid_dict:
                    material_id = generate_guid()
                    material_guid_dict[material_name] = material_id
                else:
                    material_id = material_guid_dict[material_name]

                can_be_recycled = properties['CanBeRecycled']
                density = properties['Density']
                
                if any(prop == "NO VALUE" for prop in properties.values()) or None in part_volumes:
                    non_quantifiable_elements.append(product_id)
                    note = f"Note: for the element of the class {product.is_a()} with the GUID: {product_id}, quantification is impossible. Check the IR compliance."
                    note = [note]
                    non_quantifiable_notes.append(note)
                else:
                    materials = {
                        'product_id': product_id,
                        'material_id': material_id,
                        'material_name': material_name,
                        'can_be_recycled': can_be_recycled,
                        'quantity': part_volumes[mats_of_parts.index((product_id, material_name, properties))]
                    }
                    quantifiable_elements.append(product_id)

    else:
        product_id = product.GlobalId
        can_be_recycled = get_property_value(elem_props, "CanBeRecycled")
        material_composition = get_property_value(elem_props, 'MatComposition')
        quantity_per_reference_unit = get_property_value(elem_props, 'MatQtoPerRefUnit')
        quantification_reference_unit = get_property_value(elem_props, "QtoRefUnit")

        if material_composition is not None and ";" in material_composition:
            materials = material_composition.split(";")
            quantities = quantity_per_reference_unit.split(";") if quantity_per_reference_unit else [None] * len(materials)
        else:
            materials = [material_composition]
            quantities = [quantity_per_reference_unit] if quantity_per_reference_unit else [None]

        if any(q is None for q in quantities) or can_be_recycled is None:
            non_quantifiable_elements.append(product_id)
            note = f"Note: for the element of the class {product.is_a()} with the GUID: {product_id}, quantification is impossible. Check the IR compliance."
            note = [note]
            non_quantifiable_notes.append(note)
        else:
            for material, quantity in zip(materials, quantities):
                if material is not None:
                    material_name = material.strip()
                    if material_name not in material_guid_dict:
                        material_id = generate_guid()
                        material_guid_dict[material_name] = material_id
                    else:
                        material_id = material_guid_dict[material_name]

                    if quantity is not None:
                        if quantification_reference_unit == '1m':
                            length = get_property_value(elem_props, "Length")
                            if length:
                                quantity = float(quantity) * length
                        elif quantification_reference_unit == '1m2':
                            area = get_property_value(elem_props, "Area")
                            if area:
                                quantity = float(quantity) * area
                        elif quantification_reference_unit == '1m3':
                            volume = get_property_value(elem_props, "Volume")
                            if volume:
                                quantity = float(quantity) * volume

                    if None in [quantity, can_be_recycled]:
                        non_quantifiable_elements.append(product_id)
                        note = f"Note: for the element of the class {product.is_a()} with the GUID: {product_id}, quantification is impossible. Check the IR compliance."
                        note = [note]
                        non_quantifiable_notes.append(note)
                    else:
                        material_info = {
                            "product_id": product_id,
                            "material_id": material_id,
                            "material_name": material_name,
                            "quantity": quantity,
                            "can_be_recycled": can_be_recycled
                        }
                        quantifiable_elements.append(product_id)

# print("Quantifiable Elements GUIDs:")
# print(quantifiable_elements)

# print("Non-Quantifiable Elements GlobalIds:")
# print(non_quantifiable_elements)

# print("Non-Quantifiable Notes:")
# print(non_quantifiable_notes)

# Version to check with a web-based tool:
print(json.dumps([non_quantifiable_elements, quantifiable_elements, non_quantifiable_notes]))

# print(list_of_dangerous_elems)