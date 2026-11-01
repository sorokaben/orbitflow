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

    packet.move_packet(next_hop)

    packet.state = 0 # Means the packet isn't moving

    yield next_hop.buffer.put(packet)

def simulation(rate_mbps):
    env = simpy.Environment() # This is what starts our simulated clock
    packet_buffer = simpy.Store(env)
    print("Simulating")

    topology = Topology(env)
    print(topology.nodes[0])
    pair1_source = topology.nodes[0]
    pair1_dest = topology.nodes[21] # Furthest from node 1 because we account for wrap-around

    pair2_source = topology.nodes[5]
    pair2_dest = topology.nodes[20] # Furthest from node 6 because we account for wrap-around

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
    generate_traffic(traffic_type_choice, rate_mbps, env, pair2_source, pair2_dest) 
    
    try:  
        env.run(until=100.0) # 
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
            #print(f"[{env.now:.3f}] Packet {packet.id} reached final destination {packet.destination}!")
            continue

        # Calculate Delays
        packet_size_bits = packet.size
        transmission_time = packet_size_bits / bandwidth_bps
        yield env.timeout(transmission_time) # Wait this amount of time then return to this function

        propagation_delay = 0.00658 + transmission_time

        # Route and forward
        next_hop = None
        if routing_mode == "dhbp":
            next_hop = get_next_dhbp_hop(packet, packet.location, topology)
        elif routing_mode == "ospf":
            next_hop = get_next_ospf_hop(packet, packet.location, topology)

        #print(f"[{env.now:.3f}] Packet {packet.id} forwarded from {node.id} to {next_hop.id}")

        env.process(transfer_packet(env, packet, propagation_delay, next_hop))

# def packet_transmitter(env, buffer, topology, bandwidth_bps, routing_mode="ospf"):
#   '''
#   This runs simultaneuously along the rest of the program
#   '''
#   while True: # Infinite loop that is cut off when env.run's until reaches 100

#     # Wait here until ANY packet shows up in the shared buffer
#     packet: Packet = yield buffer.get()

#     # 3. Handle routing 


#     # Calculate Transmission Delay


#     propagation_delay = 0.00658 + transmission_time

#     if routing_mode == "dhbp":
#         next_hop = get_next_dhbp_hop(packet, packet.location, topology)
#     elif routing_mode == "ospf":
#         next_hop = get_next_ospf_hop(packet, packet.location, topology)

#     if packet.location == packet.destination:
#         print(f"[{env.now:.3f}] Packet {packet.id} reached final destination {packet.destination}!")
#     else:
#         print(f"[{env.now:.3f}] Packet {packet.id} (Dest: {packet.destination}) forwarded to neighbor {next_hop} from {packet.location}")

#         yield env.process(transfer_packet(env, packet, propagation_delay, next_hop))
#         yield buffer.put(packet)

        