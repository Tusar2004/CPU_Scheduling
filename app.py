from flask import Flask, render_template, request, jsonify # type: ignore
import matplotlib.pyplot as plt # type: ignore
import io
import base64
from functools import wraps
from collections import deque
import heapq

app = Flask(__name__)

COLOR_PALETTE = [
    '#3b82f6', '#ef4444', '#10b981', '#f59e0b', 
    '#6366f1', '#ec4899', '#14b8a6', '#f97316',
    '#8b5cf6', '#06b6d4'
]

def handle_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            app.logger.error(f"Unexpected error: {str(e)}")
            return jsonify({"error": "An unexpected error occurred"}), 500
    return wrapper

def validate_processes(processes):
    if not processes:
        raise ValueError("At least one process is required")
    
    for p in processes:
        if p['burst_time'] <= 0:
            raise ValueError("Burst times must be positive numbers")
        if p['arrival_time'] < 0:
            raise ValueError("Arrival times cannot be negative")
    
    return processes

def get_process_colors(n):
    return [COLOR_PALETTE[i % len(COLOR_PALETTE)] for i in range(n)]

def calculate_metrics(processes, exec_order):
    metrics = {
        'processes': [],
        'avg_waiting': 0,
        'avg_turnaround': 0,
        'throughput': 0,
        'context_switches': 0
    }
    
    # Initialize process metrics
    for p in processes:
        metrics['processes'].append({
            'pid': p['pid'],
            'arrival_time': p['arrival_time'],
            'burst_time': p['burst_time'],
            'priority': p.get('priority', 0),
            'start_time': -1,
            'finish_time': -1,
            'waiting_time': 0,
            'turnaround_time': 0
        })
    
    # Calculate start and finish times
    for i, (pid, start, end) in enumerate(exec_order):
        proc = next(p for p in metrics['processes'] if p['pid'] == pid)
        if proc['start_time'] == -1 or start < proc['start_time']:
            proc['start_time'] = start
        if end > proc['finish_time']:
            proc['finish_time'] = end
        
        # Count context switches (except for first and consecutive same-process executions)
        if i > 0 and exec_order[i-1][0] != pid:
            metrics['context_switches'] += 1
    
    # Calculate waiting and turnaround times
    for proc in metrics['processes']:
        proc['waiting_time'] = proc['start_time'] - proc['arrival_time']
        proc['turnaround_time'] = proc['finish_time'] - proc['arrival_time']
    
    # Calculate averages
    metrics['avg_waiting'] = round(sum(p['waiting_time'] for p in metrics['processes']) / len(metrics['processes']), 2)
    metrics['avg_turnaround'] = round(sum(p['turnaround_time'] for p in metrics['processes']) / len(metrics['processes']), 2)
    
    # Calculate throughput (processes per unit time)
    total_time = max(p['finish_time'] for p in metrics['processes']) if metrics['processes'] else 0
    metrics['throughput'] = round(len(metrics['processes']) / total_time, 2) if total_time > 0 else 0
    
    return metrics

def fcfs(processes):
    processes_sorted = sorted(processes, key=lambda x: x['arrival_time'])
    time = 0
    execution_order = []
    
    for p in processes_sorted:
        if time < p['arrival_time']:
            time = p['arrival_time']
        execution_order.append((p['pid'], time, time + p['burst_time']))
        time += p['burst_time']
    
    return execution_order

def sjf(processes, preemptive=False):
    if not preemptive:
        # Non-preemptive SJF
        processes_sorted = sorted(processes, key=lambda x: (x['burst_time'], x['arrival_time']))
        return fcfs(processes_sorted)
    else:
        # Preemptive SJF (SJRF)
        time = 0
        execution_order = []
        remaining_time = {p['pid']: p['burst_time'] for p in processes}
        arrived = [p for p in processes if p['arrival_time'] <= time]
        heap = [(p['burst_time'], p['pid'], p['arrival_time']) for p in arrived]
        heapq.heapify(heap)
        
        while heap:
            burst, pid, arrival = heapq.heappop(heap)
            if remaining_time[pid] == burst:  # First time this process is selected
                start_time = max(time, arrival)
                if time < start_time:
                    time = start_time
            
            # Execute for 1 unit (preemptive)
            execution_order.append((pid, time, time + 1))
            remaining_time[pid] -= 1
            time += 1
            
            # Check for new arrivals
            new_arrivals = [p for p in processes if p['arrival_time'] <= time and 
                          p['arrival_time'] > time - 1 and 
                          remaining_time[p['pid']] > 0]
            
            # Push back current process if not finished
            if remaining_time[pid] > 0:
                heapq.heappush(heap, (remaining_time[pid], pid, arrival))
            
            # Add new arrivals
            for p in new_arrivals:
                heapq.heappush(heap, (remaining_time[p['pid']], p['pid'], p['arrival_time']))
        
        return execution_order

