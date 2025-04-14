<?php
header('Content-Type: application/json');

// Database connection details
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

// Get the latest data for each sensor
$outer = getLatest("outer_sensor", "temperature AS outer_temp");
$inner = getLatest("inner_sensor", "temperature AS inside_temp, humidity, pressure");
$health = getLatest("board_health", "cpu_temp, ram_usage, cpu_usage, disk_usage, net_up, net_down, core_volts, throttled_state, uptime");
$error = getLatest("error_logs", "message AS latest_error");

// Merge data arrays
$data = array_merge($data, $outer ?? []);
$data = array_merge($data, $inner ?? []);
$data = array_merge($data, $health ?? []);
$data = array_merge($data, $error ?? ["latest_error" => "None"]);

// Ensure that the data is numeric where applicable, and fallback to default values if missing
$data['outer_temp'] = isset($data['outer_temp']) ? floatval($data['outer_temp']) : 0;
$data['inside_temp'] = isset($data['inside_temp']) ? floatval($data['inside_temp']) : 0;
$data['humidity'] = isset($data['humidity']) ? floatval($data['humidity']) : 0;
$data['pressure'] = isset($data['pressure']) ? floatval($data['pressure']) : 0;
$data['cpu_temp'] = isset($data['cpu_temp']) ? floatval($data['cpu_temp']) : 0;
$data['ram_usage'] = isset($data['ram_usage']) ? floatval($data['ram_usage']) : 0;
$data['cpu_usage'] = isset($data['cpu_usage']) ? floatval($data['cpu_usage']) : 0;
$data['disk_usage'] = isset($data['disk_usage']) ? floatval($data['disk_usage']) : 0;
$data['net_up'] = isset($data['net_up']) ? intval($data['net_up']) : 0;
$data['net_down'] = isset($data['net_down']) ? intval($data['net_down']) : 0;
$data['core_volts'] = isset($data['core_volts']) ? floatval($data['core_volts']) : 0;
$data['throttled_state'] = isset($data['throttled_state']) ? $data['throttled_state'] : 'None';
$data['uptime'] = isset($data['uptime']) ? $data['uptime'] : 'Unknown';
$data['latest_error'] = isset($data['latest_error']) ? $data['latest_error'] : 'None';

// Return the merged data as JSON
echo json_encode($data);

$conn->close();
?>
