# CPU Scheduling Algorithm Simulator

![Project Screenshot](https://tusar2004.github.io/CPU_Scheduling/)

## Description
An interactive web application that visualizes and compares different CPU scheduling algorithms with comprehensive metrics. The simulator features a modern, transparent UI that allows the background image to show through, creating an immersive experience.

## Features
- **Six Scheduling Algorithms**:
  - First-Come First-Served (FCFS)
  - Shortest Job First (SJF) - Non-preemptive
  - Shortest Remaining Job First (SJRF) - Preemptive
  - Priority Scheduling - Non-preemptive
  - Priority Scheduling with Aging - Preemptive
  - Round Robin with configurable quantum

- **Interactive Visualization**:
  - Gantt chart showing process execution timeline
  - Ready queue visualization
  - Context switch indicators
  - Color-coded processes for easy tracking

- **Comprehensive Metrics**:
  - Average waiting time
  - Average turnaround time
  - Throughput (processes per unit time)
  - Context switches count
  - Detailed per-process metrics table

- **Customizable UI**:
  - Transparent panels with frosted glass effect
  - Background selector with multiple options
  - Algorithm-specific icons and images
  - Responsive design for all screen sizes

Usage Guide
Adding and Managing Processes
Click "Add Process" to create new processes (default starts with 3 processes)

Edit process details directly in the table:

Arrival Time (must be ≥ 0)

Burst Time (must be ≥ 1)

Priority (used for priority-based algorithms)

Remove processes with "Remove Last" button (minimum 1 process required)

Selecting and Configuring Algorithms
Choose from six available algorithms using either:

The dropdown selector

Visual algorithm cards (click to select)

Configure algorithm-specific parameters:

Time Quantum (for Round Robin, default: 2)

Aging Interval (for Priority with Aging, default: 5)

Running Simulations
Click "Run Simulation" button

View real-time loading indicator

Results appear in three sections:

Performance Metrics: Key statistics at a glance

Gantt Chart: Visual timeline of process execution

Process Metrics Table: Detailed timing information for each process

UI Customization
Change background image using the selector in bottom-right corner

The transparent design adapts to your selected background

Hover over elements for tooltips and additional information

Technology Stack
Frontend:

HTML5, CSS3, JavaScript

Tailwind CSS for styling

Animate.css for animations

Backend:

Python with Flask framework

Matplotlib for Gantt chart generation

Design:

Transparent UI with backdrop-filter

Responsive layout

Color-coded processes

Implementation Details
The simulator implements all scheduling algorithms from scratch in Python:

FCFS: Simple first-in-first-out queue

SJF: Non-preemptive shortest job first

SJRF: Preemptive version using priority queue

Priority: Both preemptive and non-preemptive variants

Round Robin: Circular queue implementation with time slicing

Metrics calculation includes:

Waiting time = Start time - Arrival time

Turnaround time = Finish time - Arrival time

Throughput = Total processes / Total time

Context switches = Number of process changes

Contact: 
For questions or feedback, please contact:

Your Name - @yTusar2004 - tusarg937@gmail.com

Project Link: https://github.com/Tusar2004/cpu-scheduling-simulator


