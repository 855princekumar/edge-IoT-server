document.addEventListener("DOMContentLoaded", function () {
    const ipInput = document.getElementById('ipInput');
    const addIpBtn = document.getElementById('addIpBtn');
    const nodeContainer = document.getElementById('nodeContainer');

    // Load saved IPs from localStorage
    let ipList = JSON.parse(localStorage.getItem('ipList')) || [];

    // Function to save IPs to localStorage
    const saveIps = () => {
        localStorage.setItem('ipList', JSON.stringify(ipList));
    };

    // Function to render nodes
    const renderNodes = () => {
        nodeContainer.innerHTML = ''; // Clear the container
        ipList.forEach(ip => {
            const nodeDiv = document.createElement('div');
            nodeDiv.classList.add('node');

            nodeDiv.innerHTML = `
                <h3>Node IP: ${ip}</h3>
                <button class="show-data-btn" data-ip="${ip}">Show Data</button>
                <button class="delete-node-btn" data-ip="${ip}">Delete</button>
                <div class="data-display" id="data-${ip}"></div>
                <div class="timer" id="timer-${ip}">Fetching data in 5s...</div>
            `;

            nodeContainer.appendChild(nodeDiv);
        });
    };

    // Add IP button event listener
    addIpBtn.addEventListener('click', function () {
        const ip = ipInput.value.trim();

        if (ip && !ipList.includes(ip)) {
            ipList.push(ip);
            saveIps();
            renderNodes();
            ipInput.value = ''; // Clear the input field
        }
    });

    // Function to start the countdown timer and fetch data after 5 seconds
    const startTimerAndFetchData = (ip) => {
        let countdown = 5; // Countdown starts at 5 seconds
        const timerElement = document.getElementById(`timer-${ip}`);
        const dataDisplay = document.getElementById(`data-${ip}`);

        const countdownInterval = setInterval(() => {
            timerElement.textContent = `Fetching data in ${countdown}s...`;
            countdown--;

            if (countdown < 0) {
                clearInterval(countdownInterval);

                // Fetch data from the node when countdown reaches 0
                fetchData(ip);

                // Restart the process after fetching data
                setTimeout(() => startTimerAndFetchData(ip), 5000); // Re-fetch every 5 seconds
            }
        }, 1000);
    };

    // Fetch data for a specific IP and display it in a styled manner
    const fetchData = (ip) => {
        const dataDisplay = document.getElementById(`data-${ip}`);
        fetch(`http://${ip}/data.php`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Clear existing data
                dataDisplay.innerHTML = '';

                // Display new data as structured UI
                Object.entries(data).forEach(([key, value]) => {
                    const dataItem = document.createElement('div');
                    dataItem.classList.add('data-item');

                    // Check if value is an object or array and display it accordingly
                    const formattedValue = typeof value === 'object' ? JSON.stringify(value, null, 2) : value;

                    dataItem.innerHTML = `
                        <label>${key}</label>
                        <span>${formattedValue}</span>
                    `;
                    dataDisplay.appendChild(dataItem);
                });

                // Apply animation to the data display
                dataDisplay.classList.add('show');
            })
            .catch(error => {
                // Keep the previous data on error
                dataDisplay.innerHTML += `<br/><span class="error">Error: ${error.message}</span>`;
            });
    };

    // Event delegation to handle "Show Data" and "Delete Node" button clicks
    nodeContainer.addEventListener('click', function (e) {
        const ip = e.target.getAttribute('data-ip');

        if (e.target.classList.contains('show-data-btn')) {
            // Start fetching the data with the timer
            startTimerAndFetchData(ip);
        } else if (e.target.classList.contains('delete-node-btn')) {
            // Delete the node
            ipList = ipList.filter(storedIp => storedIp !== ip);
            saveIps();
            renderNodes();
        }
    });

    // Initially render nodes
    renderNodes();
});
