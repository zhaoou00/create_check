<?php
date_default_timezone_set('UTC');
include("lib/check-generator.php");
// foreach ($_FILES['file'] as $key=>$value) echo $key,":",$value,"<p>"; 
$f = $_FILES['file']['tmp_name'];

if(($handle = fopen($f, 'r')) !== FALSE) {
    // necessary if a large csv file
    set_time_limit(0);

    $row = 0;    
    $CHK = new CheckGenerator;
    while(($data = fgetcsv($handle, 1000, ',')) !== FALSE) {
        // foreach ($data as $key=>$value) echo $key,":",$value,"<p>"; 
        if($row == 0){
          $kks = $data;
        }
        else{          
          foreach($data as $key=>$value){
            if($kks[$key] == 'routing_number:account_number'){
              list($check['routing_number'], $check['account_number']) = explode(':', $value);
            }
            else{
            $check[$kks[$key]] = $value;  
            }            

          }
          // 3 checks per page
          // $check['logo'] = "";
          // foreach ($check as $key=>$value) echo $key,":",$value,"<p>"; 
          $CHK->AddCheck($check);
        }
        $row++;
    }
    fclose($handle);
}



if(array_key_exists('REMOTE_ADDR', $_SERVER)) {
  // Called from a browser
  header('Content-Type: application/octet-stream', false);
  header('Content-Type: application/pdf', false);
  $CHK->PrintChecks();
} else {
  // Called from the command line
  ob_start();
  $CHK->PrintChecks();
  $pdf = ob_get_clean();
  file_put_contents('checks.pdf', $pdf);
  echo "Saved to file: checks.pdf\n";
}