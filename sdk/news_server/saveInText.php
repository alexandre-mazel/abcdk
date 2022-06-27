<?php
// Receive form Post data and Saving it in variables


$yearOfAction = @$_POST['yearOfAction'];
$monthOfAction = @$_POST['monthOfAction'];
$weekDayOfAction = @$_POST['weekDayOfAction'];
$dayOfAction = @$_POST['dayOfAction'];
$hourOfAction = @$_POST['hourOfAction'];
$minuteOfAction = @$_POST['minuteOfAction'];
$secondOfAction = @$_POST['secondOfAction'];
$place = @$_POST['place'];
$source = @$_POST['source'];
$action = @$_POST['action'];
$cible = @$_POST['cible'];
$objet = @$_POST['objet'];
$actionDuration = @$_POST['actionDuration'];
$Keywords = @$_POST['Keywords'];


// Write the name of text file where data will be store

$filename = "/home/elagrue/Desktop/test/mydata2.txt";

// Marge all the variables with text in a single variable. 

$f_data='
 '$yearOfAction.','.$monthOfAction.','.$weekDayOfAction.','.$dayOfAction.','.$hourOfAction.','.$minuteOfAction.','.$secondOfAction.','.$place.','.$source.','.$action.','.$cible.','.$objet.','.$actionDuration.','.$Keywords.',' ;
//$f_data=$yearOfAction','.$yearOfAction.',  
// ==============================================================================
// ';


echo 'Form data has been saved to '.$filename.'  <br>
<a href="'.$filename.'">Click here to read </a> ';
$file = fopen($filename, "a");
fwrite($file,$f_data);
fclose($file);
?>
