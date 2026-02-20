<?php
require_once '/opt/iem/config/settings.inc.php';
require_once "/opt/iem/include/database.inc.php";
$dbconn = iemdb("iembot");

$st_addsub = iem_pg_prepare(
    $dbconn,
    <<<EOM
    insert into iembot_subscriptions(iembot_account_id, channel_id)
    values (
        (select iembot_account_id from iembot_rooms where roomname = $1),
        (select get_or_create_iembot_channel_id($2))
    ) on conflict do nothing
EOM
);
$st_delsub = iem_pg_prepare(
    $dbconn,
    <<<EOM
    DELETE from iembot_subscriptions
                WHERE iembot_account_id = (
        select iembot_account_id from iembot_rooms where roomname = $1
    ) and channel_id = (select get_or_create_iembot_channel_id($2))
EOM
);
$st_selectsubs = iem_pg_prepare(
    $dbconn,
    <<<EOM
    select c.id, c.channel_name from iembot_channels c JOIN iembot_subscriptions s
    on (c.id = s.channel_id) WHERE s.iembot_account_id = (
        select iembot_account_id from iembot_rooms where roomname = $1
    ) ORDER by c.channel_name ASC
EOM
);
$st_selectchannels = iem_pg_prepare(
    $dbconn,
    <<<EOM
    SELECT c.id, c.channel_name from iembot_channels c ORDER by c.channel_name ASC
EOM
);
$st_availchannels = iem_pg_prepare(
    $dbconn,
    <<<EOM
    SELECT c.id, c.channel_name from iembot_channels c
    where channel_name ~* $1 ORDER by c.channel_name ASC LIMIT $2 OFFSET $3
EOM
);


if (isset($_REQUEST["mode"]) && $_REQUEST["mode"] == "remove") {
    pg_execute($dbconn, $st_delsub, array(
        $_REQUEST["chatroom"],
        $_REQUEST["channel"]
    ));
    die(0);
}
if (isset($_REQUEST["mode"]) && $_REQUEST["mode"] == "add") {
    pg_execute($dbconn, $st_addsub, array(
        $_REQUEST["chatroom"],
        $_REQUEST["channel"]
    ));
    die(0);
}

if (isset($_REQUEST["mode"]) && $_REQUEST["mode"] == "subs") {
    $rs = pg_execute($dbconn, $st_selectsubs, array($_REQUEST["chatroom"]));
    $total = pg_num_rows($rs);
} else {
    $rs = pg_execute($dbconn, $st_availchannels, array(
        $_REQUEST["query"],
        $_REQUEST["limit"],
        $_REQUEST["start"]
    ));
    $rs2 = pg_execute($dbconn, $st_selectchannels, array());
    $total = pg_num_rows($rs2);
}
$ar = array("channels" => array(), "totalCount" => $total);

for ($i = 0; $row = pg_fetch_array($rs); $i++) {
    $z = array("id" => $row["id"], "text" => $row["channel_name"]);
    $ar["channels"][] = $z;
}

echo json_encode($ar);
