# Coordinates entire simulation
from src.objects import *
from src.topology import *
from src.traffic import *
from src.simulation import *
from src.dhbp import get_next_dhbp_hop
from src.ospf import get_next_ospf_hop
import traceback

import simpy

def transfer_packet(env, packet: Packet, delay, destination):

    #print(f"{env.now:.3f}: Packet {packet.id} starts")

    packet.state = 1

    yield env.timeout(delay)

    packet.move_packet(packet.location, destination)


    packet.state = 0 # Means the packet isn't moving

    #print(f"{env.now:.3f}: Packet {packet.id} arrives")

def simulation(rate_mbps):
    env = simpy.Environment() # This is what starts our simulated clock
    packet_buffer = simpy.Store(env)
    print("Simulating")

    topology = Topology()
    print(topology.nodes[0])
    pair1_source = topology.nodes[0]
    pair1_dest = topology.nodes[21] # Furthest from node 1 because we account for wrap-around

    pair2_source = topology.nodes[5]
    pair2_dest = topology.nodes[20] # Furthest from node 6 because we account for wrap-around


    # TODO FOR DANIEL: Have your Dijkstra's build a routing table first so that your other function can refer to it!

    print("Time to generate...")
    env.process(generate_cbr(rate_mbps,env,pair1_source, pair1_dest, packet_buffer)) 
    #env.process(generate_cbr(rate_mbps,env,pair2_source, pair2_dest, packet_buffer)) TODO: UNCOMMENT THIS!!!!!
    # 10 Mbps is the paper's specified bandwidth    
    env.process(packet_transmitter(env, packet_buffer, topology, bandwidth_bps=10_000_000, routing_mode="ospf"))
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

def packet_transmitter(env, buffer, topology, bandwidth_bps, routing_mode="ospf"):
  '''
  This runs simultaneuously along the rest of the program
  '''
  while True: # Infinite loop that is cut off when env.run's until reaches 100

    # Wait here until ANY packet shows up in the shared buffer
    packet: Packet = yield buffer.get()

    # 3. Handle routing 


    # Calculate Transmission Delay
    packet_size_bits = 512 * 8
    transmission_time = packet_size_bits / bandwidth_bps
    yield env.timeout(transmission_time) # Wait this amount of time then return to this function

    propagation_delay = 0.00658 + transmission_time

    if routing_mode == "dhbp":
        next_hop = get_next_dhbp_hop(packet, packet.location, topology)
    elif routing_mode == "ospf":
        next_hop = get_next_ospf_hop(packet, packet.location, topology)

    if packet.location == packet.destination:
        print(f"[{env.now:.3f}] Packet {packet.id} reached final destination {packet.destination}!")
    else:
        print(f"[{env.now:.3f}] Packet {packet.id} (Dest: {packet.destination}) forwarded to neighbor {next_hop} from {packet.location}")

        yield env.process(transfer_packet(env, packet, propagation_delay, next_hop))
        yield buffer.put(packet)

        