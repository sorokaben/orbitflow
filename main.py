# Program entry point and testing hub
from src.simulation import simulation
from src.run_tests import run_experiments, display_results

def main():
    run_experiments()
    display_results()

if __name__ == "__main__":
    main()