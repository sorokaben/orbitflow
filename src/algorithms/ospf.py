# OSPF routing logic

# I added some recommended architecture to make it mesh nicely with my part,
# but feel free to change things as needed.

def dijkstra(topology, starting_node):
    # Calculate shortest paths from starting node
    pass

def build_routing_table(topology):
    # Call Dijkstra() to build and return a routing table
    # Organize results so that the simulator can easily lookup the next hop from get_next_ospf_hop()
    pass

def get_next_ospf_hop(packet, packet_location, topology):
    # Returns next hop (a Node object)
    pass