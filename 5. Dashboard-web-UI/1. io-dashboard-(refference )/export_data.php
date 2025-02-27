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

header('Content-Type: text/csv');
header('Content-Disposition: attachment;filename=' . $table . '_data.csv');

$sql = "SELECT * FROM $table";
$result = $conn->query($sql);

$fields = $result->fetch_fields();
$csv = '';

foreach ($fields as $field) {
    $csv .= $field->name . ",";
}
$csv = rtrim($csv, ',') . "\n";

while ($row = $result->fetch_assoc()) {
    $csv .= implode(",", $row) . "\n";
}

echo $csv;

$conn->close();
?>
