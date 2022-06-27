/****************************************************/
/* Aldebaran Project Hopias                         */
/* record.js                                        */
/* Innovation - Protolab - mcaniot@aldebaran.com    */
/* Aldebaran Robotics (c) 2016 All Rights Reserved. */
/* This file is confidential.                       */
/****************************************************/

// variable for play/stop
var state = "stop"

// Function who manage the command sent by choregraphe
function choice(){
    if (state === "stop" ){
        state = "record"
        document.images["record_img"].src = "img/stop.png"
    }
    else {
        state = "stop"
        document.images["record_img"].src = "img/start.png"
    }
    sendToChoregraphe(state)

}


// This function is called when a signal is sent by choregraphe thank to an event.
function toTabletHandler(value) {
    document.getElementById("command").value= value;
    tmp = document.getElementById("command").value;
    if ((tmp.length)>1){
        if (tmp[0] === "xxx" && tmp[1] ==="xxx") {
            // name by default
            document.getElementById("author_msg").innerHTML= "Edouard";
            document.getElementById("target_msg").innerHTML= "Jean-Marc";
        }
        else{
            document.getElementById("author_msg").innerHTML= tmp[0];
            document.getElementById("target_msg").innerHTML= tmp[1];
        }
    }
}


// Sound heard when the button is clicked
var audio = new Audio('sound/click.mp3');

// Play sound
function clickSound(){    
    audio.play();
}