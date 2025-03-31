import requests
import possible_route as pr
import create_cluster as cr
import debug_print as dp
import random
import time
import csv
import math
import user
import os
import flask_cors
import flask



def print_canvas_wp(canvas_list):
    json = []
    for i,fc in enumerate(canvas_list):
            json.append({"id":i, "canvas":str(fc), "pearl":str(get_pearl_from_canvas(fc))})
    return json

def print_canvas(canvas_list):
    for i, c in enumerate(canvas_list):
        print(str(i)+") "+str(c))

def get_pearl_from_canvas(canvas):
    file = open("pearls.txt", "r")
    file_csv = csv.reader(file, delimiter=',')

    pearls_that_contain_canvas = []

    for row in file_csv:
        if str(canvas) == str(row[1]):
            pearls_that_contain_canvas.append(row[0])    
    file.close()

    return pearls_that_contain_canvas

def get_number_of_canvas_from_pearl(pearl):
    file_pearl = open("pearls.txt","r")
    file_pearl_csv = csv.reader(file_pearl, delimiter=',')
    canvas_counter = 0
    for row in file_pearl_csv:
        if row[0] == pearl:
            canvas_counter += 1
    
    file_pearl.close()
    return canvas_counter

def get_point_from_canvas(actual_canvas):
    file = open("points.txt","r")
    file_csv = csv.reader(file, delimiter=',')
    actual_canvas_point = []
    for row in file_csv:
        if str(row[0]) == str(actual_canvas):
            actual_canvas_point.append(row[1])
            actual_canvas_point.append(row[2])
    
    file.seek(0,0)
    return actual_canvas_point

def check_canvas_pearl(canvas, route, actual_pearl, canvas_counter):
    file_pearl = open("pearls.txt","r")
    file_pearl_csv = csv.reader(file_pearl, delimiter=',')

    for row in file_pearl_csv:

        if row[0] == route[actual_pearl] and cr.remove_prefix(row[1]) == canvas:
            return canvas_counter/(get_number_of_canvas_from_pearl(route[actual_pearl]))
        else:
            if actual_pearl == 0:
                # se la mia perla è la zero oltre ad analizzare i canvas interni alla mia perla considero anche quelli della perla successiva
                if cr.remove_prefix(row[1]) == canvas and row[0] == route[actual_pearl+1]:
                    return  (get_number_of_canvas_from_pearl(route[actual_pearl]))/canvas_counter  
            elif actual_pearl == len(route)-1:
                # se sto nell'ultima perla analizzo sempre i miei canvas e quelli della perla precedente dando una penality se torno indietro
                if cr.remove_prefix(row[1]) == canvas and row[0] == route[actual_pearl-1]:
                    return  10*(get_number_of_canvas_from_pearl(route[actual_pearl]))/canvas_counter
            else:
                # sono la perla centrale (o una di esse) e quindi analizzo i canvas che sono prima e dopo di me
                if cr.remove_prefix(row[1]) == canvas and row[0] == route[actual_pearl+1]:
                    return (get_number_of_canvas_from_pearl(route[actual_pearl]))/canvas_counter
                elif cr.remove_prefix(row[1]) == canvas and row[0] == route[actual_pearl-1]:
                    return 10*(get_number_of_canvas_from_pearl(route[actual_pearl]))/canvas_counter
        
    file_pearl.close()
    return -1

def get_profile_point(preferences):
    return [preferences[0]/preferences[2], preferences[1]/preferences[2]]

def update_profile_preferences(canvas, user, actual_pearl):

    # aggiungo il canvas alla lista di canvas visitati dell'utente
    user.visited_canvas.append(str(canvas))
    user.canvas_in_pearl_counter[actual_pearl] += 1

    # inizializzo la lista delle preferenze a seconda dei canvas visitati dall'utente
    if len(user.preferences) == 0:
        user_num_x = 0
        user_num_y = 0
        user_den = 0
    else:
        user_num_x = user.preferences[0]
        user_num_y = user.preferences[1]
        user_den = user.preferences[2]

    cluster_axis = ['ext_mara.Beni','ext_mara.Tecniche_Edilizie'] # supponiamo siano le preferenze dell'utente
    user_info = cr.clustering([canvas],cluster_axis)
    user_num_x += user_info[0][1][cluster_axis[0]]
    user_num_y += user_info[0][1][cluster_axis[1]]
    user_den += user_info[1]

    return [user_num_x, user_num_y, user_den]

