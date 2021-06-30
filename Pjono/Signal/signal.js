// signal.js for sending event and message to server in real-time

class PjSignal{

    constructor(){ // Initiliaze
        this.client = new XMLHttpRequest();
    }
    
    fireEvent(name, message, action){ // Function for firing event with message to the server
        this.client.onload = function(){
            action(this.responseText, this.status);
        };
        this.client.open("POST", window.location.pathname, true);
        this.client.setRequestHeader("PjEvent", name);
        this.client.setRequestHeader("Pjmsg", message);
        this.client.send();
    }
}