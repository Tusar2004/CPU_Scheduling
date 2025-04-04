from flask import Flask, render_template, request, jsonify
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

app = Flask(__name__)

# Function to generate unique colors for each process
def get_colors(n):
    cmap = plt.get_cmap("tab10")  # Tab10 colormap has 10 unique colors
    return [cmap(i % 10) for i in range(n)]

# First Come First Serve (FCFS)
def fcfs(burst_times):
    execution_order = []
    time = 0
    for i, burst in enumerate(burst_times):
        execution_order.append((i, time, time + burst))
        time += burst
    return execution_order

# Shortest Job First (SJF)
def sjf(burst_times):
    sorted_indices = sorted(range(len(burst_times)), key=lambda k: burst_times[k])
    execution_order = []
    time = 0
    for i in sorted_indices:
        execution_order.append((i, time, time + burst_times[i]))
        time += burst_times[i]
    return execution_order

# Priority Scheduling
def priority_scheduling(burst_times, priorities):
    sorted_indices = sorted(range(len(burst_times)), key=lambda k: priorities[k])
    execution_order = []
    time = 0
    for i in sorted_indices:
        execution_order.append((i, time, time + burst_times[i]))
        time += burst_times[i]
    return execution_order

# Round Robin
def round_robin(burst_times, quantum):
    execution_order = []
    remaining_times = burst_times[:]
    process_queue = list(range(len(burst_times)))
    time = 0

    while process_queue:
        for i in process_queue[:]:
            if remaining_times[i] > quantum:
                execution_order.append((i, time, time + quantum))
                remaining_times[i] -= quantum
                time += quantum
            else:
                execution_order.append((i, time, time + remaining_times[i]))
                time += remaining_times[i]
                process_queue.remove(i)
    
    return execution_order

# Generate execution order graph
def generate_graph(execution_order, num_processes):
    plt.figure(figsize=(10, 5))
    colors = get_colors(num_processes)
    
    for process, start, end in execution_order:
        plt.barh(y=0, width=end - start, left=start, color=colors[process], edgecolor="black", label=f'P{process + 1}')
        plt.text(start + (end - start) / 2, 0, f'P{process + 1}', ha='center', va='center', fontsize=12, color='white', fontweight='bold')
    
    plt.xlabel("Execution Time")
    plt.yticks([])
    plt.title("Process Execution Order")
    
    # Create a custom legend
    handles = [plt.Line2D([0], [0], color=colors[i], lw=4, label=f'P{i + 1}') for i in range(num_processes)]
    plt.legend(handles=handles, loc="upper left", bbox_to_anchor=(1, 1))
    
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.json
    algorithm = data['algorithm']
    burst_times = list(map(int, data['burst_times'].split(',')))
    num_processes = len(burst_times)

    if algorithm == "FCFS":
        execution_order = fcfs(burst_times)
    elif algorithm == "SJF":
        execution_order = sjf(burst_times)
    elif algorithm == "Priority":
        priorities = list(map(int, data['priorities'].split(',')))
        execution_order = priority_scheduling(burst_times, priorities)
    elif algorithm == "Round Robin":
        quantum = int(data['quantum'])
        execution_order = round_robin(burst_times, quantum)
    else:
        return jsonify({"error": "Invalid algorithm"}), 400

    graph_url = generate_graph(execution_order, num_processes)
    return jsonify({"execution_order": execution_order, "graph_url": graph_url})

if __name__ == '__main__':
    app.run(debug=True)
