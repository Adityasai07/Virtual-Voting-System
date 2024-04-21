<?php
$mycon = mysqli_connect('localhost', 'root', '', 'sample'); // Modify database credentials as needed

$query = "SELECT * FROM voter"; // Selecting all columns from 'voter_faces' table
$result = mysqli_query($mycon, $query);

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Display Images</title>
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
        }
        img {
            width: 100px;
            height: auto;
        }
    </style>
</head>
<body>
    <table>
        <tr>
            <th>ID</th>
            <th>Photo</th>
        </tr>
        <?php
        if (mysqli_num_rows($result) > 0) {
            while ($row = mysqli_fetch_assoc($result)) {
                $id = $row['voterId'];
                $imageData = base64_encode($row['voterFace']); // Assuming the image is stored as binary data
                echo "<tr>";
                echo "<td>$id</td>";
                echo "<td><img src='data:image/jpeg;base64,$imageData'/></td>";
                echo "</tr>";
            }
        } else {
            echo "<tr><td colspan='6'>No images found.</td></tr>";
        }
        ?>
    </table>
</body>
</html>