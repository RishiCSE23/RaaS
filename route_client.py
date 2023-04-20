import networkx as nx
from pprint import PrettyPrinter
import random 
import matplotlib.pyplot as plt
from flask import Flask, jsonify, render_template, request
import requests
import json

pp = PrettyPrinter(indent=2)
route_client = Flask(__name__)
topo_state = False   # true if topology already exists 

def gen_graph(nodes:int, node_prefix:str='node', connected:bool=False)-> dict:
    """generates a random graph of given number of node

    Args:
        nodes (int): number of nodes
        node_prefix(str): node name format node_prfix_N where N is the index variable

    Returns:
        dict: graph in adjacency list format
    """

    ## create random adjacency matrix
    adj_mat=[[0]*nodes for i in range(nodes)]     # initial Null adjacency matrix 
    for i in range(nodes):
        is_disconnected = True   # true if a node has no neighbour 
        for j in range(i+1,nodes):
            is_connected = random.randint(0,1)  # create random adjacency
            is_disconnected = False if (is_disconnected and bool(is_connected)) else True
            adj_mat[i][j] = adj_mat[j][i] = is_connected
        
        ## run if node_i is isolated and connected flag in True
        if is_disconnected and connected:  
            ## connect node_i with a random node_j
            possible_neighbours_of_i = [k for k in range(nodes) if k != i] #list of nodes except node_i
            j = possible_neighbours_of_i[random.randint(0,nodes-2)]    # node index 0 to node-1, nodes exept node_i
            adj_mat[i][j] = adj_mat[j][i] = 1
    
    ## create adjacency list from the random adjacency matrix 
    adj_list={}  # to return 
    for i in range(nodes):
        adjacencies = [f'node_{j}' for j in range(nodes) if adj_mat[i][j]==1]
        adj_list[f'node_{i}'] = adjacencies
    
    return adj_list

def has_self_loop(topo:dict)->bool:
    """returns true if a graph has self loop otherwise false

    Args:
        topo (dict): graph in adj list 

    Returns:
        bool: true if graph has a self loop
    """
    has_loop = False   # initial assumption
    for node in topo:
        if node in topo[node]:  # node is adjacent to itself => self loop
            has_loop=True
            break
    return has_loop

def test_simple_graph(trials:int, nodes:int, connected:bool): 
    """test is a topo is simple (no self-loop, parallel-edge) for n random trials

    Args:
        trial (int): number of trials 
    """
    for trial in range(trials):
        graph = gen_graph(nodes,connected)
        status = 'Failed' if has_self_loop(graph) else 'Passed'
        print(f'Trial {trial} \t  Status : {status}')

def create_graph(adj_list:dict):
    topo = nx.Graph() # creates graph 
    for node in adj_list:
        adjacencies = [(node,j) for j in adj_list[node]]
        topo.add_edges_from(adjacencies)
    return topo

def plot_topo(topo):
    nx.draw(topo, with_labels=True)
    plt.savefig('static//topo.png')

def build_random_topo(nodes:int, connected:True):
    ## Step 1: Create a random graph 
    random_adj_list = gen_graph(nodes=nodes, connected=connected)
    pp.pprint(random_adj_list)
    
    ## Step 2: Build a NX Topology from graph 
    topo = create_graph(adj_list=random_adj_list)

    ## Step 3: Plot NX topology 
    plot_topo(topo)

@route_client.route('/client_form/', methods=['GET', 'POST'])
def client_form():
    global topo_state
    
    client_params = {}
    if request.method == "POST":
        if topo_state == False:
            client_params['server_ip']= request.form.get('server_ip')
            client_params['server_port']= request.form.get('server_port')
            client_params['nodes'] = int(request.form.get('nodes'))
            client_params['connected'] = bool(request.form.get('connected'))
            client_params['source'] = request.form.get('source')
            client_params['destination'] = request.form.get('destination')
            client_params['routing_logic'] = request.form.get('routing_logic')
            client_params['adj_list'] = gen_graph(nodes=int(request.form.get('nodes')), 
                                                connected=bool(request.form.get('connected')),
                                                node_prefix='node'
                                        )
            
            build_random_topo(nodes=client_params['nodes'], connected=client_params['connected'])
            topo_state = True

        payload = json.dumps({'source':request.form.get('source'), 
                           'destination':request.form.get('destination'),
                           'routing_logic':request.form.get('routing_logic'),
                           'adj_list':gen_graph(nodes=int(request.form.get('nodes')), 
                                                connected=bool(request.form.get('connected')),
                                                node_prefix='node')
                            }, indent=4)
        
        print('=================================')
        print('payload')
        print('---------------------------------')
        print(payload)
        print('=================================')
    
            
        url = f'http://{client_params["server_ip"]}:{client_params["server_port"]}/get_routes'
        print(f'Querying to : {url}...')
        
        response = requests.post(url, data=payload)
        print(response.json())

    return render_template('client_form.html')

if __name__ == '__main__':
    route_client.run()
