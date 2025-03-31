from owlready2 import *
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
from IPython.display import HTML
import rdflib
import csv
import numpy as np
from sklearn.cluster import KMeans
from math import radians, cos, sin, asin, sqrt

onto_path.append("")
onto = get_ontology("ext_mara.owl").load()
# onto = get_ontology("extended_mara_with_poi.owl").load()

# metto in una lista tutte le classi e gli individui dell'ontologia
class_list = list(onto.classes())
individuals_list = list(onto.individuals())

def remove_prefix(s):
    return str(s).split(".",1)[1]

def clean_list(list):
    return_list = []
    for element in list:
        return_list.append(element[0])

    return return_list

def get_all_canvas():
    canvas = list(default_world.
                                       sparql("""SELECT DISTINCT ?canvas WHERE{ 
                                                ?canvas
                                                rdf:type 
                                                <http://www.semanticweb.org/ontologies/2011/0/ProgettoAteneo2.owl#Canvas>
                                                } """))
    canvas = clean_list(canvas)
    return canvas    

def hasAnnotation(canvas):
    canvas = remove_prefix(canvas)
    annotation_contained_into_canvas = list(default_world.
                                       sparql("""SELECT ?annotation WHERE{ 
                                                <http://www.semanticweb.org/ontologies/2011/0/ProgettoAteneo2.owl#""" +canvas+"""> 
                                                <http://www.semanticweb.org/ontologies/2011/0/ProgettoAteneo2.owl#hasAnnotation>
                                                ?annotation } """))
    annotation_contained_into_canvas = clean_list(annotation_contained_into_canvas)
    return annotation_contained_into_canvas
    
def hasDetail(annotation):
    annotation = remove_prefix(annotation)
    detail_of_annotation = list(default_world.
                                    sparql("""SELECT ?detail WHERE{ 
                                                <http://www.semanticweb.org/ontologies/2011/0/ProgettoAteneo2.owl#""" +annotation+"""> 
                                                <http://www.semanticweb.org/ontologies/2011/0/ProgettoAteneo2.owl#hasDetail>
                                                ?detail } """))
    detail_of_annotation = clean_list(detail_of_annotation)
    return detail_of_annotation[0]

def hasDetailList(annotation):
    annotation = remove_prefix(annotation)
    detail_of_annotation = list(default_world.
                                    sparql("""SELECT ?detail WHERE{ 
                                                <http://www.semanticweb.org/ontologies/2011/0/ProgettoAteneo2.owl#""" +annotation+"""> 
                                                <http://www.semanticweb.org/ontologies/2011/0/ProgettoAteneo2.owl#hasDetail>
                                                ?detail } """))
    detail_of_annotation = clean_list(detail_of_annotation)
    return detail_of_annotation

def isContainedIntoAnnotation(detail):
    detail = remove_prefix(detail)
    annotation_of_detail = list(default_world.
                                    sparql("""SELECT DISTINCT ?an WHERE{ 
                                                <http://www.semanticweb.org/ontologies/2011/0/ProgettoAteneo2.owl#""" +detail+"""> 
                                                <http://www.semanticweb.org/ontologies/2011/0/ProgettoAteneo2.owl#isContainedIntoAnnotation>
                                                ?an } """))
    annotation_of_detail = clean_list(annotation_of_detail)
    return annotation_of_detail

def isInCanavs(annotation):
    annotation = remove_prefix(annotation)
    canvas_of_annotation = list(default_world.
                                    sparql("""SELECT DISTINCT ?can WHERE{ 
                                                <http://www.semanticweb.org/ontologies/2011/0/ProgettoAteneo2.owl#""" +annotation+"""> 
                                                <http://www.semanticweb.org/ontologies/2011/0/ProgettoAteneo2.owl#isInCanvas>
                                                ?can } """))
    canvas_of_annotation = clean_list(canvas_of_annotation)
    return canvas_of_annotation

def subClassOf(onto_class):
    onto_class = remove_prefix(onto_class)
    super_class = list(default_world.
                                    sparql("""SELECT ?can WHERE{ 
                                                <http://www.semanticweb.org/ontologies/2011/0/ProgettoAteneo2.owl#""" +onto_class+"""> 
                                                rdfs:subClassOf
                                                ?can } """))
    super_class = clean_list(super_class)
    return super_class[0]

