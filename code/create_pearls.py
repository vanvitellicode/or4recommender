from owlready2 import *
import create_cluster as cp

onto_path.append("/")
onto = get_ontology("extended_mara_with_poi.owl").load()

def get_coordinates(pearl):
    coordinates = []
    pearl = cp.remove_prefix(pearl)
    latitude = list(default_world.
                                    sparql("""SELECT ?x WHERE{ 
                                            <http://www.semanticweb.org/ontologies/2011/0/ProgettoAteneo2.owl#"""+pearl+""">
                                            <http://www.semanticweb.org/ontologies/2011/0/ProgettoAteneo2.owl#latitude> 
                                            ?x
                                            } """))

    long = list(default_world.
                                    sparql("""SELECT ?x WHERE{ 
                                            <http://www.semanticweb.org/ontologies/2011/0/ProgettoAteneo2.owl#"""+pearl+""">
                                            <http://www.semanticweb.org/ontologies/2011/0/ProgettoAteneo2.owl#longitude> 
                                            ?x
                                            } """))
    coordinates.append((latitude[0][0], long[0][0]))
    return coordinates 

def getPOIwithDetail():
    poi = list(default_world.
                                       sparql("""SELECT DISTINCT ?poi  WHERE{ 
                                                ?poi
                                                rdf:type 
                                                <http://www.semanticweb.org/ontologies/2011/0/ProgettoAteneo2.owl#POI>
                                                ?poi <http://www.semanticweb.org/ontologies/2011/0/ProgettoAteneo2.owl#hasDetail> ?X
                                                } """))
    poi = cp.clean_list(poi)
    return poi 

def getCanvasFromPOI(poi_list):
    added_tuple =[]
    added_canvas = []
    pearls_file = open("/pearls.txt", "w")
    # pearls_file = open("/pearls_test.txt", "w")
    for poi in poi_list:
        detail_list = cp.hasDetailList(poi)
        for detail in detail_list:
            annotation_list = cp.isContainedIntoAnnotation(detail)
            for an in annotation_list:
                canvas = cp.isInCanavs(an)
                if (str(poi), str(canvas)) not in added_tuple and str(canvas) not in added_canvas:
                    print(str(poi)+","+str(canvas[0]), file=pearls_file)
                    added_tuple.append((str(poi), str(canvas)))
                    added_canvas.append(str(canvas))

if __name__ == '__main__':
    print("creating Perls...")
    getCanvasFromPOI(getPOIwithDetail())
