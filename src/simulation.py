# Coordinates entire simulation
from src.objects import *
from src.topology import *
from src.traffic import *
from src.simulation import *
from src.dhbp import get_next_dhbp_hop
from src.ospf import get_next_ospf_hop
import traceback

import simpy

BANDWIDTH_BPS = 10_000_000

def transfer_packet(env, packet: Packet, delay, next_hop):

    #print(f"{env.now:.3f}: Packet {packet.id} starts")

    packet.state = 1

    yield env.timeout(delay)

    packet.location = next_hop

    # Drop Packet if there's no room
    if len(next_hop.buffer.items) < next_hop.buffer.capacity:
        yield next_hop.buffer.put(packet)
    else:
        #print(f"[{env.now:.3}] DROP: Packet {packet.id}. Dropped at Node {next_hop.id}. Reason: Buffer Full")
        env.metrics["packets_dropped_transit"] += 1

    packet.state = 0 # Means the packet isn't moving


def simulation(rate_mbps):
    env = simpy.Environment() # This is what starts our simulated clock
    env.metrics = {
        "packets_created": 0,
        "packets_delivered": 0,
        "packets_dropped_source": 0,
        "packets_dropped_transit": 0,
        "routing_failures": 0

    }
    packet_buffer = simpy.Store(env)
    print("Simulating")

    topology = Topology(env)
    print(topology.nodes[0])
    pair1_source = topology.nodes[0]
    pair1_dest = topology.nodes[21] # Furthest from node 0 because we account for wrap-around

    pair2_source = topology.nodes[8]
    pair2_dest = topology.nodes[29] # Furthest from node 8 because we account for wrap-around

    routing_mode_choice = ""

    while routing_mode_choice not in ["ospf", "dhbp"]:
        routing_mode_input = (input("Welcome! Please choose an option: \n 1 : OSPF \n 2 : DHBP \n>>>"))
        if routing_mode_input == "1" or routing_mode_input.lower() == "ospf":
            routing_mode_choice = "ospf"
        elif routing_mode_input == "2" or routing_mode_input.lower() == "dhbp":
            routing_mode_choice = "dhbp"
        else:
            print("Please enter a valid selection.")

    traffic_type_choice = ""

    while traffic_type_choice not in ["cbr", "poisson", "bursty"]:
        traffic_type_input = (input("Welcome! Please choose an option: \n 1 : CBR \n 2 : Poisson \n 3 : BURSTY \n >>>"))
        if traffic_type_input == "1" or traffic_type_input.lower() == "cbr":
            traffic_type_choice = "cbr"
        elif traffic_type_input == "2" or traffic_type_input.lower() == "poisson":
            traffic_type_choice = "poisson"
        elif traffic_type_input == "3" or traffic_type_input.lower() == "bursty":
            traffic_type_choice = "bursty"
        else:
            print("Please enter a valid selection.")


    for node in topology.nodes.values():
        env.process(node_transmitter(env, node, topology, bandwidth_bps=BANDWIDTH_BPS, routing_mode=routing_mode_choice))

    print("Time to generate...")
    # No need for env process since generate_traffic does that based off the selected traffic type
    generate_traffic(traffic_type_choice, rate_mbps, env, pair1_source, pair1_dest) 
    #generate_traffic(traffic_type_choice, rate_mbps, env, pair2_source, pair2_dest) 
    
    try:  
        env.run(until=1) # TODO: CHANGE BACK TO 100

        print(f"Total Created: {env.metrics['packets_created']}")
        print(f"Total Delivered: {env.metrics['packets_delivered']}")
        print(f"Total Dropped: {env.metrics['packets_dropped_transit'] + env.metrics['packets_dropped_source']}")
    except Exception as e:
        print("\n" + "="*50)
        print("FOUND THE HIDDEN CRASH DETAILS:")
        print("="*50)
        # This extracts the actual background generator crash details
        traceback.print_exception(type(e), e, e.__traceback__)
        print("="*50 + "\n")
        raise e

def node_transmitter(env, node, topology, bandwidth_bps, routing_mode):
    '''
    Runs continuously for a specific node, pulling from its personal buffer
    '''
    while True:
        # Wait for a packet to arrive to a specific node
        packet: Packet = yield node.buffer.get()

        # Check if it has reached final destination
        if packet.location == packet.destination:
            env.metrics["packets_delivered"] += 1
            #print(f"[{env.now:.3f}] Packet {packet.id} reached its destination of {packet.destination}")
            continue
        # Calculate Delays
        packet_size_bits = packet.size
        transmission_time = packet_size_bits / bandwidth_bps
        yield env.timeout(transmission_time) # Wait this amount of time then return to this function

        propagation_delay = 0.00658 + transmission_time

        # Route and forward
        next_hop = None
        if routing_mode == "dhbp":
            next_hop = get_next_dhbp_hop(packet, node, topology)
        elif routing_mode == "ospf":
            next_hop = get_next_ospf_hop(packet, node, topology)

        if next_hop is None:
            print(f"[{env.now:.3}] DROP: Packet {packet.id}. Dropped at Node {node.id}. Reason: No Route To Destination")
            env.metrics["routing_failures"] += 1
            continue


        #print(f"[{env.now:.3f}] Packet {packet.id} forwarded from {node.id} to {next_hop.id}")

        env.process(transfer_packet(env, packet, propagation_delay, next_hop))


        