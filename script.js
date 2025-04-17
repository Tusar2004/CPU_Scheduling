document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const algorithmSelector = document.getElementById("algorithm");
    const quantumContainer = document.getElementById("quantum-container");
    const agingContainer = document.getElementById("aging-container");
    const processTableBody = document.getElementById("process-table-body");
    const resultsTableBody = document.getElementById("results-table-body");
    const queueVisualization = document.getElementById("queue-visualization");
    const runButton = document.getElementById("run-btn");
    const loadingIndicator = document.getElementById("loading-indicator");
    const resultsContainer = document.getElementById("results");
    const toastElement = document.getElementById("toast");
    const toastContent = document.getElementById("toast-content");
    const algorithmCards = document.querySelectorAll(".algorithm-card");

    // Color palette for processes
    const COLOR_PALETTE = [
        '#3b82f6', '#ef4444', '#10b981', '#f59e0b', 
        '#6366f1', '#ec4899', '#14b8a6', '#f97316',
        '#8b5cf6', '#06b6d4'
    ];

    // Process counter
    let processCounter = 1;

    // Initialize with 3 default processes
    for (let i = 0; i < 3; i++) {
        addProcess();
    }

    // Event Listeners
    algorithmSelector.addEventListener("change", updateAlgorithmSettings);
    updateAlgorithmSettings();

    // Algorithm card selection
    algorithmCards.forEach(card => {
        card.addEventListener("click", () => {
            const algo = card.getAttribute("data-algo");
            algorithmSelector.value = algo;
            updateAlgorithmSettings();
            
            // Update card selection UI
            algorithmCards.forEach(c => c.classList.remove("selected"));
            card.classList.add("selected");
        });
    });

    // Functions
    function updateAlgorithmSettings() {
        const algorithm = algorithmSelector.value;
        quantumContainer.classList.toggle("hidden", algorithm !== "RoundRobin");
        agingContainer.classList.toggle("hidden", !algorithm.includes("PriorityP"));

        // Update selected card
        algorithmCards.forEach(card => {
            card.classList.toggle("selected", card.getAttribute("data-algo") === algorithm);
        });
    }

    function addProcess() {
        const newRow = document.createElement("tr");
        newRow.className = "hover:bg-white/90 transition-colors";
        newRow.innerHTML = `
            <td class="px-4 py-2 text-center font-medium">P${processCounter}</td>
            <td class="px-4 py-2"><input type="number" class="w-full p-2 border rounded bg-white/80" value="${processCounter-1}" min="0"></td>
            <td class="px-4 py-2"><input type="number" class="w-full p-2 border rounded bg-white/80" value="${Math.floor(Math.random() * 10) + 1}" min="1"></td>
            <td class="px-4 py-2"><input type="number" class="w-full p-2 border rounded bg-white/80" value="${Math.floor(Math.random() * 5) + 1}" min="1"></td>
        `;
        processTableBody.appendChild(newRow);
        processCounter++;
    }

    function removeProcess() {
        if (processTableBody.children.length > 1) {
            processTableBody.removeChild(processTableBody.lastElementChild);
            processCounter--;
        } else {
            showError("You need at least one process");
        }
    }

    function getProcessData() {
        const processes = [];
        const rows = processTableBody.querySelectorAll("tr");
        
        rows.forEach((row, index) => {
            const cells = row.querySelectorAll("td");
            processes.push({
                pid: index + 1,
                arrival_time: parseInt(cells[1].querySelector("input").value),
                burst_time: parseInt(cells[2].querySelector("input").value),
                priority: parseInt(cells[3].querySelector("input").value)
            });
        });
        
        return processes;
    }

    function showError(message) {
        toastContent.textContent = message;
        toastElement.classList.remove("hidden");
        toastElement.classList.add("animate__fadeInRight");
        toastElement.classList.remove("animate__fadeOutRight");
        
        setTimeout(() => {
            toastElement.classList.add("animate__fadeOutRight");
            setTimeout(() => toastElement.classList.add("hidden"), 300);
        }, 3000);
    }

    function setLoading(isLoading) {
        runButton.disabled = isLoading;
        loadingIndicator.classList.toggle("hidden", !isLoading);
        runButton.innerHTML = isLoading ? 
            `<svg class="animate-spin h-5 w-5 inline mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg> Processing...` : 
            `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
            </svg> Run Simulation`;
    }

    function visualizeQueue(executionOrder) {
        if (!executionOrder || executionOrder.length === 0) {
            queueVisualization.innerHTML = '<p class="text-gray-500 text-center py-8">No queue data available</p>';
            return;
        }

        let html = '<div class="flex flex-col space-y-4">';
        html += '<div class="font-medium text-gray-700">Ready Queue Timeline:</div>';
        
        // Group by time
        const timeMap = {};
        executionOrder.forEach(([pid, start, end]) => {
            if (!timeMap[start]) timeMap[start] = [];
            timeMap[start].push(pid);
        });
        
        // Create timeline
        const times = Object.keys(timeMap).sort((a, b) => a - b);
        times.forEach(time => {
            html += `<div class="flex items-start">
                <div class="w-16 text-sm font-medium text-gray-600">T=${time}</div>
                <div class="flex-1 flex flex-wrap gap-2">`;
            
            timeMap[time].forEach(pid => {
                const colorIndex = (pid-1) % COLOR_PALETTE.length;
                html += `<span class="inline-flex items-center justify-center w-8 h-8 rounded-full text-white font-bold" style="background-color: ${COLOR_PALETTE[colorIndex]}">P${pid}</span>`;
            });
            
            html += `</div></div>`;
        });
        
        html += '</div>';
        queueVisualization.innerHTML = html;
    }

    function updateResultsTable(metrics) {
        let html = '';
        metrics.processes.forEach(proc => {
            html += `
                <tr class="hover:bg-white/90">
                    <td class="px-4 py-2 text-center">P${proc.pid}</td>
                    <td class="px-4 py-2 text-center">${proc.arrival_time}</td>
                    <td class="px-4 py-2 text-center">${proc.burst_time}</td>
                    <td class="px-4 py-2 text-center">${proc.priority}</td>
                    <td class="px-4 py-2 text-center">${proc.start_time}</td>
                    <td class="px-4 py-2 text-center">${proc.finish_time}</td>
                    <td class="px-4 py-2 text-center">${proc.waiting_time}</td>
                    <td class="px-4 py-2 text-center">${proc.turnaround_time}</td>
                </tr>
            `;
        });
        resultsTableBody.innerHTML = html;
    }

    // Background selector functionality
    document.getElementById('bg-toggle').addEventListener('click', function() {
        document.getElementById('bg-options').classList.toggle('hidden');
    });

    document.querySelectorAll('.bg-option').forEach(option => {
        option.addEventListener('click', function() {
            const bgUrl = this.getAttribute('data-bg');
            document.getElementById('main-bg').style.backgroundImage = `url('${bgUrl}')`;
            
            document.querySelectorAll('.bg-option').forEach(opt => {
                opt.classList.remove('selected');
            });
            this.classList.add('selected');
            
            document.getElementById('bg-options').classList.add('hidden');
        });
    });

    // Show welcome tooltip on first hover of process table
    const firstProcessInput = document.querySelector('#process-table-body td input');
    if (firstProcessInput) {
        firstProcessInput.addEventListener('mouseenter', function() {
            showError("Tip: Edit these values to customize your processes");
        }, { once: true });
    }

    // Main simulation function
    window.runSimulation = async () => {
        const algorithm = algorithmSelector.value;
        const processes = getProcessData();
        const quantum = document.getElementById("quantum")?.value;
        const agingInterval = document.getElementById("aging-interval")?.value;
        
        // Validate inputs
        try {
            if (processes.some(p => isNaN(p.arrival_time) || isNaN(p.burst_time) || isNaN(p.priority))) {
                throw new Error("All fields must contain valid numbers");
            }
            
            if (algorithm === "RoundRobin" && (!quantum || quantum <= 0)) {
                throw new Error("Quantum must be a positive number");
            }
            
            if (algorithm.includes("PriorityP") && (!agingInterval || agingInterval <= 0)) {
                throw new Error("Aging interval must be a positive number");
            }
        } catch (err) {
            showError(err.message);
            return;
        }

        // Prepare data
        const data = { 
            algorithm,
            processes,
            ...(algorithm === "RoundRobin" && { quantum }),
            ...(algorithm.includes("PriorityP") && { aging_interval: agingInterval })
        };

        try {
            setLoading(true);
            resultsContainer.classList.add("hidden");
            queueVisualization.innerHTML = '<div class="flex items-center justify-center h-full"><div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div></div>';

            const response = await fetch("/simulate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || "Failed to run simulation");
            }

            if (result.graph_url) {
                // Update metrics
                document.getElementById("avg_waiting").textContent = result.metrics.avg_waiting;
                document.getElementById("avg_turnaround").textContent = result.metrics.avg_turnaround;
                document.getElementById("throughput").textContent = result.metrics.throughput;
                document.getElementById("context_switches").textContent = result.metrics.context_switches;
                document.getElementById("graph").src = `data:image/png;base64,${result.graph_url}`;
                
                // Update tables and visualizations
                updateResultsTable(result.metrics);
                visualizeQueue(result.execution_order);
                
                // Show results
                resultsContainer.classList.remove("hidden");
                resultsContainer.scrollIntoView({ behavior: "smooth", block: "nearest" });
            }
        } catch (err) {
            console.error("Simulation error:", err);
            showError(err.message || "An unexpected error occurred");
            queueVisualization.innerHTML = '<p class="text-gray-500 text-center py-8">Queue visualization failed</p>';
        } finally {
            setLoading(false);
        }
    };

    // Expose functions to global scope
    window.addProcess = addProcess;
    window.removeProcess = removeProcess;
});
