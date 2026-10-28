# Generates all 3 types of traffic
from src.objects import Packet


PACKET_SIZE = 512

def bursty():
    
    pass
def poisson():
    pass
def cbr_interval(rate_mbps):  
    packet_size_bytes = PACKET_SIZE * 8
    traffic_rate = rate_mbps * 1000000 # Convert from Mbps to bps
    interval = packet_size_bytes / traffic_rate
    return interval

def generate_cbr(rate_mbps, env, source, destination, buffer):
    print("Beginning cbr generation from ", source, " to ", destination)
    interval = cbr_interval(rate_mbps)
    packet_id = 0
    while True: #Continues until main program stops environment
        yield env.timeout(interval)

        packet_id += 1
        packet = Packet(packet_id, source, destination, env.now)
        #print("Created packet: ", packet, " at time ", env.now)
        yield buffer.put(packet) 
 
