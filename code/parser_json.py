import json, os, Levenshtein
from owlready2 import *

def normalize_list(l):
    norm_list = []
    for element in l:
        norm_list.append(str(element).lower().replace("_","").split(".")[1])
    return norm_list

# directory dove ci sono tutti i manifest .json
files = os.listdir("/file/files prof/manifests")

# directory dell'ontologia
onto_path.append("/file/files prof/mara ontology")
onto = get_ontology("mara.owl").load()

# # metto in una lista tutte le classi e gli individui dell'ontologia
class_list = list(onto.classes())
# individuals_list = list(onto.individuals())

# normalizzo tutta la lista degli individui e delle classi per ottimizzare la ricerca degli elementi
# normalized_list_individuals = normalize_list(individuals_list)
normalized_class_list = normalize_list(class_list)


# cerco l'individuo più vicino all'annotazione letta
def get_nearest_individual(s1):

    detail = None

    individuals_list = list(onto.individuals())
    normalized_list_individuals = normalize_list(individuals_list)

    s = s1.lower().replace("_","")[5:]
    
    max_sim = 0
    max_individuo = None
    for ind in normalized_list_individuals:
        sim = 1 - (Levenshtein.distance(ind, s)/ max(len(s), len(ind)))
        if sim > max_sim:
            max_sim = sim
            max_individuo = ind

    if max_sim >0.72:
        index = normalized_list_individuals.index(max_individuo)
        ind_name = str(individuals_list[index])[5:]
        detail = onto.search_one(iri= f"*{ind_name}")
        # print("STRING: "+s+" IND: "+str(detail.name))
    else: 
        # print("Creo il nuovo individuo: "+s)
        # vuol dire che non ho trovato corrispondenza con un individuo già presente nell'ontologia
        # bisogna creare un nuovo individuo
        # verificare che il nome sia diverso da quello di una classe
        if s in normalized_class_list:
            index = normalized_class_list.index(s)
            searched_class = str(class_list[index]).split(".")[1]
            onto_class = onto.search_one(iri=f"*{searched_class}")
            onto_class(s+"_norba")
            t = s+"_norba"
            detail = onto.search_one(iri = f"*{t}")        
        else:
                # creo l'oggetto relativo
                if "cas" in s or "domu" in s:
                    onto.Domus(s)
                elif "strad" in s or "vie" in s:
                    onto.Vie(s)
                elif "marcia" in s:
                    onto.Pavimenti(s)
                else:
                    onto.Beni(s)
                detail = onto.search_one(iri = f"*{s}")

    return detail


# per ogni file della directory devo leggerlo e popolare l'ontologia
for file in files:

    individuals_list = list(onto.individuals())
    normalized_list_individuals = normalize_list(individuals_list)
    annotation_file = open("/file/files prof/manifests/"+str(file), "r")
    data = json.load(annotation_file)
    
    # print(data['id'])
    norba = onto.search_one(iri = "*Norba")
    manifest = onto.Manifest(str(data['id']))
    manifest.isPartOf.append(norba)

    #prendo tutti i canvas del manifest    
    for input in data['items']:

        # print(input['id'])
        canvas = onto.Canvas(str(input['id']))
        canvas.hasManifest.append(manifest)
        canvas.isPartOf.append(norba)

        try:    
            for annotation in input['annotations']['items']:
                # print(str(annotation['id'])+" ----> "+str(annotation['body']['value']))
                an = onto.Annotation(str(annotation['id']))
                detail = get_nearest_individual(str(annotation['body']['value']))

                # assegno le object property
                canvas.hasAnnotation.append(an)
                an.isPartOf.append(norba)
                an.isInCanvas.append(canvas)
                an.hasDetail.append(detail)
                detail.isPartOf.append(norba)
                detail.isContainedIntoAnnotation.append(an)
                    
        except:
            continue

onto.save(file = "ext_mara.owl", format = "rdfxml")