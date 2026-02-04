<?php
require_once '/opt/iem/config/settings.inc.php';
require_once "/opt/iem/include/database.inc.php";

$dbconn = iemdb("iembot");

$st_createroom = iem_pg_prepare(
    $dbconn,
    <<<EOM
    insert into iembot_rooms(roomname, iembot_account_id)
    values ($1, (select create_iembot_account_id($2)))
    on conflict do nothing
EOM
);


if (isset($_REQUEST["mode"]) && $_REQUEST["mode"] == "join") {
    pg_execute($dbconn, "DELSYND", array(
        $_REQUEST["chatroom"],
        $_REQUEST["synd"]
    ));
    die(0);
}
if (isset($_REQUEST["mode"]) && $_REQUEST["mode"] == "add") {
    pg_execute($dbconn, "ADDSYN", array(
        $_REQUEST["synd"],
        $_REQUEST["chatroom"],
        'P'
    ));
    die(0);
}

if (isset($_REQUEST["mode"]) && $_REQUEST["mode"] == "subs") {
    $rs = pg_execute($dbconn, "SYNROOMS", array($_REQUEST["chatroom"]));
    $total = pg_num_rows($rs);
} else {
    $rs = pg_execute($dbconn, "SELECTROOMS", array(
        $_REQUEST["chatroom"],
        $_REQUEST["query"],
        $_REQUEST["limit"],
        $_REQUEST["start"]
    ));
    $rs2 = pg_execute($dbconn, "SELECTROOMS", array(
        $_REQUEST["chatroom"],
        $_REQUEST["query"],
        100000,
        0
    ));
    $total = pg_num_rows($rs2);
}
$ar = array("synd" => array(), "totalCount" => $total);

for ($i = 0; $row = pg_fetch_array($rs); $i++) {
    $z = array("id" => $row["roomname"], "text" => $row["roomname"]);
    $ar["synd"][] = $z;
}

echo json_encode($ar);
