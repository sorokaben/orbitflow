# Coordinates entire simulation
from src.objects import *
from src.topology import *
from src.traffic import *
from src.simulation import *
import simpy

def travel(env, packet_id, delay):
    print(f"{env.now:.3f}: Packet {packet_id} starts")

    yield env.timeout(delay)

    print(f"{env.now:.3f}: Packet {packet_id} arrives")

def simulation(rate_mbps):
    env = simpy.Environment() # This is what starts our simulated clock
    packet_buffer = simpy.Store(env)
    print("Simulating")

    topology = Topology()
    pair1_source = topology.nodes[1]
    pair1_dest = topology.nodes[22] # Furthest from node 1 because we account for wrap-around

    pair2_source = topology.nodes[6]
    pair2_dest = topology.nodes[21] # Furthest from node 6 because we account for wrap-around

    print("Time to generate...")
    env.process(generate_cbr(rate_mbps,env,pair1_source, pair1_dest, packet_buffer))
    env.process(generate_cbr(rate_mbps,env,pair2_source, pair2_dest, packet_buffer))

    env.process(packet_transmitter(env, packet_buffer, bandwidth_bps=10_000_000)) # 10 Mbps is the paper's specified bandwidth
    env.run(until=100.0) # 

def packet_transmitter(env, buffer, bandwidth_bps):
  '''
  This runs simultaneuously along the rest of the program
  '''
  while True: # Infinite loop that is cut off when env.run's until reaches 100

    # 1. Wait here until ANY packet shows up in the shared buffer
    packet = yield buffer.get()

    print(
        f"[{env.now:.3f}] Transmitting Packet {packet.id} from"
        f" {packet.source} to {packet.destination}"
    )

    # 2. Calculate Transmission Delay (Serialization delay based on size)
    # Assuming PACKET_SIZE is in bytes
    packet_size_bits = 512 * 8
    transmission_time = packet_size_bits / bandwidth_bps
    yield env.timeout(transmission_time)

    # 3. Handle routing / space propagation delay
    # (You can check packet.destination here to calculate distance/delay!)
    propagation_delay = 0.020  # e.g., 20ms satellite hop
    yield env.timeout(propagation_delay)

    print(f"[{env.now:.3f}] Packet {packet.id} successfully delivered!")


    ''' All tests
    print(t)
        #env.process(travel(env, "A", 0.007))
        
    
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
        p = Packet(1, 20, 20)
        print(p)
        p.move_packet(node1, node7)
        print(p)
    
    '''
    