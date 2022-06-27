/****************************************************/
/* Aldebaran Project Hopias                         */
/* play_message.js                                  */
/* Innovation - Protolab - mcaniot@aldebaran.com    */
/* Aldebaran Robotics (c) 2016 All Rights Reserved. */
/* This file is confidential.                       */
/****************************************************/

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

