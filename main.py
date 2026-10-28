# Program entry point and testing hub
from src.simulation import simulation

def main():
    print("Entered main")
    rate_mbps = 2
    simulation(rate_mbps)

if __name__ == "__main__":
    main()