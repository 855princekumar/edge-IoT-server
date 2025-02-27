<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $ip = $_POST['ip'];

    // Database credentials
    $username = "admin";
    $password = "node@123";
    $dbname = "outer-temp"; // Your database name

    // Attempt to connect to the database
    $conn = @new mysqli($ip, $username, $password, $dbname);

    // Check if the connection was successful
    if ($conn->connect_error) {
        // If connection fails, redirect to phpMyAdmin login
        header("Location: http://$ip/phpmyadmin");
        exit();
    }

    $sql = "SELECT temperature FROM outer_temp ORDER BY id DESC LIMIT 1";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        $row = $result->fetch_assoc();
        echo $row['temperature'];
    } else {
        echo "No data found";
    }

    $conn->close();
}
?>
