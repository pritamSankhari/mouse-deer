<?php
include 'myconfig/db.php';

if (!isset($_GET['snapshot_id']) || empty($_GET['snapshot_id'])) {
    die("Snapshot ID is required.");
}

$snapshot_id = $_GET['snapshot_id'];

/* Fetch data safely */
$stmt = $conn->prepare("SELECT * FROM netstat_logs WHERE snapshot_id=? ORDER BY protocol, local_address");
$stmt->bind_param("s", $snapshot_id);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows == 0) {
    die("No records found for this snapshot.");
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>Snapshot <?= htmlspecialchars($snapshot_id); ?></title>
    <style>
        body { font-family: Arial; padding:20px; }
        table { border-collapse: collapse; width:100%; }
        th, td { border:1px solid #ccc; padding:8px; font-size:14px; }
        th { background:#f4f4f4; }
        .listening { background:#e7f7e7; }
        .established { background:#fff3cd; }
    </style>
</head>
<body>

<h2>Snapshot ID: <?= htmlspecialchars($snapshot_id); ?></h2>

<table>
    <tr>
        <th>Protocol</th>
        <th>Local Address</th>
        <th>Foreign Address</th>
        <th>State</th>
        <th>PID</th>
        <th>Created At</th>
    </tr>

    <?php while($row = $result->fetch_assoc()): 
        $class = '';
        if ($row['state'] == 'LISTENING') $class = 'listening';
        if ($row['state'] == 'ESTABLISHED') $class = 'established';
    ?>
        <tr class="<?= $class; ?>">
            <td><?= htmlspecialchars($row['protocol']); ?></td>
            <td><?= htmlspecialchars($row['local_address']); ?></td>
            <td><?= htmlspecialchars($row['foreign_address']); ?></td>
            <td><?= htmlspecialchars($row['state']); ?></td>
            <td><?= htmlspecialchars($row['pid']); ?></td>
            <td><?= htmlspecialchars($row['created_at']); ?></td>
        </tr>
    <?php endwhile; ?>
</table>

</body>
</html>
