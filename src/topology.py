# Build network topology

from src.objects import *

class Topology():
    def __init__(self):
        self.nodes = {}
        self.grid = [[None for x in range(6)] for y in range(6)] # Create a 6x6 2d array

        self.max_buffer_size = 100 # Default 100. Change this to 50 when testing with CBR like the paper does.

        self.build_topology()
        self.link_nodes()

    def __str__(self):
        count = 0
        string = f""
        for row in self.grid:
            for node in row:
                count += 1
                gap = "  " if count < 10 else " "
                string += (f"[{self.nodes[count]}]{gap}")
            return string

    def build_topology(self):
        # Creates the 6x6 36-node topology
        count = 0
        print("Creating topology: ")
        for y in range(6):
            for x in range(6):
                count += 1
                node = Node(count, x, y, self.max_buffer_size)
                node.id = count
                node.pos_x = x
                node.pos_y = y
                self.nodes[count] = node
                self.grid[y][x] = node

                # Print out topology
                gap = "  " if count < 10 else " "
                print(f"[{self.nodes[count]}]", end=gap)

            print()

    def link_nodes(self):
        # Creates link objects between each node, including wrap-around behavior

        link_set = set()
        count = 0
        for y in range(6):
            for x in range(6):
                current_satellite = self.grid[y][x]

                # Calculate which satellites are neighbors
                up = (y - 1) if y > 0 else 5
                down = (y + 1) if y < 5 else 0
                left = (x - 1) if x > 0 else 5
                right = (x + 1) if x < 5 else 0

                # Create the links
                link_up = Link(current_satellite, self.grid[up][x])
                if (self.grid[up][x], current_satellite) in current_satellite.links:
                    pass
                link_down = Link(current_satellite, self.grid[down][x])
                link_left = Link(current_satellite, self.grid[y][left])
                link_right = Link(current_satellite, self.grid[y][right])

                # Assign links
                links = [link_up, link_down, link_left, link_right]
                for link in links:
                    forward_pair = (link.sat1, link.sat2)
                    reverse_pair = (link.sat2, link.sat1)
                    if forward_pair not in link_set and reverse_pair not in link_set: # Dont want duplicate "flipped" links
                        #Only create 1 link per connection, but ensure both nodes have that link inside them!
                        link.sat1.links.add(link)
                        link.sat2.links.add(link)
                        link_set.add(forward_pair)

        self.link_nodes = link_set

    def print_links(self):
        for row in self.grid:
            for node in row:
                print(f"{node} Links: {node.links}")