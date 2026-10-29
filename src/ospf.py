# OSPF routing logic
from src.topology import *
from src.objects import *
import heapq
# I added some recommended architecture to make it mesh nicely with my part,
# but feel free to change things as needed.

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
    # Calculate shortest paths from starting node
    # Dijkstra -> least-costs -> source node -> look at neighbors -> take lowest cost -> look at that node's neighbors, add to set
    # -> take lowest cost again -> repeat

    # Tracks the best next hop depending on destination, index i corresponds to node i
    routing_table = [starting_node.id] * topology.nodes

    distance = [float('inf')] * topology.nodes
    distance[starting_node.id] = 0

    visited = set()
    next_check = []
    neighbors = []

    heapq.heappush(next_check, (0, starting_node))

    while next_check:
        cost, node = heapq.heappop(next_check)

        if cost > distance[node.id]:
            continue
        if node.id in visited:
            continue

        distance[node.id] = cost
        neighbors = find_neighbors(topology, node)

        # We assume every link is of cost 1, we consider num of hops to be the only cost
        new_cost = cost + 1
        for i in neighbors:

            if distance[i.id] > new_cost:
                distance[i.id] = new_cost

                # In theory, the routing table should have the index for the next hop,
                # if that hop is not a neighbor node, then it will take the value in that element
                # and index again, this will continue until we get a neighbor node that we can hop to
                routing_table[i.id] = node.id

                heapq.heappush(next_check, (new_cost, i))

        visited.add(node.id)

    return routing_table

def build_routing_table(topology):
    # Call Dijkstra() to build and return a routing table
    # Organize results so that the simulator can easily lookup the next hop from get_next_ospf_hop()
    pass

def get_next_ospf_hop(packet, packet_location, topology):
    # Returns next hop (a Node object)
    pass