def get_super_class(detail):
    detail = remove_prefix(detail)
    super_class = list(default_world.
                                    sparql("""SELECT ?class WHERE{ 
                                                <http://www.semanticweb.org/ontologies/2011/0/ProgettoAteneo2.owl#""" +detail+"""> 
                                                rdf:type
                                                ?class
                                                filter(?class != owl:Class)
                                                filter(?class != owl:NamedIndividual)
                                                } """))
    super_class = clean_list(super_class)
    return super_class[0]

def create_graph_from_canvas(canvas, G):
    for c in canvas:
        annotations = hasAnnotation(c)
        for an in annotations:    
            detail = hasDetail(an)
            for d in detail:
                annotations_of_detail = isContainedIntoAnnotation(d)
                for an in annotations_of_detail:
                    canvas_of_annotation = isInCanavs(an)
                    for i in canvas_of_annotation:
                        G.add_node(str(i)[50:])
                        G.add_edge(str(c),str(i)[50:])
    
    net=Network(filter_menu=True, layout='dot', directed=True, select_menu=True)
    net.from_nx(G)
    net.save_graph("./canvas_graph.html")
    HTML(filename="./canvas_graph.html")

def get_mara_distances():
    
    nif = rdflib.Namespace('http://www.semanticweb.org/ontologies/2011/0/ProgettoAteneo2.owl#')
    g = rdflib.Graph()
    g.parse ('ext_mara.owl', format='application/rdf+xml')
    
    # creo un grafo networkx
    onto_graph = nx.MultiDiGraph()
    
    # itero tra le triple
    for s, p, o in g:
        onto_graph.add_edge(str(s), str(o), key=str(p))

    fout = open("ext_ara_distances.csv", "w")

    for c in get_all_canvas():
        for e in get_all_canvas():
            if c != e:
                try:
                    p = nx.shortest_path(onto_graph, nif+remove_prefix(c), nif+remove_prefix(e))    
                    print(str(p[0])[106:]+", "+str(p[len(p)-1])[106:]+", "+str(len(p)), file= fout)
                    print(str(p), file= fout)
                except:
                    continue

def clustering(canvas_list, axes):
    
    clustering_list = []
    subclass_axis = []
    clustering_dict = {}
    annotation_len = 0
    for axis in axes:
        clustering_dict[axis] = 0
        subclass_axis.append(get_all_subclass(axis))
        
    for canvas in canvas_list:
        
        for axis in axes:
            clustering_dict[axis] = 0    
        
        clustering_list.append(canvas)
        annotations_list = hasAnnotation(canvas)
        annotation_len = len(annotations_list)
        for annotation in annotations_list:
            detail = hasDetail(annotation)
            individual_class = get_super_class(detail)

            if str(individual_class) in axes:
                clustering_dict[str(individual_class)] += 1
            else:
                for sbl in subclass_axis:
                    if individual_class in sbl:
                        index = subclass_axis.index(sbl)
                        clustering_dict[str(axes[index])] += 1

        # normalizzazione sul numero totale di annotazioni
        # for axis in axes:
        #     if len(annotations_list) != 0:
        #         clustering_dict[axis] = clustering_dict[axis]/len(annotations_list)
        
        clustering_list.append(clustering_dict)
        clustering_dict = {}
    return clustering_list, annotation_len

def clustering_metric2(canvas_list, axes):
    
    clustering_list = []
    subclass_axis = []
    clustering_dict = {}
    
    for axis in axes:
        clustering_dict[axis] = 0
        subclass_axis.append(get_all_subclass(axis))
        
    for canvas in canvas_list:
        
        for axis in axes:
            clustering_dict[axis] = 0    
        
        clustering_list.append(canvas)
        annotations_list = hasAnnotation(canvas)
        for annotation in annotations_list:
            detail = hasDetail(annotation)
            individual_class = get_super_class(detail)

            for ax in axes:
                sim = 0
                if str(individual_class) != str(ax):
                    s = distance(individual_class, ax)
                    if s > 0:
                        sim += s
                else:
                    sim = 1
                
                clustering_dict[ax] += sim
                # print("AXIS: "+str(ax)+" ---- INDIV: "+str(individual_class)+" ---- VALUE: "+str(sim))

        # normalizzazione sul numero totale di annotazioni
        for axis in axes:
            if len(annotations_list) != 0:
                clustering_dict[axis] = clustering_dict[axis]/len(annotations_list)
        
        clustering_list.append(clustering_dict)
        clustering_dict = {}
    return clustering_list

