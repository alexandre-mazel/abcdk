
// New session naoqi
var session = new QiSession();

function sendToChoregraphe(response, sound) {
    session.service("ALMemory").done(function (ALMemory) {
        console.log("ALMemory");
        ALMemory.raiseEvent("tabletResponse", response);
        ALMemory.raiseEvent("soundEvent", sound)
    });    
}