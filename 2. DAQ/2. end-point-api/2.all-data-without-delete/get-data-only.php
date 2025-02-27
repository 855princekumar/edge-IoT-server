<?php
// API Configuration
$pythonScript = "/usr/bin/python3 /home/nodeL2/Downloads/daq-flush/db_handler_safe_mode.py";
$zipFile = "/tmp/node_db_backup.zip";
$validUsername = "nodeL2";
$validPassword = "node@123";

// Input Validation
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    if (!isset($_GET['username']) || !isset($_GET['password'])) {
        http_response_code(400);
        echo "Error: Username and password are required.";
        exit;
    }

    $username = $_GET['username'];
    $password = $_GET['password'];

    if ($username !== $validUsername || $password !== $validPassword) {
        http_response_code(401);
        echo "Error: Invalid credentials.";
        exit;
    }

    // Trigger the Python Script (Safe Mode)
    ob_start(); // Start output buffering
    echo "[INFO] Triggering Python script...\n";
    exec($pythonScript, $output, $return_var);

    if ($return_var !== 0) {
        http_response_code(500);
        echo "Error: Failed to execute Python script.";
        ob_end_flush();
        exit;
    }

    // Check if the Zip File Exists
    if (!file_exists($zipFile)) {
        http_response_code(404);
        echo "Error: Backup file not found.";
        ob_end_flush();
        exit;
    }

    // Serve the Zip File for Download
    ob_clean(); // Clean output buffer before headers
    header('Content-Type: application/zip');
    header('Content-Disposition: attachment; filename="node_db_backup.zip"');
    header('Content-Length: ' . filesize($zipFile));
    readfile($zipFile);

    ob_end_flush();
    exit;
} else {
    http_response_code(405);
    echo "Error: Only GET method is allowed.";
    exit;
}
?>
