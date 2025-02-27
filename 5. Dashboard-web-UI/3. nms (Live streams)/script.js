document.addEventListener("DOMContentLoaded", function () {
    const addNodeBtn = document.getElementById("addNodeBtn");
    const addNodePopup = document.getElementById("addNodePopup");
    const submitNodeBtn = document.getElementById("submitNodeBtn");
    const cancelAddNodeBtn = document.getElementById("cancelAddNodeBtn");
    const nodeContainer = document.getElementById("nodeContainer");
    const toggleModeBtn = document.getElementById("toggleModeBtn");
    const body = document.body;
    const infoBtn = document.getElementById("infoBtn");
    const infoPopup = document.getElementById("infoPopup");
    const closeInfoBtn = document.getElementById("closeInfoBtn");
    const infoContent = document.getElementById("infoContent");

    let nodes = JSON.parse(localStorage.getItem("nodes")) || [];

    function renderNodes() {
        nodeContainer.innerHTML = "";
        nodes.forEach((node, index) => {
            const nodeDiv = document.createElement("div");
            nodeDiv.className = "nodeDiv";

            const features = node.features || [];

            const nodeContent = `
                <div class="nodeContent">
                    <div class="nodeDetails">
                        <h3>${node.ip}</h3>
                        <div class="nodeFeatures">
                            <h4>Features of Node:</h4>
                            <ul>
                                ${features.includes("Sensor") ? "<li class='feature-yes'>✔ Sensor</li>" : "<li class='feature-no'>✖ Sensor</li>"}
                                ${features.includes("Camera") ? "<li class='feature-yes'>✔ Camera</li>" : "<li class='feature-no'>✖ Camera</li>"}
                                ${features.includes("Battery Backup") ? "<li class='feature-yes'>✔ Battery Backup</li>" : "<li class='feature-no'>✖ Battery Backup</li>"}
                                ${features.includes("AC Power") ? "<li class='feature-yes'>✔ AC Power</li>" : "<li class='feature-no'>✖ AC Power</li>"}
                                ${features.includes("Solar Powered") ? "<li class='feature-yes'>✔ Solar Powered</li>" : "<li class='feature-no'>✖ Solar Powered</li>"}
                                ${features.includes("Active Cooling") ? "<li class='feature-yes'>✔ Active Cooling</li>" : "<li class='feature-no'>✖ Active Cooling</li>"}
                                ${features.includes("Bluetooth") ? "<li class='feature-yes'>✔ Bluetooth</li>" : "<li class='feature-no'>✖ Bluetooth</li>"}
                                ${features.includes("WiFi") ? "<li class='feature-yes'>✔ WiFi</li>" : "<li class='feature-no'>✖ WiFi</li>"}
                                ${features.includes("UART Terminal Access") ? "<li class='feature-yes'>✔ UART Terminal Access</li>" : "<li class='feature-no'>✖ UART Terminal Access</li>"}
                                ${features.includes("USB") ? "<li class='feature-yes'>✔ USB</li>" : "<li class='feature-no'>✖ USB</li>"}
                                ${features.includes("LAN") ? "<li class='feature-yes'>✔ LAN</li>" : "<li class='feature-no'>✖ LAN</li>"}
                            </ul>
                        </div>
                    </div>
                    <div class="nodeStream">
                        <iframe src="http://${node.ip}:9081" width="640" height="480"></iframe>
                    </div>
                    <button class="removeNodeBtn" data-index="${index}">🗑️</button>
                    <button class="editNodeBtn" data-index="${index}">✏️</button>
                </div>
            `;

            nodeDiv.innerHTML = nodeContent;
            nodeContainer.appendChild(nodeDiv);
        });
    }

    addNodeBtn.addEventListener("click", () => {
        addNodePopup.style.display = "block";
    });

    cancelAddNodeBtn.addEventListener("click", () => {
        addNodePopup.style.display = "none";
    });

    submitNodeBtn.addEventListener("click", () => {
        const form = document.getElementById("addNodeForm");
        const ip = form.nodeIP.value;
        const features = Array.from(form.querySelectorAll('input[name="feature"]:checked')).map(cb => cb.value);

        if (ip) {
            nodes.push({ ip, features });
            localStorage.setItem("nodes", JSON.stringify(nodes));
            renderNodes();
            addNodePopup.style.display = "none";
        }
    });

    nodeContainer.addEventListener("click", (event) => {
        if (event.target.classList.contains("removeNodeBtn")) {
            const index = event.target.dataset.index;
            nodes.splice(index, 1);
            localStorage.setItem("nodes", JSON.stringify(nodes));
            renderNodes();
        }

        if (event.target.classList.contains("editNodeBtn")) {
            const index = event.target.dataset.index;
            const node = nodes[index];
            const form = document.getElementById("addNodeForm");
            form.nodeIP.value = node.ip;
            form.querySelectorAll('input[name="feature"]').forEach(cb => {
                cb.checked = node.features.includes(cb.value);
            });
            addNodePopup.style.display = "block";
            submitNodeBtn.innerText = "Save Changes";
            submitNodeBtn.removeEventListener("click", handleAddNode);
            submitNodeBtn.addEventListener("click", () => handleEditNode(index));
        }
    });

    function handleEditNode(index) {
        const form = document.getElementById("addNodeForm");
        const ip = form.nodeIP.value;
        const features = Array.from(form.querySelectorAll('input[name="feature"]:checked')).map(cb => cb.value);

        if (ip) {
            nodes[index] = { ip, features };
            localStorage.setItem("nodes", JSON.stringify(nodes));
            renderNodes();
            addNodePopup.style.display = "none";
        }
    }

    toggleModeBtn.addEventListener("click", () => {
        body.classList.toggle("dark-mode");
        toggleModeBtn.innerHTML = body.classList.contains("dark-mode") ? "🌙" : "☀️";
    });

    infoBtn.addEventListener("click", () => {
        const infoHTML = `
            <p>Here you can provide information about the Node Monitoring System. Include details about the system, how to use it, and any other relevant information.</p>
        `;
        infoContent.innerHTML = infoHTML;
        infoPopup.style.display = "block";
    });

    closeInfoBtn.addEventListener("click", () => {
        infoPopup.style.display = "none";
    });

    renderNodes();
});
