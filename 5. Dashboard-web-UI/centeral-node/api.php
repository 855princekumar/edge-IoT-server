<?php
header("Content-Type: application/json");
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, DELETE");
header("Access-Control-Allow-Headers: Content-Type, Authorization");

$db_host = "localhost";
$db_user = "admin";
$db_pass = "node@123";
$db_name = "node-db";

// Create connection
$conn = new mysqli($db_host, $db_user, $db_pass, $db_name);

// Check connection
if ($conn->connect_error) {
    die(json_encode(["status" => "error", "message" => "Connection failed: " . $conn->connect_error]));
}

// Helper function to verify credentials
function verifyCredentials($conn, $username, $password) {
    $stmt = $conn->prepare("SELECT password_hash FROM `user-credentials` WHERE username = ?");
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $result = $stmt->get_result();
    
    if ($result->num_rows === 0) return false;
    
    $row = $result->fetch_assoc();
    $hashed_input = hash('sha256', $password . 'somesalt');
    return hash_equals($row['password_hash'], $hashed_input);
}

// API to login
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_GET['action']) && $_GET['action'] === 'login') {
    $data = json_decode(file_get_contents('php://input'), true);
    
    if (empty($data['username']) || empty($data['password'])) {
        echo json_encode(["status" => "error", "message" => "Username and password are required"]);
        exit;
    }
    
    if (verifyCredentials($conn, $data['username'], $data['password'])) {
        echo json_encode(["status" => "success", "token" => base64_encode($data['username'] . ':' . hash('sha256', $data['password'] . 'somesalt'))]);
    } else {
        echo json_encode(["status" => "error", "message" => "Invalid credentials"]);
    }
    exit;
}

// Verify token for all other endpoints
if (!isset($_GET['action']) || $_GET['action'] !== 'login') {
    if (!isset($_SERVER['HTTP_AUTHORIZATION'])) {
        header('HTTP/1.0 401 Unauthorized');
        echo json_encode(["status" => "error", "message" => "Authorization required"]);
        exit;
    }
    
    $auth = $_SERVER['HTTP_AUTHORIZATION'];
    if (strpos($auth, 'Bearer ') !== 0) {
        header('HTTP/1.0 401 Unauthorized');
        echo json_encode(["status" => "error", "message" => "Invalid authorization format"]);
        exit;
    }
    
    $token = substr($auth, 7);
    $decoded = base64_decode($token);
    if ($decoded === false || strpos($decoded, ':') === false) {
        header('HTTP/1.0 401 Unauthorized');
        echo json_encode(["status" => "error", "message" => "Invalid token"]);
        exit;
    }
    
    list($username, $password_hash) = explode(':', $decoded, 2);
    if (!verifyCredentials($conn, $username, 'dummy')) { // We only check the hash matches
        $stmt = $conn->prepare("SELECT password_hash FROM `user-credentials` WHERE username = ?");
        $stmt->bind_param("s", $username);
        $stmt->execute();
        $result = $stmt->get_result();
        
        if ($result->num_rows === 0 || !hash_equals($result->fetch_assoc()['password_hash'], $password_hash)) {
            header('HTTP/1.0 401 Unauthorized');
            echo json_encode(["status" => "error", "message" => "Invalid token"]);
            exit;
        }
    }
}

// API to get all nodes
if ($_SERVER['REQUEST_METHOD'] === 'GET' && (!isset($_GET['action']) || $_GET['action'] !== 'login')) {
    $sql = "SELECT node_name, node_ip FROM `node-stat` ORDER BY created_at DESC";
    $result = $conn->query($sql);
    
    $nodes = [];
    if ($result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            $nodes[] = $row;
        }
    }
    
    echo json_encode(["status" => "success", "nodes" => $nodes]);
    exit;
}

// API to add a node
if ($_SERVER['REQUEST_METHOD'] === 'POST' && (!isset($_GET['action']) || $_GET['action'] !== 'login')) {
    $data = json_decode(file_get_contents('php://input'), true);
    
    if (empty($data['node_name']) || empty($data['node_ip'])) {
        echo json_encode(["status" => "error", "message" => "Node name and IP are required"]);
        exit;
    }
    
    // Check if node exists
    $stmt = $conn->prepare("SELECT id FROM `node-stat` WHERE node_name = ? OR node_ip = ?");
    $stmt->bind_param("ss", $data['node_name'], $data['node_ip']);
    $stmt->execute();
    $result = $stmt->get_result();
    
    if ($result->num_rows > 0) {
        echo json_encode(["status" => "error", "message" => "Node name or IP already exists"]);
        exit;
    }
    
    // Insert new node
    $stmt = $conn->prepare("INSERT INTO `node-stat` (node_name, node_ip) VALUES (?, ?)");
    $stmt->bind_param("ss", $data['node_name'], $data['node_ip']);
    
    if ($stmt->execute()) {
        echo json_encode(["status" => "success", "message" => "Node added successfully"]);
    } else {
        echo json_encode(["status" => "error", "message" => "Error adding node"]);
    }
    exit;
}

// API to remove a node
if ($_SERVER['REQUEST_METHOD'] === 'DELETE') {
    parse_str(file_get_contents('php://input'), $data);
    
    if (empty($data['node_ip'])) {
        echo json_encode(["status" => "error", "message" => "Node IP is required"]);
        exit;
    }
    
    $stmt = $conn->prepare("DELETE FROM `node-stat` WHERE node_ip = ?");
    $stmt->bind_param("s", $data['node_ip']);
    
    if ($stmt->execute()) {
        echo json_encode(["status" => "success", "message" => "Node removed successfully"]);
    } else {
        echo json_encode(["status" => "error", "message" => "Error removing node"]);
    }
    exit;
}

echo json_encode(["status" => "error", "message" => "Invalid request"]);
?>