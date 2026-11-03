from src.simulation import simulation
import csv
import os
from src.simulation import simulation
import pandas as pd
import matplotlib.pyplot as plt

    # env.metrics = {
    #     "packets_created": 0,
    #     "packets_delivered": 0,
    #     "packets_dropped_source": 0,
    #     "packets_dropped_transit": 0,
    #     "routing_failures": 0,
    #     "packets_in_network": 0,
    #     "total_delay": 0,
    #     "total_hops": 0

    # }
# Figure 9 
# Figure 10
# Figure 11

## Figure 9 ##

# 9a - Average end-to-end delay (seconds)
# 9b - Average packet forwardings (hops)
# 9c - Throughput (Mbps)
# 9d - Data Delivery Ratio

def run_experiments():
    rates = [2.00, 2.25, 2.50, 2.75, 3.00, 3.25, 3.50, 3.75, 4.00]
    bursty_ceilings = [3,4,5,6,7,8,9,10,11]
    algorithms = ["ospf", "dhbp"]
    traffic_types = ["cbr", "poisson", "bursty"]
    bursty_count = 0
    for i, rate in enumerate(rates):
        for algorithm in algorithms:
            for traffic_type in traffic_types:
                print(f"Starting simulation on {algorithm} with {traffic_type} traffic at {rate}mbps")
                
                if traffic_type == "bursty":
                    current_test_rate = bursty_ceilings[i]
                else:
                    current_test_rate = rate

                results = simulation(rate_mbps=current_test_rate, algorithm=algorithm, traffic_type=traffic_type)
                delivered = results["packets_delivered"]
                created = results["packets_created"]
                duration = results["simulation_duration"]

                # Checks to prevent divide by 0 error
                avg_delay = (results["total_delay"] / delivered) if delivered > 0 else 0
                avg_hops = (results["total_hops"] / delivered) if delivered > 0 else 0

                throughput_mbps = (delivered * 512 * 8) / duration / 1_000_000
                data_delivered_ratio = (delivered / created) if created > 0 else 0

                file_exists = os.path.isfile("results.csv")

                with open("results.csv", mode="a", newline='') as file:
                    writer = csv.writer(file)
                    if not file_exists:
                        writer.writerow(["Rate (Mbps)", "Routing Mode", "Traffic Type", "Average Delay (s)", "Average Hops","Throughput (mbps)", "Data Delivery Ratio" ])

                    writer.writerow([current_test_rate, algorithm, traffic_type, f"{avg_delay:.4f}", f"{avg_hops:.4f}", f"{throughput_mbps:.4f}", f"{data_delivered_ratio:.4f}"])
                print(f"Finished simulation on {algorithm} with {traffic_type} traffic at {rate}mbps")

def plot_metrics(results, traffic_type):

    # Display CBR
    data = results[results["Traffic Type"] == traffic_type]
    ospf = data[data["Routing Mode"] == "ospf"]
    dhbp = data[data["Routing Mode"] == "dhbp"]

    x_label = "Max Burst Rate (Mbps)" if traffic_type == "bursty" else "Rate (Mbps)"
    figure, axis = plt.subplots(2,2, figsize=(12,10))

    # (a) Average Delay
    axis[0,0].plot(ospf["Rate (Mbps)"], ospf["Average Delay (s)"], label="OSPF", marker='o', linestyle='--')
    axis[0,0].plot(dhbp["Rate (Mbps)"], dhbp["Average Delay (s)"], label="DHBP", marker='s', linestyle='-', mfc='none', linewidth=1.5, alpha=0.8)
    axis[0,0].set_title("(a) Average Delay")
    axis[0,0].set_xlabel(x_label)
    axis[0,0].set_ylabel("Delay (s)")
    axis[0,0].legend()
    if traffic_type == "cbr":
            axis[0,0].set_ylim(0.0435,0.0455)
    # (b) Average Forwarding Count
    axis[0,1].plot(ospf["Rate (Mbps)"], ospf["Average Hops"], label="OSPF", marker='o', linestyle='--')
    axis[0,1].plot(dhbp["Rate (Mbps)"], dhbp["Average Hops"], label="DHBP", marker='s', linestyle='-', mfc='none', linewidth=1.5, alpha=0.8)
    axis[0,1].set_title("(b) Average Forwarding Count")
    axis[0,1].set_xlabel(x_label)
    axis[0,1].set_ylabel("Hops")
    if traffic_type == "cbr":
        axis[0,1].set_ylim(5.98,6.02)
    axis[0,1].legend()
    # (c) Throughput
    axis[1,0].plot(ospf["Rate (Mbps)"], ospf["Throughput (mbps)"], label="OSPF", marker='o', linestyle='--')
    axis[1,0].plot(dhbp["Rate (Mbps)"], dhbp["Throughput (mbps)"], label="DHBP", marker='s', linestyle='-', mfc='none', linewidth=1.5, alpha=0.8)
    axis[1,0].set_title("(c) Throughput")
    axis[1,0].set_xlabel(x_label)
    axis[1,0].set_ylabel("Throughput (Mbps)")
    axis[1,0].legend()

    # (d) Delivery Ratio
    axis[1,1].plot(ospf["Rate (Mbps)"], ospf["Data Delivery Ratio"], label="OSPF", marker='o', linestyle='--')
    axis[1,1].plot(dhbp["Rate (Mbps)"], dhbp["Data Delivery Ratio"], label="DHBP", marker='s', linestyle='-', mfc='none', linewidth=1.5, alpha=0.8)
    axis[1,1].set_title("(d) Delivery Ratio")
    axis[1,1].set_xlabel(x_label)
    axis[1,1].set_ylabel("Ratio")
    axis[1,1].legend()
    if traffic_type != "bursty":
        axis[1,1].set_ylim(0.9985,1.0005)

    plt.tight_layout()
    plt.show()

def display_results():
    results = pd.read_csv("results.csv")
    for traffic_type in ["cbr", "poisson", "bursty"]:
        plot_metrics(results, traffic_type)
