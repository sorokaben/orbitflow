# DHBP Routing Logic

import random
from src.objects import *
from src.topology import *

def get_next_dhbp_hop(packet, packet_location, topology):
    # Returns next hop (a Node object)
    # TODO: This rudimentary_test is for testing only. Delete it when you actually implement this!
    print("Hi!")
    #return(rudimentary_test(packet, packet_location, topology))
    pass

def rudimentary_test(packet, packet_location, topology: Topology):
    # random_link = random.choice(list(packet_location.links.get_partner()))
    print("Hi test")