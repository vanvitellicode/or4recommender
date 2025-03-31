from owlready2 import *
from pykml import parser
from os import path

onto_path.append("/")
onto = get_ontology("ext_mara.owl").load()

kml_file = "/NORBA_itinerario1.kml"

with open(kml_file, "r") as f:
    doc = parser.parse(f)

placemarks = doc.getroot().Document.Placemark
route_name = doc.getroot().Document.name

route = onto.Itinerario(route_name)
norba = onto.search_one(iri = "*Norba")
route.isPartOf.append(norba)

for placemark in placemarks:
    # Processa ogni placemark
    name = placemark.name.text
    coordinates = placemark.LookAt.longitude.text
    name = name.replace(" ", "_").replace('"', '').replace("(","").replace(")","")
    
    poi = onto.POI(name)
    route.hasPOI.append(poi)
    
    poi.isPartOf.append(norba)
    poi.latitude.append(placemark.LookAt.latitude.text)
    poi.longitude.append(placemark.LookAt.longitude.text)
    poi.altitude.append(placemark.LookAt.altitude.text)

for i, pl in enumerate(placemarks):
    name = pl.name.text
    name = name.replace(" ", "_").replace('"', '').replace("(","").replace(")","")
    poi = onto.search_one(iri = f"*{name}")
    if i==0:
        next_poi_name = placemarks[i+1].name.text
        next_poi_name = next_poi_name.replace(" ", "_").replace('"', '').replace("(","").replace(")","")
        next_poi = onto.search_one(iri = f"*{next_poi_name}")
        poi.hasNextPOI.append(next_poi)
    elif i==len(placemarks)-1:
        prev_poi_name = placemarks[i-1].name.text
        prev_poi_name = prev_poi_name.replace(" ", "_").replace('"', '').replace("(","").replace(")","")
        prev_poi = onto.search_one(iri = f"*{prev_poi_name}")
        poi.hasPreviousPOI.append(prev_poi)
    else:
        next_poi_name = placemarks[i+1].name.text
        next_poi_name = next_poi_name.replace(" ", "_").replace('"', '').replace("(","").replace(")","")
        next_poi = onto.search_one(iri = f"*{next_poi_name}")
        poi.hasNextPOI.append(next_poi)
        prev_poi_name = placemarks[i-1].name.text
        prev_poi_name = prev_poi_name.replace(" ", "_").replace('"', '').replace("(","").replace(")","")
        prev_poi = onto.search_one(iri = f"*{prev_poi_name}")
        poi.hasPreviousPOI.append(prev_poi)

onto.save(file = "extended_mara_with_poi.owl", format = "rdfxml")