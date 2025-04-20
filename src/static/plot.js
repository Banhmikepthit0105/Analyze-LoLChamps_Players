async function generatePlot() {
    const userInput = document.getElementById('userInput').value;
    const provider = document.getElementById('provider').value;
    const dataset = document.getElementById('dataset').value;

    const response = await fetch('/api/plot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_input: userInput,
            provider: provider,
            dataset: dataset
        })
    });

    const data = await response.json();
    if (data.error) {
        alert('Lỗi: ' + data.error);
        return;
    }

    const plotDiv = document.getElementById('plot');
    Plotly.newPlot(plotDiv, data.plot.data, data.plot.layout);
}