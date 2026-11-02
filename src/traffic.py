# Generates all 3 types of traffic
from src.objects import Packet
import random

PACKET_SIZE = 512
packet_id = 0

def inject_packet(env, packet, node):
        env.metrics["packets_created"] += 1
        env.metrics["packets_in_network"] += 1

        if len(node.buffer.items) < node.buffer.capacity:
            # print(f"{len(node.buffer.items)} items in node {node.id}'s buffer")
            yield node.buffer.put(packet)
            if len(node.buffer.items) > node.peak_buffer:
                node.peak_buffer = len(node.buffer.items)
            #print("Put packet")
        else:
            #print(f"[{env.now:.3}] DROP: Packet {packet.id}. Dropped at Node {node.id}. Reason: Buffer Full with {len(node.buffer.items)}items")
            env.metrics["packets_dropped_source"] += 1
            env.metrics["packets_in_network"] -= 1


def generate_bursty(rate_mbps, env, source, destination):
    # Generates CBR ocassionally and bursty at other times, meaning more traffic
    state = "NORMAL"
    global packet_id

    while True: #Continues until main program stops environment

        # Set traffic rate based on current state
        if state == "NORMAL":
            current_rate = 2.0 # Standard CBR traffic load
        elif state == "BURSTY":
            # Get a random float between 3 and 11. All numbers have equal probability
            current_rate = rate_mbps

        interval = cbr_interval(current_rate)

        # How long to stay in the state; average of 1 second
        state_duration = random.expovariate(1.0)
        state_end_time = env.now + state_duration

        # Generate packets until the state timer runs out

        while env.now < state_end_time:
            yield env.timeout(interval)
            packet_id += 1
            packet = Packet(packet_id, source, destination, env.now)
            packet.location = source 
            #print(f"[{env.now:.3f}] Packet {packet.id} created")
            yield from inject_packet(env, packet, source)

        # Timer runs out: Swap state
        state = "BURSTY" if state == "NORMAL" else "NORMAL"

    
def generate_poisson(rate_mbps, env, source, destination):
    # Like CBR, but packets arrive at random times
    packets_per_second = (rate_mbps * 1_000_000) / (PACKET_SIZE * 8)
    global packet_id

    while True: #Continues until main program stops environment
        interval = random.expovariate(packets_per_second)
        yield env.timeout(interval)
        packet_id += 1
        packet = Packet(packet_id, source, destination, env.now)
        packet.location = source
        #print(f"[{env.now:.6f}] Packet {packet.id} created")
        yield from inject_packet(env, packet, source)


    

def cbr_interval(rate_mbps):  
    packet_size_bytes = PACKET_SIZE * 8
    traffic_rate = rate_mbps * 1000000 # Convert from Mbps to bps
    interval = packet_size_bytes / traffic_rate
    return interval

def generate_cbr(rate_mbps, env, source, destination):
    interval = cbr_interval(rate_mbps)
    global packet_id
    packets_sent = 0
    while True: #Continues until main program stops environment
        yield env.timeout(interval)
        packet_id += 1
        packet = Packet(packet_id, source, destination, env.now)
        packet.location = source
        #print(f"[{env.now:.3f}] Packet {packet.id} created")
        yield from inject_packet(env, packet, source)

        # TODO: COMMENT THIS NEXT BIT OUT
        #packets_sent += 1
        #if packets_sent > 0:
        #    return

def generate_traffic(traffic_type, rate_mbps, env, source, destination):
    if traffic_type == "cbr":
        #print(f"Starting CBR traffic from {source.id} to {destination.id}")
        env.process(generate_cbr(rate_mbps,env,source,destination))
    elif traffic_type == "poisson":
        #print(f"Starting Poisson traffic from {source.id} to {destination.id}")
        env.process(generate_poisson(rate_mbps,env,source,destination))
    elif traffic_type == "bursty":
        #print(f"Starting Bursty traffic from {source.id} to {destination.id}")
        env.process(generate_bursty(rate_mbps,env,source,destination))
    else:
        print("Error in traffic type")
        quit()
 
