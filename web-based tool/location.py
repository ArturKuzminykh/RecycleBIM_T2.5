
import sys
import ifcopenshell
import ifcopenshell.util
import ifcopenshell.util.element
import ifcopenshell.util.selector
import json

import ifcopenshell.util.pset

model = str(sys.argv[1])

ifc = ifcopenshell.open('uploads/'+str(model))


site = ifc.by_type("IfcSite")
lat = site[0].RefLatitude
long = site[0].RefLongitude

def degr_to_dec(position):
    value = [i for i in position ]
    if value[3] < 0:
        value[3] = int(str(value[3])[:4])/1000
    else:
        value[3] = int(str(value[3])[:3])/1000
    value[1] = value[1]/60
    value[2] = (value[2]+value[3])/3600
    value = value[:-1]
    return(sum(value))

if lat != None and long != None:
    latitude = str(degr_to_dec(lat))
    longitude = str(degr_to_dec(long))
else:
    latitude = "0"
    longitude = "0"
coordinates = []
coordinates.append(latitude)
coordinates.append(longitude)

print(json.dumps(coordinates))