/****************************************************/
/* Aldebaran Project Hopias                         */
/* menu.js                                          */
/* Innovation - Protolab - mcaniot@aldebaran.com    */
/* Aldebaran Robotics (c) 2016 All Rights Reserved. */
/* This file is confidential.                       */
/****************************************************/

// List of the name of the button
var list_answer = ["Video","Music","next","back","App 3","App 4","App 5","App 6","App 7","App 8"]

var nb_page = 1;
// Function who manage the command sent by choregraphe
function choice(tmp){
    for(var i= 0; i < list_answer.length; i++)
    {
        if (list_answer[i] === tmp){

            if (tmp === "next"){
                changePage("1","2")
            }
            else{
                if (tmp === "back"){
                    changePage("2","1")
                }
                else{
                    erase();
                    sendToChoregraphe(tmp);
                }
            }
            
        }
    }
}

// This function is called when a signal is sent by choregraphe thank to an event.
function toTabletHandler(value) { 
    document.getElementById("command").value= value;
    tmp = document.getElementById("command").value;
    if (tmp === "erase_all"){
        erase();
    }
    else {
        choice(tmp);
    }
    
}


function changePage(old_page, next_page){
    document.getElementById("pageMenu"+old_page).style.display = 'none';
    document.getElementById("pageMenu"+next_page).style.display = 'block';
}

// Erase Question and button answer
function erase(){
    document.getElementById("pageMenu1").style.display = 'none';
    document.getElementById("pageMenu2").style.display = 'none';
}

// Sound heard when the button is clicked
var audio = new Audio('sound/click.mp3');

// Play sound
function clickSound(){    
    audio.play();
}