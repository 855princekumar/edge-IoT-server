<?php
$servername = "localhost";
$username = "your_username";
$password = "your_password";
$dbname = "node_db";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$table = $_GET['table'];

$sql = "SELECT * FROM $table ORDER BY id DESC LIMIT 100";
$result = $conn->query($sql);

$values = [];
while($row = $result->fetch_assoc()) {
    $values[] = $row['value']; // Assuming 'value' is the column name
}

$average = array_sum($values) / count($values);

echo json_encode(['average' => $average]);

$conn->close();
?>