# ! FUNZIONE CHE RESTITUISCE LA LISTA CONTENENTE I CANVAS PIÙ VICINI
def get_next_canvas(actual_canvas, route, actual_pearl, canvas_counter, user, filtered_canvas):
    
    # apro il file dei punti
    file = open("points.txt","r")
    file_csv = csv.reader(file, delimiter=',')
    
    # recuper i punti dai quali calcolerò la distanza
    profile_point = get_profile_point(user.preferences)
    actual_canvas_point = get_point_from_canvas(actual_canvas)
    
    # struttura contenente i canvas con le relative distanze
    distances_between_canvas = []
    
    for row in file_csv:
        
        pi = check_canvas_pearl(cr.remove_prefix(str(row[0])), route, actual_pearl, canvas_counter)
        
        # se qui nell'if aggiungo anche la condizione se presente o meno nella filtered_list lavoro solo su quelli appartenenti a quel cluster
        if pi > 0 and str(row[0]) not in user.visited_canvas:
        # if pi > 0 and str(row[0]) not in user.visited_canvas and str(row[0]) in filtered_canvas:    
            
            alpha1 = math.sqrt(pow(float(actual_canvas_point[0])-float(row[1]),2)+pow(float(actual_canvas_point[1])-float(row[2]),2))
            alpha2 = math.sqrt(pow(float(profile_point[0])-float(row[1]),2)+pow(float(profile_point[1])-float(row[2]),2))
            
            # print("\nCanvas: "+str(cr.remove_prefix(str(row[0])))
                #   +"\nDistance(alpha1): "+str(alpha1)+" \nDistance(alpha2): "+str(alpha2)
                #   +"\nTotal distance: "+str(pi*(alpha1+alpha2))+"\npi: "+str(pi)+"\n"+"Pearl: "+
                #   str(get_pearl_from_canvas(row[0])[0])+"\n")
            
            distances_between_canvas.append((row[0], pi*(alpha1+alpha2), get_pearl_from_canvas(row[0])))
    
    # print("CANVAS ANALYZED: "+str(len(distances_between_canvas))+"\n")
    distances_between_canvas_new = []
    for element in distances_between_canvas:
        url = element[0].split("ext_mara.")[1].split(".json")[0]+".json"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            canvas_id = element[0].split("ext_mara.")[1]
            item = next((element for element in items if element['id'] == canvas_id), None)
            if item:
                try:
                    a = item['items'][0]['items'][0]['body']['id']
                    distances_between_canvas_new.append(element)
                except:
                    None
    distances_between_canvas = distances_between_canvas_new
    distances_between_canvas.sort(key=lambda a:a[1])

    print(dp.debug_line)
    for d in distances_between_canvas:
        print(d)
    print(dp.end_line+"\n")
    suggested_canvas = []
    for i in range(2):
        suggested_canvas.append(distances_between_canvas[i][0])
    file.close()

    return suggested_canvas

# ? ―――――――――――――――――――――――――――――――――― MAIN ――――――――――――――――――――――――――――――――――


#create a post to create a session in flask
app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config["CORS_HEADERS"] = "Content-Type"
cors = flask_cors.CORS(app, resources={r"/api/*": {"origins": "*"}})


active_users = {}
user_first_choice_done = {}
actual_pearl_for_user = {}
filtered_canvas_for_user = {}
sample_route = ('extended_mara_with_poi.12._Complesso_termale', 
                'extended_mara_with_poi.2._Porta_Maggiore_e_le_mura_di_Norba', 
                'extended_mara_with_poi.14._Tempio_di_Giunone_Lucina')

@app.route("/api/create_session", methods=["POST"])
def create_session():
    data = flask.request.json
    active_users[data["name"]]=user.User(data["name"], [], sample_route)
    actual_pearl = actual_pearl_for_user[data["name"]] = 0
    #returnstring = pr.print_route_pos(actual_pearl, sample_route)
    total_canvas = 0
    
    for pearl in sample_route:
        total_canvas += get_number_of_canvas_from_pearl(pearl)
    
    # prendo tutti i canvas cotenuti nella perla
    canvas_list = pr.get_canvas_from_pearl(sample_route[actual_pearl])
    # print("The canvas inside this perl are: ")
    # print_canvas(canvas_list)
    # prendo i canvas contenuti nel cluster che parla "di più" di beni e tecniche edilizie;
    filtered_canvas = pr.filter_canvas(canvas_list)
    filtered_canvas_for_user[data["name"]] = filtered_canvas
    print("\nBased on clustering, I suggest you this canvas: ")
    js = print_canvas_wp(filtered_canvas)
    return flask.jsonify({"status": "ok", "response": js })


