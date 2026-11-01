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

def is_in_region(packet, candidate):
    source = packet.source
    destination = packet.destination
    x_valid = False
    y_valid = False

    if source.pos_x <= candidate.pos_x and candidate.pos_x <= destination.pos_x:
        x_valid = True

    if source.pos_y <= candidate.pos_y and candidate.pos_y <= destination.pos_y:
        y_valid = True

    return x_valid and y_valid

def construct_backlog(topology, node, hop_table):
    topology_size = len(topology.nodes)
    backlog = [[0 for _ in range(topology_size)] for _ in range(topology_size)]
    backlog_sum = 0

    for packet in node.buffer.items:
        backlog[packet.location.id][packet.destination.id] += hop_table[packet.location.id][packet.destination.id]

    return backlog


def get_next_dhbp_hop(packet, packet_location, topology, hop_table):
    # Returns next hop (a Node object)
    topology_size = len(topology.nodes)

    destination_hops_delay = hop_table[packet_location.id][packet.destination.id]
    # ------------------------- Then we need to enqueue packet here ? ----------------------------

    backlog = [[0 for _ in range(topology_size)] for _ in range(topology_size)]
    backlog = construct_backlog(topology, packet_location, hop_table)
    backlog[packet_location.id][packet.destination.id] += destination_hops_delay

    # When packet is dequeued: we decide the next hop

    neighbors = find_neighbors(topology, packet_location)
    # Propagation will only be allowed within this region
    omega = []
    for n in neighbors:
        if is_in_region(packet, n):
            candidate_backlog = construct_backlog(topology, n, hop_table)
            # Equation 15
            omega.append((backlog[packet_location.id][packet.destination.id] - 
                         candidate_backlog[n.id][packet.destination.id], n))
     
    # Not necessary, but including it for detail
    backlog[packet_location.id][packet.destination.id] -= destination_hops_delay

    candidate = max(omega)
    print("Sending to node: ", candidate)
    return candidate

def rudimentary_test(packet, packet_location, topology: Topology):
    # random_link = random.choice(list(packet_location.links.get_partner()))
    #print("Hi test")
    pass