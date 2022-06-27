/****************************************************/
/* Aldebaran Project Hopias                         */
/* connection.js                                    */
/* Innovation - Protolab - mcaniot@aldebaran.com    */
/* Aldebaran Robotics (c) 2016 All Rights Reserved. */
/* This file is confidential.                       */
/****************************************************/

// New session naoqi

var started = 0;

var machine4
var machine5 
var machine6 

var m1
var m2
var m3

var session = new QiSession();

// Subscribe to the event "nameSubscribe"
function startSubscribe(nameSubscribe) {
    session.service("ALMemory").done(function (ALMemory) {
        ALMemory.subscriber(nameSubscribe).done(function(subscriber) {
            // Call the function "toTabletHandler" when a signal raised on the event.
            // This function is defined in the other js files.
            subscriber.signal.connect(startMachine);
        });    
    });
}

function sendToChoregraphe(response) {
    session.service("ALMemory").done(function (ALMemory) {
        console.log("ALMemory");
        ALMemory.raiseEvent("slotMachine", response);
    });    
}

function startMachine(value) { 
	//todo
	if (started == 0) {
		document.getElementById("win").style.display = 'none';
		document.getElementById("lose").style.display = 'none';
		started = 3;
		machine4.shuffle();
		machine5.shuffle();
		machine6.shuffle();
	}
	else {
		switch(started){
			case 3:
				m1 = machine4.stop();
				break;
			case 2:
				m2 = machine5.stop();
				break;
			case 1:
				m3 = machine6.stop();
				if (m1 == m2 && m1==m3){
					document.getElementById("win").style.display = 'block';
					sendToChoregraphe("win")
				}
				else{
					document.getElementById("lose").style.display = 'block';
					sendToChoregraphe("lose")
				}
				break;
		}
		started--;

	}

}

function startBouzin(){
	machine4 = $("#casino1").slotMachine({
		active	: 0,
		delay	: 500
	});

	machine5 = $("#casino2").slotMachine({
		active	: 1,
		delay	: 500
	});
	machine6 = $("#casino3").slotMachine({
		active	: 2,
		delay	: 500
	});

	$("#slotMachineButtonShuffle").click(function(){
		document.getElementById("win").style.display = 'none';
		document.getElementById("lose").style.display = 'none';
		started = 3;
		machine4.shuffle();
		machine5.shuffle();
		machine6.shuffle();
	});

	$("#slotMachineButtonStop").click(function(){
		switch(started){
			case 3:
				m1 = machine4.stop();
				break;
			case 2:
				m2 = machine5.stop();
				break;
			case 1:
				m3 = machine6.stop();
				if (m1 == m2 && m1==m3){
					document.getElementById("win").style.display = 'block';
					sendToChoregraphe("win")
				}
				else{
					document.getElementById("lose").style.display = 'block';
					sendToChoregraphe("lose")
				}
				break;
		}
		started--;
	});
}

