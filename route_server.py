import networkx as nx
from pprint import PrettyPrinter
import random 
import matplotlib.pyplot as plt
from flask import Flask, jsonify, request
import json

pp = PrettyPrinter(indent=2)
app = Flask(__name__)


def create_graph(adj_list:dict):
    topo = nx.Graph() # creates graph 
    for node in adj_list:
        adjacencies = [(node,j) for j in adj_list[node]]
        topo.add_edges_from(adjacencies)
    return topo

def get_routes(topo:nx.Graph, routing_logic:str, source:str, destination:str, cutoff:int = None) -> list:
    """takes a topology and routing logic as input and returns path as node list

    Args:
        topo (nx.Graph): topology graph as adj_list
        routing_logic (str): name of the SPF algo
        source (str): name of the source node
        destination (str): name of the destination node
        cutoff (int): hop count limit 

    Returns:
        list: node list
    """
    ## make cutoff to max if not set explicitly or set higher than node count  
    cutoff = len(topo) if (cutoff == None or cutoff > len(topo)) else cutoff  


    if routing_logic == 'all_simple_paths':
        
        ## from all paths found sort them by hop_count
        all_paths = [path for path in nx.all_simple_paths(topo, source=source, target=destination, cutoff=cutoff)]
        all_paths.sort(key=len) # sort paths by hop count 

        return all_paths
    
    elif routing_logic == 'all_cheapest_paths':
        ## all path with minimal cost from all possible paths found, sort them by hop_count
        all_paths = [path for path in nx.shortest_simple_paths(topo, source=source, target=destination, weight=None)]
        all_paths.sort(key=len) # sort paths by hop count 
        
        return all_paths
    
    elif routing_logic == 'sortest_path_spf':
        return nx.shortest_path(topo, source=source, target=destination, weight=None, method='dijkstra')
    
    elif routing_logic == 'sortest_path_bf':
        return nx.shortest_path(topo, source=source, target=destination, weight=None, method='bellman-ford')
    
    else:
        print('Error: Invalid Routing Logic !!')
        return None

@app.route("/get_routes/", methods=['GET', 'POST'])
def get_route_api():
    payload = json.loads(request.data)
    print('Payload Received:')
    pp.pprint(payload)
    topo = create_graph(adj_list=payload['adj_list'])
    routes = get_routes(topo,
                        routing_logic=payload['routing_logic'], 
                        source=payload['source'], 
                        destination=payload['destination']
                        )
    return jsonify(routes)

def main():
    app.run(port=5001)
    #pp.pprint(get_routes(topo=topo,routing_logic='sortest_path_spf', source='node_2', destination='node_4'))

if __name__ == '__main__':
    main()

## TEST Suite
#test_simple_graph(nodes=20, connected=True, trials=50)