def priority_scheduling(processes, preemptive=False, aging_interval=5):
    if not preemptive:
        # Non-preemptive Priority
        processes_sorted = sorted(processes, key=lambda x: (x.get('priority', 0), x['arrival_time']))
        return fcfs(processes_sorted)
    else:
        # Preemptive Priority with Aging
        time = 0
        execution_order = []
        remaining_time = {p['pid']: p['burst_time'] for p in processes}
        priority = {p['pid']: p.get('priority', 0) for p in processes}
        last_aged = {p['pid']: 0 for p in processes}
        
        arrived = [p for p in processes if p['arrival_time'] <= time]
        heap = [(priority[p['pid']], p['pid'], p['arrival_time']) for p in arrived]
        heapq.heapify(heap)
        
        while heap:
            prio, pid, arrival = heapq.heappop(heap)
            if remaining_time[pid] == processes[pid-1]['burst_time']:  # First time selected
                start_time = max(time, arrival)
                if time < start_time:
                    time = start_time
            
            # Apply aging
            if time - last_aged[pid] >= aging_interval:
                priority[pid] = max(0, priority[pid] - 1)
                last_aged[pid] = time
            
            # Execute for 1 unit (preemptive)
            execution_order.append((pid, time, time + 1))
            remaining_time[pid] -= 1
            time += 1
            
            # Check for new arrivals
            new_arrivals = [p for p in processes if p['arrival_time'] <= time and 
                          p['arrival_time'] > time - 1 and 
                          remaining_time[p['pid']] > 0]
            
            # Push back current process if not finished
            if remaining_time[pid] > 0:
                heapq.heappush(heap, (priority[pid], pid, arrival))
            
            # Add new arrivals
            for p in new_arrivals:
                heapq.heappush(heap, (priority[p['pid']], p['pid'], p['arrival_time']))
        
        return execution_order

def round_robin(processes, quantum):
    time = 0
    execution_order = []
    remaining_time = {p['pid']: p['burst_time'] for p in processes}
    queue = deque()
    processes_sorted = sorted(processes, key=lambda x: x['arrival_time'])
    next_process = 0
    
    while True:
        # Add arriving processes to the queue
        while next_process < len(processes_sorted) and processes_sorted[next_process]['arrival_time'] <= time:
            queue.append(processes_sorted[next_process]['pid'])
            next_process += 1
        
        if not queue:
            if next_process < len(processes_sorted):
                time = processes_sorted[next_process]['arrival_time']
                continue
            else:
                break
        
        current_pid = queue.popleft()
        start_time = time
        
        # Execute for quantum or remaining time, whichever is smaller
        exec_time = min(quantum, remaining_time[current_pid])
        execution_order.append((current_pid, time, time + exec_time))
        time += exec_time
        remaining_time[current_pid] -= exec_time
        
        # Add arriving processes during this execution
        while next_process < len(processes_sorted) and processes_sorted[next_process]['arrival_time'] < time:
            queue.append(processes_sorted[next_process]['pid'])
            next_process += 1
        
        # If process isn't finished, add it back to the queue
        if remaining_time[current_pid] > 0:
            queue.append(current_pid)
    
    return execution_order

def generate_gantt_chart(execution_order, num_processes):
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(14, 6))
    
    colors = get_process_colors(num_processes)
    process_labels = [f'P{i+1}' for i in range(num_processes)]
    
    # Track context switches
    context_switches = []
    for i in range(1, len(execution_order)):
        if execution_order[i][0] != execution_order[i-1][0]:
            context_switches.append(execution_order[i][1])
    
    # Plot execution bars
    for process, start, end in execution_order:
        duration = end - start
        ax.barh(y=process_labels[process-1], width=duration, left=start, 
                color=colors[process-1], edgecolor='black', alpha=0.8, height=0.6)
        ax.text(start + duration/2, process_labels[process-1], f'{duration}',
                ha='center', va='center', color='white', fontweight='bold', fontsize=10)
    
    # Mark context switches
    for switch_time in context_switches:
        ax.axvline(x=switch_time, color='red', linestyle='--', alpha=0.7, linewidth=1)
        ax.text(switch_time, num_processes-0.5, 'CS', color='red', fontsize=8, ha='center')
    
    ax.set_xlabel('Time Units', fontweight='bold', fontsize=12)
    ax.set_ylabel('Processes', fontweight='bold', fontsize=12)
    ax.set_title('CPU Scheduling Timeline (Context switches marked with red dashed lines)', fontweight='bold', fontsize=14, pad=20)
    ax.grid(True, axis='x', linestyle='--', alpha=0.7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', transparent=False)
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
@handle_errors
def simulate():
    data = request.json
    algorithm = data.get('algorithm')
    processes = data.get('processes', [])
    quantum = int(data.get('quantum', 2)) if data.get('quantum') else 2
    aging_interval = int(data.get('aging_interval', 5)) if data.get('aging_interval') else 5
    
    processes = validate_processes(processes)
    num_processes = len(processes)
    
    if algorithm == "FCFS":
        exec_order = fcfs(processes)
    elif algorithm == "SJF":
        exec_order = sjf(processes)
    elif algorithm == "SJRF":
        exec_order = sjf(processes, preemptive=True)
    elif algorithm == "Priority":
        exec_order = priority_scheduling(processes)
    elif algorithm == "PriorityP":
        exec_order = priority_scheduling(processes, preemptive=True, aging_interval=aging_interval)
    elif algorithm == "RoundRobin":
        exec_order = round_robin(processes, quantum)
    else:
        raise ValueError("Invalid algorithm selected")
    
    metrics = calculate_metrics(processes, exec_order)
    chart_url = generate_gantt_chart(exec_order, num_processes)
    
    return jsonify({
        "execution_order": exec_order,
        "graph_url": chart_url,
        "metrics": metrics
    })

if __name__ == '__main__':
    app.run(debug=True)
