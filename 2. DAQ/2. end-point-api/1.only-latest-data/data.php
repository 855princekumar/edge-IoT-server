<?php
// Allow cross-origin requests
header("Access-Control-Allow-Origin: *");  // Allows any origin to access this API
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");

// Database connection parameters
$servername = "localhost";
$username = "admin";
$password = "node@123";
$dbname = "node-db";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die(json_encode(['error' => 'Database connection failed']));
}

// Fetch the latest data from all tables (adjust the query according to your schema)
$tables = [];
$sql = "SHOW TABLES";  // Fetch all table names
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    while ($row = $result->fetch_row()) {
        $tableName = $row[0];
        $query = "SELECT * FROM $tableName ORDER BY timestamp DESC LIMIT 1";
        $tableData = $conn->query($query);

        if ($tableData->num_rows > 0) {
            $tables[$tableName] = $tableData->fetch_assoc();
        }
    }
} else {
    echo json_encode(['error' => 'No tables found']);
    $conn->close();
    exit;
}

// Output the latest data as JSON
echo json_encode($tables);

$conn->close();
?>
