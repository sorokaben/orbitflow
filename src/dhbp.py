# DHBP Routing Logic

import random
from src.objects import *
from src.topology import *
from collections import deque

# Why hop table? -> Separates DHBP from BP, BP simply uses queue length, DHBP uses num of hops left
# Also, we are assuming that hops take little to no time to calculate (based on the paper)
# The hop table will represent this as a search-up time

def find_neighbors(topology, starting_node):
    up = (starting_node.pos_y - 1) if starting_node.pos_y > 0 else 5
    down = (starting_node.pos_y + 1) if starting_node.pos_y < 5 else 0
    left = (starting_node.pos_x - 1) if starting_node.pos_x > 0 else 5
    right = (starting_node.pos_x + 1) if starting_node.pos_x < 5 else 0

    neighbors = [topology.grid[up][starting_node.pos_x],
                 topology.grid[down][starting_node.pos_x],
                 topology.grid[starting_node.pos_y][left],
                 topology.grid[starting_node.pos_y][right]]


    return neighbors

# SHOULD WORK, BUT IDK lol
def build_hop_table(topology):
    topology_size = len(topology.nodes)
    hop_table = [[-1 for _ in range(topology_size)] for _ in range(topology_size)]

    # all_neighbors[i] holds a list of node i's neighbors
    # should be 36 lists, each with 4 nodes
    all_neighbors = []
    for i in range(topology.nodes):
        all_neighbors.append(find_neighbors(topology, i))

    for node in topology.nodes:
        distance = {node : 0}
        neighbor_queue = deque([node])

        while neighbor_queue:
            x = neighbor_queue.popleft()
            for y in all_neighbors[x]:
                if y not in distance:
                    distance[y] = distance[x] + 1
                    neighbor_queue.append(y)

        for other_node, dist in distance.items():
            hop_table[node.id][other_node.id] = dist

    return hop_table


            





def get_next_dhbp_hop(packet, packet_location, topology):
    # Returns next hop (a Node object)
    # TODO: This rudimentary_test is for testing only. Delete it when you actually implement this!
    #print("Hi!")
    #return(rudimentary_test(packet, packet_location, topology))
    pass

def rudimentary_test(packet, packet_location, topology: Topology):
    # random_link = random.choice(list(packet_location.links.get_partner()))
    #print("Hi test")
    pass