# DHBP Routing Logic

import random
import time
import heapq
from src.objects import *
from src.topology import *
from collections import deque

# Why hop table? -> Separates DHBP from BP, BP simply uses queue length, DHBP uses num of hops left
# Also, we are assuming that hops take little to no time to calculate (based on the paper)
# The hop table will represent this as a search-up time

dhbp_cache = {}

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

def build_hop_table(topology):
    topology_size = len(topology.nodes)
    hop_table = [[-1 for _ in range(topology_size)] for _ in range(topology_size)]

    # all_neighbors[i] holds a list of node i's neighbors
    # should be 36 lists, each with 4 nodes
    all_neighbors = []
    for i in range(topology_size):
        node = topology.nodes[i]
        all_neighbors.append(find_neighbors(topology, node))

    for i in range(topology_size):
        node = topology.nodes[i]
        distance = {node : 0}
        neighbor_queue = deque([node])

        while neighbor_queue:
            x = neighbor_queue.popleft()
            for y in all_neighbors[x.id]:
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


def get_next_dhbp_hop(packet, packet_location, topology):
    # Returns next hop (a Node object)
    topology_size = len(topology.nodes)

    if 'table' not in dhbp_cache: # Save table instead of rebuilding each time
        dhbp_cache['table'] = build_hop_table(topology)

    hop_table = dhbp_cache['table']
    destination_hops_delay = hop_table[packet_location.id][packet.destination.id]
    # ------------------------- Then we need to enqueue packet here ? ----------------------------

    backlog = [[0 for _ in range(topology_size)] for _ in range(topology_size)]
    backlog = construct_backlog(topology, packet_location, hop_table)
    backlog[packet_location.id][packet.destination.id] += destination_hops_delay

    # When packet is dequeued: we decide the next hop
    # print(hop_table[2][21])
    # print(hop_table[3][21])
    # print(hop_table[9][21])
    #time.sleep(10000)

    neighbors = find_neighbors(topology, packet_location)
    # Propagation will only be allowed within a region
    omega = []
    for n in neighbors:
        if is_in_region(packet, n):
            candidate_backlog = construct_backlog(topology, n, hop_table)
           # # print()
           # # print("candidate backlog:", candidate_backlog)
           # # print()
            # Equation 15
            heapq.heappush(omega, (backlog[packet_location.id][packet.destination.id] - 
                         candidate_backlog[n.id][packet.destination.id], n))
     
    # Not necessary, but including it for detail
    backlog[packet_location.id][packet.destination.id] -= destination_hops_delay

    # print(omega)
    weight1, candidate1 = heapq.heappop(omega)
    weight2, candidate2 = heapq.heappop(omega)
    true_candidate = candidate2
    # print("Candidate1: ", candidate1)
    # print("Candidate2: ", candidate2)


    # print("Hops for each Candidate: ", hop_table[candidate1.id][packet.destination.id], hop_table[candidate2.id][packet.destination.id])
    if weight1 == weight2:
        if hop_table[candidate1.id][packet.destination.id] < hop_table[candidate2.id][packet.destination.id]:
            true_candidate = candidate1
        

    # print("Sending to node: ", true_candidate)
    return true_candidate

def rudimentary_test(packet, packet_location, topology: Topology):
    # random_link = random.choice(list(packet_location.links.get_partner()))
    ## print("Hi test")
    pass

def clear_dhbp_cache():
    dhbp_cache.clear()