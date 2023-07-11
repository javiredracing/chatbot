/*
Makes backend API call to rasa chatbot and display output to chatbot frontend
*/

function init() {

    //---------------------------- Including Jquery ------------------------------

    var script = document.createElement('script');
    script.src = 'https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js';
    script.type = 'text/javascript';
    document.getElementsByTagName('head')[0].appendChild(script);

    //--------------------------- Important Variables----------------------------
    botLogoPath = "./imgs/bot-logo.png"

    //--------------------------- Chatbot Frontend -------------------------------
    const chatContainer = document.getElementById("chat-container");

    template = ` <button class='chat-btn'><img src = "./icons/comment.png" class = "icon" ></button>

    <div class='chat-popup'>
    
		<div class='chat-header'>
			<div class='chatbot-img'>
				<img src='${botLogoPath}' alt='Chat Bot image' class='bot-img'> 
			</div>
			<h3 class='bot-title'>ITER Bot</h3>
			<button class = "expand-chat-window" ><img src="./icons/open_fullscreen.png" class="icon" ></button>
		</div>

		<div class='chat-area'>
            <div class='bot-msg'>
                <img class='bot-img' src ='${botLogoPath}' />
				<span class='msg'>Hi, How can i help you?</span>
			</div>

            <!-- <div class='bot-msg'>
                <img class='bot-img' src ='${botLogoPath}' />
                <div class='response-btns'>
                    <button class='btn-primary' onclick= 'userResponseBtn(this)' value='/sign_in'>sample btn</button>            
                </div>
			</div> -->

			<!-- <div class='bot-msg'>
				<img class='msg-image' src = "https://i.imgur.com/nGF1K8f.jpg" />
			</div> -->

			<!-- <div class='user-msg'>
				<span class='msg'>Hi, How can i help you?</span>
			</div> -->
			

		</div>


		<div class='chat-input-area'>
			<input type='text' autofocus class='chat-input' onkeypress='return givenUserInput(event)' placeholder='Type a message ...' autocomplete='off'>
			<button class='chat-submit'><i class='material-icons'>send</i></button>
		</div>

	</div>`


    chatContainer.innerHTML = template;

    //--------------------------- Important Variables----------------------------
    var inactiveMessage = "Server is down, Please contact the developer to activate it"


    chatPopup = document.querySelector(".chat-popup")
    chatBtn = document.querySelector(".chat-btn")
    chatSubmit = document.querySelector(".chat-submit")
    chatHeader = document.querySelector(".chat-header")
    chatArea = document.querySelector(".chat-area")
    chatInput = document.querySelector(".chat-input")
    expandWindow = document.querySelector(".expand-chat-window")
    root = document.documentElement;
    chatPopup.style.display = "none"
    var host = ""


    //------------------------ ChatBot Toggler -------------------------

    chatBtn.addEventListener("click", () => {

        mobileDevice = !detectMob()
        if (chatPopup.style.display == "none" && mobileDevice) {
            chatPopup.style.display = "flex"
            chatInput.focus();
            chatBtn.innerHTML = `<img src = "./icons/close.png" class = "icon" >`
        } else if (mobileDevice) {
            chatPopup.style.display = "none"
            chatBtn.innerHTML = `<img src = "./icons/comment.png" class = "icon" >`
        } else {
            mobileView()
        }
    })

    chatSubmit.addEventListener("click", () => {
        let userResponse = chatInput.value.trim();
        if (userResponse !== "") {
            setUserResponse();
            send(userResponse)
			
        }
    })

    expandWindow.addEventListener("click", (e) => {
        // console.log(expandWindow.innerHTML)
        if (expandWindow.innerHTML == '<img src="./icons/open_fullscreen.png" class="icon">') {
            expandWindow.innerHTML = `<img src = "./icons/close_fullscreen.png" class = 'icon'>`
            root.style.setProperty('--chat-window-height', 80 + "%");
            root.style.setProperty('--chat-window-total-width', 85 + "%");
        } else if (expandWindow.innerHTML == '<img src="./icons/close.png" class="icon">') {
            chatPopup.style.display = "none"
            chatBtn.style.display = "block"
        } else {
            expandWindow.innerHTML = `<img src = "./icons/open_fullscreen.png" class = "icon" >`
            root.style.setProperty('--chat-window-height', 500 + "px");
            root.style.setProperty('--chat-window-total-width', 380 + "px");
        }

    })
}

// end of init function



var passwordInput = false;

function userResponseBtn(e) {
    send(e.value);
}

// to submit user input when he presses enter
function givenUserInput(e) {
    if (e.keyCode == 13) {
        let userResponse = chatInput.value.trim();
        if (userResponse !== "") {
            setUserResponse()
            send(userResponse)
        }
    }
}

// to display user message on UI
function setUserResponse() {
    let userInput = chatInput.value;
    if (passwordInput) {
        userInput = "******"
    }
    if (userInput) {
        let temp = `<div class="user-msg"><span class = "msg">${userInput}</span></div>`
        chatArea.innerHTML += temp;
        chatInput.value = ""
    } else {
        chatInput.disabled = false;
    }
    scrollToBottomOfResults();
}



function scrollToBottomOfResults() {
    chatArea.scrollTop = chatArea.scrollHeight;
}

/***************************************************************
Frontend Part Completed
****************************************************************/
// host socket: http://localhost:5005/socket.io
function send(message) {
    chatInput.type = "text"
    passwordInput = false;
    chatInput.focus();    
	socket.emit('user_uttered', {
		'message': message,
		'session_id': getSessionId(),
	});
    chatInput.focus();
}


