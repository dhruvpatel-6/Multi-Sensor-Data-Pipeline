import json
import matplotlib.pyplot as plt

def plot_robot_performance():
    try:
        with open("final_flagged_logs.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: Run anomaly_detector.py first!")
        return

    timestamps = [e["timestamp"] for e in data]
    distances = [e["depth_distance"] for e in data]
    # Identify anomalies for the legend
    colors = ['red' if "CRITICAL" in e["status"] else 'blue' for e in data]

    plt.figure(figsize=(12, 6))
    plt.scatter(timestamps, distances, c=colors, label='Sensor Data', s=15)
    
    # Adding professional labels for your portfolio
    plt.title("Robot Telemetry: Depth Sensor vs Time (Anomaly Detection)", fontsize=14)
    plt.xlabel("Time (Seconds)", fontsize=12)
    plt.ylabel("Distance (Meters)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # Simple legend
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], marker='o', color='w', label='Healthy', markerfacecolor='blue', markersize=10),
                       Line2D([0], [0], marker='o', color='w', label='Anomaly (Spike)', markerfacecolor='red', markersize=10)]
    plt.legend(handles=legend_elements)

    plt.savefig("sensor_graph.png")
    print("--- SUCCESS ---")
    print("Graph saved as 'sensor_graph.png'. Open this file to see your results!")
    plt.show()

if __name__ == "__main__":
    plot_robot_performance()    