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
    s_x, s_y = packet.source.pos_x, packet.source.pos_y
    d_x, d_y = packet.destination.pos_x, packet.destination.pos_y
    c_x, c_y = candidate.pos_x, candidate.pos_y

    # Helper Function: Checks to see if the candidate is near an edge to allow for wraparound
    def is_between_wrap(source, dest, candidate, grid_size=6):
        if source == dest:
            return candidate == source

        # This is the straight line distance
        direct_dist = abs(dest - source)

        # If the distance is 3 or less, shortest path doesn't need wrapping
        if direct_dist <= grid_size / 2: # Which direction  bounding box should be drawn
            return min(source, dest) <= candidate <= max(source, dest)
        else: # Otherwise, shortest path wraps around the edge
            return candidate >= max(source, dest) or candidate <= min(source, dest)
    # Valid candidate has to be within the shortest-path bounds for both X and Y
    return is_between_wrap(s_x, d_x, c_x) and is_between_wrap(s_y, d_y, c_y)

def construct_backlog(topology, node, hop_table):
    # Create blank dictionary 
    backlog = {}

    for packet in node.buffer.items: #If node has packet headed to destination node:
        dest_id = packet.destination.id 
        # Add hop penalty to destination's running total
        # .get(dest_id, 0) typically has a default of 0 if dest isnt in backlog 
        # .get is what was recommended online, since it looks up keys without crashing if the key doesn't exist
        backlog[dest_id] = backlog.get(dest_id, 0) + hop_table[node.id][dest_id]

    return backlog


def get_next_dhbp_hop(packet, packet_location, topology):
    # Returns next hop (a Node object)
    topology_size = len(topology.nodes)

    # Cache table, this lets us only calculate grid's distance once
    if 'table' not in dhbp_cache: # Save table instead of rebuilding each time
        dhbp_cache['table'] = build_hop_table(topology)

    hop_table = dhbp_cache['table']
    destination_hops_delay = hop_table[packet_location.id][packet.destination.id]
    # ------------------------- Then we need to enqueue packet here ? ----------------------------

    # Calculate current node's backlog weight regarding the current packet's dest
    backlog = construct_backlog(topology, packet_location, hop_table)
    weight = backlog.get(packet.destination.id, 0) + destination_hops_delay

    # When packet is dequeued: we decide the next hop

    neighbors = find_neighbors(topology, packet_location)
    # Propagation will only be allowed within a region
    # print("Neighbors: ", neighbors)
    omega = []
    for n in neighbors:
        if is_in_region(packet, n):
            # Calculate hypothetical backlog weight for this region
            candidate_backlog = construct_backlog(topology, n, hop_table)
            candidate_weight = candidate_backlog.get(packet.destination.id, 0)

            # w is the pressure difference
            w = weight - candidate_weight
            hops_to_dest = hop_table[n.id][packet.destination.id]
            # Equation 15
            # Heapq always pops smallest value, thus we need to do -w to look for biggest pressure difference
            # Then hops_to_dest breaks ties and chooses the shorest path
            # n also breaks ties without having to do weird node comparisons
            heapq.heappush(omega, (-w, hops_to_dest, n.id, n))

    # Incase the bounding box blocks everything, don't move
    if not omega:
        return packet_location

    # Gets the best candidate 
    best_weight, best_hops, best_id, true_candidate = heapq.heappop(omega)

    return true_candidate


def rudimentary_test(packet, packet_location, topology: Topology):
    # random_link = random.choice(list(packet_location.links.get_partner()))
    ## print("Hi test")
    pass

def clear_dhbp_cache():
    dhbp_cache.clear()