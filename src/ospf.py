# OSPF routing logic
from src.topology import *
from src.objects import *
import heapq
import time

dijkstra_cache = {}

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

def dijkstra(topology, starting_node):
    #print("Starting dijkstra on: ", starting_node)
    # Calculate shortest paths from starting node
    # Dijkstra -> least-costs -> source node -> look at neighbors -> take lowest cost -> look at that node's neighbors, add to set
    # -> take lowest cost again -> repeat

    # Tracks the best next hop depending on destination, index i corresponds to node i
    routing_table = []
    topology_size = len(topology.nodes)
    for i in range(topology_size):
        routing_table.append(starting_node)

    distance = []
    for i in range(topology_size):
            distance.append(float('inf'))
    distance[starting_node.id] = 0

    visited = set()
    visited.add(starting_node.id)
    next_check = []
    neighbors = []

    heapq.heappush(next_check, (0, starting_node))

    while next_check:
        cost, node = heapq.heappop(next_check)

        if cost > distance[node.id]:
            continue
        #if node.id in visited:
            #continue

        distance[node.id] = cost
        neighbors = find_neighbors(topology, node)

        # We assume every link is of cost 1, we consider num of hops to be the only cost
        new_cost = cost + 1
        for i in neighbors:
            
            if distance[i.id] > new_cost:
                # print("visited: ", visited)
                # print("i.id: ", i.id)
                distance[i.id] = new_cost
                # In theory, the routing table should have the index for the next hop,
                # if that hop is not a neighbor node, then it will take the value in that element
                # and index again, this will continue until we get a neighbor node that we can hop to
                if node == starting_node:
                    routing_table[i.id] = i
                else:
                    routing_table[i.id] = node


                heapq.heappush(next_check, (new_cost, i))

        visited.add(node.id)
    # print("ROUTING TABLE FOR: ", starting_node, " with a length of: ", len(routing_table))
    # print(routing_table)
    # print("DISTANCE TABLE FOR: ", starting_node, " with a length of: ", len(distance))
    # print(distance)
    return routing_table, distance

def build_routing_table(topology):
    # Call Dijkstra() to build and return a routing table
    # Organize results so that the simulator can easily lookup the next hop from get_next_ospf_hop()
    pass

def get_next_ospf_hop(packet, packet_location, topology):
    if packet_location.id not in dijkstra_cache:
        dijkstra_cache[packet_location.id] = dijkstra(topology,packet_location)

    # Returns next hop (a Node object)
    routing_table, distance = dijkstra_cache[packet_location.id]

    source = packet.source
    destination = packet.destination
    found_next_hop = False
    source_neighbors = find_neighbors(topology, packet_location)

    candidate = routing_table[destination.id]
    while not found_next_hop:

        if candidate in source_neighbors:
            found_next_hop = True
        else:
            if candidate.id == packet_location.id or routing_table[candidate.id] == candidate:
                return candidate
            candidate = routing_table[candidate.id]

    #print("routing: ", routing_table)
    #print("distance: ", distance)
    return candidate

def clear_ospf_cache():
    dijkstra_cache.clear()
 
