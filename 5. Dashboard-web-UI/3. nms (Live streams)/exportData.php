<?php
if (isset($_GET['ip'])) {
    $ip = $_GET['ip'];

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

    $sql = "SELECT * FROM outer_temp";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        header('Content-Type: text/csv');
        header('Content-Disposition: attachment;filename="temperature_data.csv"');

        $output = fopen('php://output', 'w');
        fputcsv($output, array('ID', 'Temperature', 'Timestamp'));

        while ($row = $result->fetch_assoc()) {
            fputcsv($output, $row);
        }

        fclose($output);
    } else {
        echo "No data found";
    }

    $conn->close();
}
?>