//------------------------------------ Set bot response -------------------------------------
function setBotResponse(val) {
    setTimeout(function() {
        if (val.length < 1) {
            //if there is no response from Rasa
            // msg = 'I couldn\'t get that. Let\' try something else!';
            msg = inactiveMessage;

            var BotResponse = `<div class='bot-msg'><img class='bot-img' src ='${botLogoPath}' /><span class='msg'> ${msg} </span></div>`;
            $(BotResponse).appendTo('.chat-area').hide().fadeIn(1000);
            scrollToBottomOfResults();
            chatInput.focus();

        } else {
            //if we get response from Rasa
			//check if there is text message
			if (val.hasOwnProperty("text")) {
				const botMsg = val.text;
				if (botMsg.includes("password")) {
					chatInput.type = "password";
					passwordInput = true;
				}
				var BotResponse = `<div class='bot-msg'><img class='bot-img' src ='${botLogoPath}' /><span class='msg'>${val.text}</span></div>`;
				$(BotResponse).appendTo('.chat-area').hide().fadeIn(1000);
			}

			//check if there is image
			if (val.hasOwnProperty("image")) {
				var BotResponse = "<div class='bot-msg'>" + "<img class='bot-img' src ='${botLogoPath}' />"
				'<img class="msg-image" src="' + val.image + '">' +
					'</div>'
				$(BotResponse).appendTo('.chat-area').hide().fadeIn(1000);
			}

			//check if there are buttons
			if (val.hasOwnProperty("buttons")) {
				var BotResponse = `<div class='bot-msg'><img class='bot-img' src ='${botLogoPath}' /><div class='response-btns'>`

				buttonsArray = val.buttons;
				buttonsArray.forEach(btn => {
					BotResponse += `<button class='btn-primary' onclick= 'userResponseBtn(this)' value='${btn.payload}'>${btn.title}</button>`
				})

				BotResponse += "</div></div>"

				$(BotResponse).appendTo('.chat-area').hide().fadeIn(1000);
				chatInput.disabled = true;
			}

		}
		scrollToBottomOfResults();
		chatInput.disabled = false;
		chatInput.focus();

    }, 500);
}

/*****/
function getSessionId() {
	const storage = localStorage;
	const storageKey = 'RASA_SESSION_ID';
	const savedId = storage.getItem(storageKey);
	if (savedId) {
		console.log(savedId);
		return savedId;
	}
	const newId = socket.id;
	storage.setItem(storageKey, newId);
	return newId;
}

function mobileView() {
    $('.chat-popup').width($(window).width());

    if (chatPopup.style.display == "none") {
        chatPopup.style.display = "flex"
            // chatInput.focus();
        chatBtn.style.display = "none"
        chatPopup.style.bottom = "0"
        chatPopup.style.right = "0"
            // chatPopup.style.transition = "none"
        expandWindow.innerHTML = `<img src = "./icons/close.png" class = "icon" >`
    }
}

function detectMob() {
    return ((window.innerHeight <= 800) && (window.innerWidth <= 600));
}

function chatbotTheme(theme) {
    const gradientHeader = document.querySelector(".chat-header");
    const orange = {
        color: "#FBAB7E",
        background: "linear-gradient(19deg, #FBAB7E 0%, #F7CE68 100%)"
    }
	
	const iterColor = {
        color: "#87b09a",
        background: "linear-gradient(19deg, #6c7572 0%, #87b09a 100%)"
    }

    const purple = {
        color: "#B721FF",
        background: "linear-gradient(19deg, #21D4FD 0%, #B721FF 100%)"
    }

    if (theme === "orange") {
        root.style.setProperty('--chat-window-color-theme', orange.color);
        gradientHeader.style.backgroundImage = orange.background;
        chatSubmit.style.backgroundColor = orange.color;
    } else if (theme === "purple") {
        root.style.setProperty('--chat-window-color-theme', purple.color);
        gradientHeader.style.backgroundImage = purple.background;
        chatSubmit.style.backgroundColor = purple.color;
    } else if (theme === "iterColor") {
        root.style.setProperty('--chat-window-color-theme', iterColor.color);
        gradientHeader.style.backgroundImage = iterColor.background;
        chatSubmit.style.backgroundColor = iterColor.color;
    }
}

function createChatBot(botLogo, title, welcomeMessage, inactiveMsg, theme = "blue") {

    botLogoPath = botLogo;
    inactiveMessage = inactiveMsg;
    init()
    const msg = document.querySelector(".msg");
    msg.innerText = welcomeMessage;

    const botTitle = document.querySelector(".bot-title");
    botTitle.innerText = title;

    chatbotTheme(theme)
}
const path = "/socket.io/"
const socketUrl = "http://localhost:5005"
const options = path ? { path } : {};
const socket = io(socketUrl, options);

//console.log(socket);

socket.on("disconnect", () => {
  //console.log(socket.id);
	
});

socket.on('connect', () =>{
	console.log('Connected to Socket.io server.');
	socket.emit('session_request', {
		'session_id': getSessionId(),
	});
	console.log(`Session ID: ${getSessionId()}`);
});

socket.on('connect_error', (error) => {
	// Write any connection errors to the console 
	console.error(error);
});

socket.on('bot_uttered',  (response) =>{
	console.log('Bot uttered:', response);
	setBotResponse(response);
});