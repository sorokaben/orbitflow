# Coordinates entire simulation
from src.objects import *
from src.topology import *
import simpy

def simulation():
    env = simpy.Environment() # This is what starts our simulated clock
    print("Simulating")
    topology = Topology()

    # This is how, given a specific node, you can get the Link object to its partner:
    node1 = topology.grid[0][0]
    node7 = topology.grid[1][0]
    print(topology)

    # Another way to get a specific node
    node6 = (topology.nodes[6])
    print(node6, "type: ", type(node6))

    topology.print_links()

    # Example
    p = Packet(1, 20)
    print(p)
    p.move_packet(node1, node7)
    print(p)
