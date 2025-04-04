document.getElementById("algorithm").addEventListener("change", function() {
    let quantumInput = document.getElementById("quantum");
    let quantumLabel = document.getElementById("quantumLabel");
    
    if (this.value === "Round Robin") {
        quantumInput.style.display = "inline";
        quantumLabel.style.display = "inline";
    } else {
        quantumInput.style.display = "none";
        quantumLabel.style.display = "none";
    }
});

async function simulate() {
    let algorithm = document.getElementById("algorithm").value;
    let bursts = document.getElementById("bursts").value.split(",").map(Number);
    let quantum = parseInt(document.getElementById("quantum").value);

    let response = await fetch("/schedule", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ algorithm, bursts, quantum })
    });

    let data = await response.json();
    drawChart(data.order);
}

function drawChart(order) {
    let ctx = document.getElementById("chart").getContext("2d");
    new Chart(ctx, {
        type: "bar",
        data: {
            labels: order.map(p => `P${p}`),
            datasets: [{
                label: "Process Execution Order",
                data: order.map((_, i) => i + 1),
                backgroundColor: "blue"
            }]
        }
    });
}
