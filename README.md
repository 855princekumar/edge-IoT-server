# Edge IoT Server 🚀

The `edge-IoT-server` repository is designed to provide a minimalistic yet effective edge node server based on a **four-layer architecture**, functioning as a gateway for field nodes in IoT deployments. This project draws inspiration from the [IOTstack](https://github.com/SensorsIot/IOTstack) project, aiming to offer a streamlined solution for edge computing needs.

This project is mainly focused on **Linux-based systems** and has been specifically tested on **Ubuntu 24 LTS**. However, for Windows users, **XAMPP** is recommended for easy setup.

## Features ✨

- **Layered Architecture 🏗️**: Implements a four-layer model for modularity and scalability.
- **LAMP Stack Integration (Linux) 🖥️**: Utilizes the Linux, Apache, MySQL, and PHP stack to ensure a robust and scalable server environment.
- **XAMPP Compatibility (Windows) 💻**: Allows easy setup on Windows using XAMPP.
- **Data Acquisition (DAQ) 📡**: Implements mechanisms for collecting and processing data from various IoT sensors and devices.
- **Stream Synchronization ⏳**: Ensures real-time data streaming and synchronization between devices and the server.
- **SQL Data Download 💾**: Facilitates efficient retrieval and management of data stored in SQL databases.
- **Dashboard Web UI 📊**: Provides a user-friendly web interface for monitoring and managing connected devices and data streams.

## Four-Layer Architecture 🏗️

1. **Perception Layer 📡**: Includes all field nodes and sensors that collect data.
2. **Network Layer 🌐**: Handles communication protocols like MQTT, HTTP, and WebSockets.
3. **Edge Processing Layer ⚡**: Processes and filters data before sending it to the cloud or database.
4. **Application Layer 🎛️**: Web dashboard and API endpoints for user interaction.

   ![image](https://github.com/user-attachments/assets/b5a658b0-56ee-4700-a929-d255687537bb)

## Getting Started 🛠️

To set up the `edge-IoT-server`, follow these steps:

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/855princekumar/edge-IoT-server.git
cd edge-IoT-server
```

### 2️⃣ Install Dependencies
#### Linux (Ubuntu 24 LTS Preferred)
- Install **LAMP stack** (Linux, Apache, MySQL, PHP):
  ```bash
  sudo apt update
  sudo apt install apache2 mysql-server php libapache2-mod-php php-mysql
  ```
- Install any additional dependencies required by the project.

#### Windows (XAMPP Recommended)
- Download and install **XAMPP** from [Apache Friends](https://www.apachefriends.org/index.html).
- Start **Apache** and **MySQL** from the XAMPP control panel.

### 3️⃣ Configure the Server
- Set up configuration files as needed, ensuring that database connections and other settings are correctly specified.

### 4️⃣ Run the Server
#### Linux (Ubuntu)
```bash
sudo systemctl start apache2
sudo systemctl enable apache2
```

#### Windows (XAMPP)
- Start **Apache** and **MySQL** from the XAMPP control panel.

### 5️⃣ Access the Dashboard
- Open a web browser and navigate to `http://localhost` (or the appropriate IP address) to access the dashboard interface.

## Folder Structure 📂

- **Perception Layer (Sensors & Nodes) 📡**: Houses data acquisition modules.
- **Network Layer (Communication) 🌐**: Handles data transmission between devices and the server.
- **Edge Processing Layer ⚡**: Includes real-time processing and filtering mechanisms.
- **Application Layer (Dashboard & API) 🎛️**: Contains front-end web dashboard and API components.

## Inspiration 💡

This project is inspired by:
- [IOTstack by gcgarner](https://github.com/gcgarner/IOTstack)
- [IOTstack by SensorsIot](https://github.com/SensorsIot/IOTstack)

While IOTstack provides a comprehensive Docker-based solution for IoT on Raspberry Pi, `edge-IoT-server` focuses on delivering a minimalistic and efficient edge server tailored for specific IoT gateway applications.

## Contributing 🤝

Contributions are welcome! If you'd like to contribute to this project:
1. Fork the repository.
2. Create a new branch.
3. Submit a pull request.

Ensure that your code adheres to the project's coding standards and includes appropriate tests.

## License 📄

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

By providing a lightweight and structured four-layer edge server solution, `edge-IoT-server` aims to simplify the deployment and management of IoT devices in various environments. 🚀