def distance(individual_class, axis):
    individual_class = remove_prefix(individual_class)
    axis = remove_prefix(axis)
    file = open("mara_distances.csv", "r")
    file_csv = csv.reader(file, delimiter=",")
    
    for row in file_csv:
        if row[0]==individual_class and row[1]==axis:
            sim  = 1/(1+int(row[2]))
            return sim
    
    return -1

def get_canvas_type(canvas_list):
    
    canvas_type = []  
    for canvas in canvas_list:
        canvas_type.append(canvas)
        type = []
        annotations_list = hasAnnotation(canvas)
        for annotation in annotations_list:
            detail = hasDetail(annotation)
            individual_class = get_super_class(detail)
            type.append(individual_class)
        canvas_type.append(type)    
    return canvas_type

def get_all_subclass(cls):
    cls = remove_prefix(cls)
    c  = onto.search_one(iri=f"*{cls}")
    subclasses = list(c.subclasses())  
    for sbc in subclasses:
        sub = list(sbc.subclasses())
        if len(sub)>0:
            for s in sub:
                subclasses.append(s)

    return subclasses

def graph_cluster(kmeans, kmeans_two_cluster):
    
    x = np.linspace(0, 1, 6)
    fig, axs = plt.subplots(2)
    fig.suptitle('Clustering')
    # axs[0].scatter(kmeans_two_cluster.cluster_centers_[:,0], kmeans_two_cluster.cluster_centers_[:,1], color='gray', s=125)
    axs[0].scatter(X[:,0], X[:,1])
    axs[0].set_title('Space')
    axs[0].plot(x, x+0, linestyle='dashed')
    axs[1].scatter(kmeans.cluster_centers_[:,0], kmeans.cluster_centers_[:,1], color='gray', s=125)
    axs[1].scatter(X[:,0], X[:,1], c = kmeans.labels_, cmap='rainbow', s=50)
    axs[1].set_title('n_cluster = 4')
    
    for ax in axs.flat:
        ax.set(xlabel=cluster_axis[0], ylabel=cluster_axis[1])

    plt.show()


# ! MAIN START HERE

if __name__ == "__main__":

    print("Starting...")
    
    init_canvas = 'ext_Mara.https://cosme.unicampania.it/rasta/norba/1-EDIFICI-SACRI/index.json/canvas/10'
    staring_canvas = [init_canvas]
    # voglio clusterizzare rispetto a beni ed elementi architettonici
    canvas_list = get_all_canvas()
    cluster_axis = ['ext_mara.Beni','ext_mara.Tecniche_Edilizie'] # supponiamo siano le preferenze dell'utente
    # cluster_list = clustering(canvas_list,cluster_axis)
    cluster_list = clustering_metric2(canvas_list, cluster_axis)

    # preparo i file per il salvataggio delle informazioni utili
    file_kmeans_4C = open("kmeans4C.txt", "w")
    fout = open("points.txt", "w+")
    
    points = []
    for i,t in enumerate(cluster_list):
        if i%2!=0:
            print(str(t[cluster_axis[0]])+","+ str(t[cluster_axis[1]]), file=fout)
            points.append([t[cluster_axis[0]], t[cluster_axis[1]]])
        else:
            print(str(t)+",", file=fout, end="")

    # creo il dataset
    X = np.array(points)
    
    # clusterizzazione utiliazzando il kmeans
    kmeans = KMeans(n_clusters=4, n_init='auto').fit(X)
    kmeans_two_cluster = KMeans(n_clusters=2, n_init='auto').fit(X)

    for i, l in enumerate(kmeans.labels_):
        print(str(canvas_list[i])+","+str(l) ,file=file_kmeans_4C)

    fout.close()
    file_kmeans_4C.close()
    graph_cluster(kmeans, kmeans_two_cluster)

    
    
