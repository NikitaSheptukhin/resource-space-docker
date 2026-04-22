<?php
###############################
## ResourceSpace
## Local Configuration Script
###############################

# All custom settings should be entered in this file.
# Options may be copied from config.default.php and configured here.

# MySQL database settings
$mysql_server = 'mariadb';
$mysql_username = 'resourcespace_rw';
$mysql_password = 'rs_test_password';
$mysql_db = 'resourcespace';

# Base URL of the installation
# Internal IP here gets overwritten with the sed in entrypoint.sh
$baseurl = 'http://10.172.22.196:8000';

# Email settings
$email_notify = 'test@test.test';
$email_from = 'test@test.test';
# Secure keys
$scramble_key = '7f99d8e25ad1e65f3b21a7a864b83570093ce7bafdc8b343fa62c789c9610eb6';
$api_scramble_key = 'c0c7f6563b9dc69b6bcdccf5c8e83dca7e95fd62a34e3e8ad5c17e71a2ec2ede';

# Paths
$defaultlanguage = '';
$homeanim_folder = '';

/*

New Installation Defaults
-------------------------

The following configuration options are set for new installations only.
This provides a mechanism for enabling new features for new installations without affecting existing installations (as would occur with changes to config.default.php)

*/
                                
// Set imagemagick default for new installs to expect the newer version with the sRGB bug fixed.
$imagemagick_colorspace = "sRGB";

$contact_link=false;
$themes_simple_view=true;

$stemming=true;
$case_insensitive_username=true;
$user_pref_user_management_notifications=true;

$use_zip_extension=true;
$collection_download=true;

$ffmpeg_preview_force = true;
$ffmpeg_preview_extension = 'mp4';
$ffmpeg_preview_options = '-f mp4 -b:v 1200k -b:a 64k -ac 1 -c:v libx264 -pix_fmt yuv420p -profile:v baseline -level 3 -c:a aac -strict -2';

$daterange_search = true;
$upload_then_edit = true;

$purge_temp_folder_age=90;
$filestore_evenspread=true;

$comments_resource_enable=true;

$api_upload_urls = array();

$use_native_input_for_date_field = true;
$resource_view_use_pre = true;

$sort_tabs = false;
$maxyear_extends_current = 5;
$thumbs_display_archive_state = true;
$file_checksums = true;
$hide_real_filepath = true;
$annotate_enabled = true;

$plugins[] = "brand_guidelines";

# Tool paths
$imagemagick_path = '/usr/bin';
$ghostscript_path = '/usr/bin';
$ffmpeg_path      = '/usr/bin';
$exiftool_path    = '/usr/bin';
