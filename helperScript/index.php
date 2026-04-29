<?php
//This file must be placed in /var/www/html/resourcespace/rs_helper/ and www-data must have all permissions on both the parent directory (rs_helper) and the file itself


// Admin helper endpoint for operations not exposed by the standard RS API.
// Uses the same signature verification as the RS API (sha256 + api_scramble_key).
include "../include/boot.php";
include_once "../include/api_functions.php";
include_once "../include/user_functions.php";

header('Content-Type: application/json');

$user  = getval("user", "");
$sign  = getval("sign", "");
$query = $_SERVER["QUERY_STRING"];

parse_str($query, $qp);
if (isset($qp['sign'])) {
    $query = str_ireplace("sign=" . $qp['sign'], "!|!|", $query);
}
$query = str_replace("&!|!|", "", ltrim($query, "!|!|&"));

if (!check_api_key($user, $query, $sign)) {
    http_response_code(401);
    exit(json_encode(["error" => "Unauthorized"]));
}

$function = getval("function", "");

switch ($function) {

    case "create_group":
        $name        = getval("param1", "");
        $permissions = getval("param2", "");
        $parent      = (int) getval("param3", 0);
        if ($name === "") {
            http_response_code(400);
            exit(json_encode(["error" => "Group name required"]));
        }
        $id = save_usergroup(0, [
            "name"        => $name,
            "permissions" => $permissions,
            "parent"      => $parent,
        ]);
        echo json_encode((int) $id);
        break;

    case "add_group_collection_access":
        $group_id      = (int) getval("param1", 0);
        $collection_id = (int) getval("param2", 0);
        ps_query(
            "INSERT IGNORE INTO usergroup_collection (collection, usergroup) VALUES (?, ?)",
            ["i", $collection_id, "i", $group_id]
        );
        echo json_encode(true);
        break;

    case "delete_group_collection_access":
        $group_id      = (int) getval("param1", 0);
        $collection_id = (int) getval("param2", 0);
        ps_query(
            "DELETE FROM usergroup_collection WHERE collection = ? AND usergroup = ?",
            ["i", $collection_id, "i", $group_id]
        );
        echo json_encode(true);
        break;

    case "set_collection_public":
        $collection_id = (int) getval("param1", 0);
        $public        = (int) getval("param2", 0);
        ps_query(
            "UPDATE collection SET public = ?, type = ? WHERE ref = ?",
            ["i", $public, "i", ($public ? 4 : 0), "i", $collection_id]
        );
        echo json_encode(true);
        break;

    case "set_collection_featured":
        $collection_id = (int) getval("param1", 0);
        $featured      = (int) getval("param2", 1);
        ps_query(
            "UPDATE collection SET home_page_publish = ?, type = ? WHERE ref = ?",
            ["i", $featured, "i", ($featured ? 3 : 0), "i", $collection_id]
        );
        echo json_encode(true);
        break;
        
    case "update_user_group":
        $target_username = getval("param1", "");
        $group_id        = (int) getval("param2", 0);
        $user_ref        = get_user_by_username($target_username);
        if ($user_ref === false) {
            http_response_code(404);
            exit(json_encode(["error" => "User not found: $target_username"]));
        }
        ps_query(
            "UPDATE user SET usergroup = ? WHERE ref = ?",
            ["i", $group_id, "i", $user_ref]
        );
        echo json_encode(true);
        break;

    default:
        http_response_code(400);
        exit(json_encode(["error" => "Unknown function: $function"]));
}