#create api to choose next canvas
@app.route("/api/choose_first_canvas", methods=["POST"])
def choose_first_canvas():
    data = flask.request.json
    user_name = data["name"]
    choiced_canvas = data["canvas"]
    actual_pearl = actual_pearl_for_user[user_name]
    user = active_users[user_name]
    if(data["name"] not in user_first_choice_done.keys()):
        user_first_choice_done[user_name] = True
    else:
        return flask.jsonify({"status": "ok", "response": "You have already chosen a canvas"})
    # print("The user "+user_name+" is looking the canvas: "+choiced_canvas+"\n")
    choiced_canvas = filtered_canvas_for_user[user_name][int(choiced_canvas)]
    user.preferences = update_profile_preferences(choiced_canvas, user, actual_pearl)
    
    suggested_canvas = get_next_canvas(choiced_canvas, sample_route, actual_pearl, user.canvas_in_pearl_counter[actual_pearl], user, 0)
    filtered_canvas_for_user[data["name"]] = suggested_canvas

    js = print_canvas_wp(suggested_canvas)
    return flask.jsonify({"status": "ok", "response": js })

#create api to choose next canvas
@app.route("/api/choose_next_canvas", methods=["POST"])
def choose_next_canvas():
    data = flask.request.json
    user_name = data["name"]
    choiced_canvas = data["canvas"]
    actual_pearl = actual_pearl_for_user[user_name]
    user = active_users[user_name]
    # print("The user "+user_name+" is looking the canvas: "+choiced_canvas+"\n")
    choiced_canvas = filtered_canvas_for_user[user_name][int(choiced_canvas)]
    if sample_route[actual_pearl] not in get_pearl_from_canvas(choiced_canvas):
        return({"status": "ok", "response": "You're looking for another pearl, this need your move to another POI! If you are sure, reselect canvas in /api/go_next_pearl"})
    else:
        user.preferences = update_profile_preferences(choiced_canvas, user,actual_pearl)
        suggested_canvas = get_next_canvas(choiced_canvas, sample_route, actual_pearl, user.canvas_in_pearl_counter[actual_pearl], user, 0)
        filtered_canvas_for_user[data["name"]] = suggested_canvas
        js = print_canvas_wp(suggested_canvas)
        return flask.jsonify({"status": "ok", "response": js })

#create api to choose next pearl
@app.route("/api/go_next_pearl", methods=["POST"])
def go_next_pearl():
    data = flask.request.json
    user_name = data["name"]
    choiced_canvas = data["canvas"]
    actual_pearl = actual_pearl_for_user[user_name]
    user = active_users[user_name]
    choiced_canvas = filtered_canvas_for_user[user_name][int(choiced_canvas)]
    if sample_route[actual_pearl] in get_pearl_from_canvas(choiced_canvas):
        return flask.jsonify({"status": "ok", "response": "This choice will not result in moving in another pearl"})
    else:

        previous_pearl = actual_pearl
        #user.change_pearl_satisfaction_value.append(user.satisfaction[-1])
        #user.change_pearl_counter+=1
        actual_pearl_str = get_pearl_from_canvas(choiced_canvas)
        actual_pearl = sample_route.index(actual_pearl_str[0])
        actual_pearl_for_user[user_name] = actual_pearl
        user.preferences = update_profile_preferences(choiced_canvas, user,actual_pearl)
        suggested_canvas = get_next_canvas(choiced_canvas, sample_route, actual_pearl, user.canvas_in_pearl_counter[actual_pearl], user, 0)
        filtered_canvas_for_user[data["name"]] = suggested_canvas
        js = print_canvas_wp(suggested_canvas)
        return flask.jsonify({"status": "ok", "response": js })

if __name__ == '__main__':     
    print(dp.initial)
    #start app
    app.run(host="0.0.0.0", port=5000, debug=True)