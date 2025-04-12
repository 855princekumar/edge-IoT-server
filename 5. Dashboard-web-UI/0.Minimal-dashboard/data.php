<?php
header('Content-Type: application/json');

$host = "localhost";
$dbname = "node-db";
$username = "admin";
$password = "node@123";

$conn = new mysqli($host, $username, $password, $dbname);
if ($conn->connect_error) {
  echo json_encode(["error" => "Database connection failed"]);
  exit;
}

function getLatest($table, $fields = "*") {
  global $conn;
  $result = $conn->query("SELECT $fields FROM $table ORDER BY timestamp DESC LIMIT 1");
  return $result->fetch_assoc();
}

$data = [];

$outer = getLatest("outer_sensor", "temperature AS outer_temp");
$inner = getLatest("inner_sensor", "temperature AS inside_temp, humidity, pressure");
$health = getLatest("board_health", "cpu_temp, ram_usage, cpu_usage, disk_usage, net_up, net_down, core_volts, throttled_state, uptime");
$error = getLatest("error_logs", "message AS latest_error");

$data = array_merge($data, $outer ?? []);
$data = array_merge($data, $inner ?? []);
$data = array_merge($data, $health ?? []);
$data = array_merge($data, $error ?? ["latest_error" => "None"]);

echo json_encode($data);
$conn->close();
?>
