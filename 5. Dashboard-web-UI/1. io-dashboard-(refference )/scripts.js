window.onload = function () {
    fetchData('outer_sensor', 'outer-sensor-gauge');
    fetchData('inner_sensor', 'inner-sensor-gauge');
    fetchData('board_health', 'board-health-gauge');
};

function fetchData(table, gaugeId) {
    fetch(`fetch_data.php?table=${table}`)
        .then(response => response.json())
        .then(data => {
            renderGauge(data.average, gaugeId);
        });
}

function renderGauge(value, gaugeId) {
    const gauge = document.getElementById(gaugeId);
    gauge.innerHTML = `${value.toFixed(2)}`;
    // Here you can use any JavaScript gauge library to render the gauge more dynamically.
}

function exportData(table) {
    window.location.href = `export_data.php?table=${table}`;
}
