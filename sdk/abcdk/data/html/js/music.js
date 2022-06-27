/****************************************************/
/* Aldebaran Project Hopias                         */
/* music.js                                         */
/* Innovation - Protolab - mcaniot@aldebaran.com    */
/* Aldebaran Robotics (c) 2016 All Rights Reserved. */
/* This file is confidential.                       */
/****************************************************/

var play = 1

window.onclick = function() {
    play = play + 1
    if (play == 2 ){
        play = 0
        choice("Pepper menu")
    }
}


// Function who manage the command sent by choregraphe
function choice(tmp){
    
    if (tmp === "Pepper lecture" ){
        document.images["pause/play"].src = "img/pause.png"
        hide()
        response("Pepper lecture")
        play = 0
    }
    if (tmp === "Pepper pause" ){
        document.images["pause/play"].src = "img/start.png"
        hide()
        response("Pepper pause")
    }
    if (tmp === "Pepper suivant" ){
        response("Pepper suivant")
    }
    if (tmp === "Pepper précédent" ){
        response("Pepper précédent")
    }
    if (tmp === "Pepper plus" ){
        response("Pepper plus")
    }
    if (tmp === "Pepper moins" ){
        response("Pepper moins")
    }
    if (tmp === "Pepper menu" ){
        document.images["pause/play"].src = "img/start.png"
        show()
        response("Pepper pause")
    }

    if(tmp === "Pepper cache"){
        hide();
        response("Pepper cache")
    }
    if (tmp === "Pepper stop" ){
        response("Pepper stop")
        eraseArtist()
        document.getElementById("animation").style.display = 'none';
        hide();
        
    }

}

// Display the button bar
function show(){
	document.getElementById("buttonbar").style.display = 'block';
}

// Undisplay the button bar
function hide(){
    document.getElementById("buttonbar").style.display = 'none';
}

// This function is called when a signal is sent by choregraphe thank to an event.
function toTabletHandler(value) {
    document.getElementById("command").value= value;
    tmp = document.getElementById("command").value;
    list = tmp.split(";")

    if (list[0] == "artist" && list.length > 1) {
        // Change the text on the tablet screen
        eraseArtist()
        writeArtist(list[1])
        document.getElementById("animation").style.display = 'block';
    }
    else{
        choice(tmp)
    }
}

// Send data to choregraphe
function response(resp) {
	sendToChoregraphe(resp);  
}

// animation when the button is clicked
function clickAnimation(element,name1, name2) {
    clickSound()
    setTimeout(function(){
        element.setAttribute('src', name2);
    }, 250);
    element.setAttribute('src', name1);

}


// Sound heard when the button is clicked
var audio = new Audio('sound/click.mp3');

// Play sound
function clickSound(){    
    audio.play();
}


// Write artist
function writeArtist(tmp){
    $.getScript("js/write.js", function(){
        textFullScreen(tmp,"#objectArtist","Block")

    });
}

// Erase name artist
function eraseArtist(){
    $("#objectArtist").empty()
}
