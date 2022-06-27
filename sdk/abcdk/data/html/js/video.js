/****************************************************/
/* Aldebaran Project Hopias                         */
/* video.js                                         */
/* Innovation - Protolab - mcaniot@aldebaran.com    */
/* Aldebaran Robotics (c) 2016 All Rights Reserved. */
/* This file is confidential.                       */
/****************************************************/

// Creation of a video
var video = document.createElement("video"); 
video.height=950 
video.width=1600 

// Creation of a video source
var sourceMP4 = document.createElement("source"); 
sourceMP4.type = "video/mp4";
sourceMP4.src = ""

// sourceMP4 become a child of video
video.appendChild(sourceMP4);


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
        video.play()
        document.images["pause/play"].src = "img/pause.png"
        hide()
    }
    if (tmp === "Pepper pause" ){
        video.pause()
        document.images["pause/play"].src = "img/start.png"
        hide()
    }

    if (tmp === "Pepper menu" ){
        video.pause()
        document.images["pause/play"].src = "img/start.png"
        show()
    }

    if(tmp === "Pepper cache"){
        hide();
    }

    if (tmp === "Pepper stop" ){
        eraseVideo()      
        hide();
        sendToChoregraphe("stop")
    }
    if (tmp === "Pepper suivant" ){
        video.currentTime += 10
    }
    if (tmp === "Pepper précédent" ){
        video.currentTime -= 10
    }
    if (tmp === "Pepper plus" && (video.volume + 0.1 <= 1)){
        video.volume += 0.1
    }
    if (tmp === "Pepper moins" && (video.volume - 0.1 >= 0)){
        video.volume -= 0.1
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
    if (list[0] == "video" && list.length > 1) {
        eraseVideo()
        newVideo(list[1])
    }
    else{
        choice(tmp)
    }
}

// Create a new video
function newVideo(nameVideo){
	$(sourceMP4).attr("src", nameVideo)
	document.getElementById("groupMovie").appendChild(video);
	video.load();
	video.play();
}

// erase video
function eraseVideo(){
	video.pause()
	$(sourceMP4).attr("src", "")
	while (document.getElementById("groupMovie").firstChild) {
        document.getElementById("groupMovie").removeChild(document.getElementById("groupMovie").firstChild);
    }

}


// play video
function vidplay(evt) {
                    
    button = evt.target; //  get the button id to swap the text based on the state                                    
    if (video.paused) {   // play the file, and display pause symbol
        video.play();
        document.images["pause/play"].src = "img/pause.png";
    } else {              // pause the file, and display play symbol  
            video.pause();
            document.images["pause/play"].src = "img/start.png";
    }
    hide();
}

//  button helper functions 
//  skip forward, backward, or restart
function setTime(tValue) {
//  if no video is loaded, this throws an exception 
    try {
        if (tValue === 0) {
            video.currentTime = tValue;
        }
    else {
            video.currentTime += tValue;
        }
                        
    } catch (err) {
        // errMessage(err) // show exception
        errMessage("Video content might not be loaded");
    }
}
        

//  display an error message 
function errMessage(msg) {
        // displays an error message for 5 seconds then clears it
        document.getElementById("errorMsg").textContent = msg;
        setTimeout("document.getElementById('errorMsg').textContent=''", 5000);
}
        
// change volume based on incoming value 
function setVol(value) {
    var vol = video.volume;
    vol += value;
    //  test for range 0 - 1 to avoid exceptions
    if (vol >= 0 && vol <= 1) {
    // if valid value, use it
        video.volume = vol;
    } else {
        // otherwise substitute a 0 or 1
        video.volume = (vol < 0) ? 0 : 1;                        
    }
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