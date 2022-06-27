/****************************************************/
/* Aldebaran Project Hopias                         */
/* image.js                                         */
/* Innovation - Protolab - mcaniot@aldebaran.com    */
/* Aldebaran Robotics (c) 2016 All Rights Reserved. */
/* This file is confidential.                       */
/****************************************************/


// This function is called when a signal is sent by choregraphe thank to an event.
function toTabletHandler(value) {
    document.getElementById("command").value= value;
    tmp = document.getElementById("command").value;
    if (tmp === "erase_all"){
        undisplay();
    }
    else{
        changeSourceImage(tmp)
    }
}

// Change the image source
function changeSourceImage(nameImage){
    document.getElementById("groupImage").style.display ="block"
    document.images["image"].src =  nameImage
}

// Undisplay the image
function undisplay(){
    document.images["image"].src =  ""
    document.getElementById("groupImage").style.display ="none"
}