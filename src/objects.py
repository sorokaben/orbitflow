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
        self.links = []

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
            # Remove oldest item from the front and return it
            return self.buffer.popleft()

        return None

class Packet:
    def __init__(self, id, size):
        self.id = id
        self.size = size

class Link:
    def __init__(self, sat1, sat2):
        self.sat1 = sat1
        self.sat2 = sat2

    def get_partner(self, sat):
        if sat == self.sat1:
            return self.sat2
        if sat == self.sat2:
            return self.sat1

    