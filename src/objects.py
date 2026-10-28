# Define network objects and behavior

from collections import deque # Used for more efficient FIFO pops than python's built-in pop()

class Node:
    '''
    Defines functionality for Node class
    add_packet(packet) adds a new packet to the end of self.buffer. 
        Returns True on success and False on failure
    extract_packet() pops and returns the Packet
    '''
    def __init__(self,id,pos_x,pos_y,max_buffer_size):
        self.id = id
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.max_buffer_size = max_buffer_size
        self.buffer = deque() # Double-ended FIFO queue
        self.links = set()

    def __str__(self):
        # Allows you to print() the node
        return (f"Node {self.id}")

    def __repr__(self):
        # Allows you to print() the node inside of a list or call (Like print([node1, node2]))
        return (f"Node {self.id}")
    
    def add_packet(self, packet):
        # Add new packet to the end of the queue
        # Prevents overflowing buffers
        if len(self.buffer) < self.max_buffer_size:
            self.buffer.append(packet)
            return True #Success
        else:
            return False #Failure

    def extract_packet(self):
        if self.buffer:
            # Remove oldest packet from the front and return it
            return self.buffer.popleft()

        return None

    def get_partner_link(self, partner):
        # Given a node and its partner, returns the link
        for link in self.links:
            if link.get_partner(self) == partner:
                return link

    def downlink():
        # This should only be used by satellites connected to a ground station!
        # Note: Implement functionality for 10 Mbps downlink rate using simpy Environment processes
        pass

class Packet:
    '''
    Data structure for network packets

    Attributes:
        id (int or str): A unique identifier for the packet tracking.
        size (in bits)
        state: 0 (Stationary) 1 (In transit)
    '''
    def __init__(self, id, source, destination, creation_time, size=512):
        self.id = id
        self.size = size
        self.state = 0 # Stationary by default
        self.source = source
        self.destination = destination
        self.location = None
        self.creation_time = creation_time
        self.arrival_time = None
        self.forwarding_count = 0

    def __str__(self):
        state_str = "stationary" if self.state == 0 else f"moving from {self.source} to {self.destination}"
        return f"Packet {self.id} : {self.size} bits, state: {state_str}"

    def move_packet(self, src, dest):
        self.source = src
        self.destination = dest
        self.forwarding_count += 1
        self.state = 1
        

class Link:
    '''
    Data structure for a link between two satellites

    Attributes:
        sat1: First satellite in the link
        sat2: Second satellite in the link 
    '''
    def __init__(self, sat1, sat2):
        self.sat1 = sat1
        self.sat2 = sat2

    def __str__(self):
        # Allows you to print() the link
        return f"{self.sat1} <--> {self.sat2}"

    def __repr__(self): 
        # Allows you to print() the link inside of a list or call (Like print([link1, link2]))
        return self.__str__()

    def get_partner(self, sat):
        # Returns the link partner for a given link between a given satellite and its link partner
        if sat == self.sat1:
            return self.sat2
        if sat == self.sat2:
            return self.sat1



    