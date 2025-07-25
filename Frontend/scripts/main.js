// Functions
function cleanName (text) { // Encode spaces as %20
    text = text.replace(/\./g, '%2E');
    return text.replace(/ /g, '%20');
}
// function returnSpaces (text) { // Unencode spaces previously converted to %20
//     return text.replace(/%20/g, ' ');
// }


function popupNewChat (send = false) {
    // Include the HTML to ask for the name of the new chat
    // Include the send attribute
    popup.innerHTML = `                        
                    <div class="popup">
                        <div class="new-chat">
                            <h1>Name the new chat:</h1>
                            <div class="input">
                                <div>
                                    <input maxlength="15" placeholder="New name", class="js-new-chat-input">
                                </div>
                                <button class="send-new-chat js-send-new-chat" send="${send}">Send</button>
                            </div>
                            <button class="exit js-exit"><img class="closeImg" src="images/close.png"></button>
                        </div>
                    </div>`;

    // Popup listeners
    document.querySelector('.new-chat .js-exit').addEventListener('click', hidePopup); // Exit button
    document.querySelector('.js-send-new-chat').addEventListener('click',createChat); // Send button
    newChatInput = document.querySelector('.new-chat .js-new-chat-input') 
}

function hidePopup () {
    console.log('Hiding popup')
    popup.innerHTML = '';
}

function createChatSelector(realName, id) {
    const button = document.createElement("button");
    button.classList.add("chat");
    button.id = id;
    button.innerHTML = `
        <p>${realName}</p>
        <img src="images/closedBin.png" class="delete-chat" chat="${id}">`;
    // Insert at the top
    openChats.insertBefore(button, openChats.firstChild);
    requestAnimationFrame(() => {
        console.log("Button " + button.id + " was registered");
        button.addEventListener('click', () => {
            selectChat(id);
        });
        const deleteButton = button.querySelector('.delete-chat');
        deleteButton.addEventListener('mouseover', () => {
            deleteButton.src = 'images/openBin.png';
        });
        deleteButton.addEventListener('mouseout', () => {
            deleteButton.src = 'images/closedBin.png';
        });
        deleteButton.addEventListener('click', deleteChat);
    });
}


function createChat (event) {
    console.log('send new chat clicked: '+ event.target)
    const realName = newChatInput.value.trim();
    const cleanedName = cleanName(realName); // Not to have errors with the URL
    fetch('http://' + apiHost + ':13001/createChat/' + cleanedName, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
          },
        body: JSON.stringify({}),
    })
    .then(response => response.json()).catch(()=>alert('Backend api not ready, createChat'))
    .then(data => {
        if (data.success) {
            // Create the button to select the chat
            createChatSelector(realName, data.id)
            // Remove the popup 
            hidePopup();            
            // Select the new chat
            selectChat(data.id);
            // Send message if required (you got here pressing button send)
            if (event.target.getAttribute('send') === 'true') {
                console.log('Entra')
                sendMessage();
            }
        }
        // Alert of errors
        else {
            if (data.error_code === 107) {
                alert("The name can't have a dot (.)")
            }
            else if (data.error_code === 106) {
                alert("There is a chat with that name alredy, please change it")
            }
            else if (data.error_code === 108) {
                alert("The name can't start with a number")
            }
            else if (data.error_code === 109) {
                alert("The name can't be empty")
            }
            else {alert(`Unexpected error ${data.error_code}: ${data.description}`)}
        }
    })
}

function deleteChat (event) { // We delete the chat with the same id as the button pressed
    // Send the backend the order to delete that chat
    fetch('http://' + apiHost + ':13001/deleteChat/' + event.currentTarget.getAttribute('chat'), {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
          },
        body: JSON.stringify({}),
    })
    .then(response => response.json()).catch(()=>alert('Backend api not ready, createChat'))
    .then(data => {
        if (data.success) {
            chatSelected = undefined; // Select no chat
            localStorage.removeItem("chatSelected");
            console.log('deleting chat')
            loadPage();
            console.log('page loaded')
        }
        // Alert of errors
        else {
            if (data.error_code === 105) {
                console.log("Chat doesn't exist alredy")
                chatSelected = undefined; // Select no chat
                localStorage.removeItem("chatSelected");
                loadPage();
            }
            else {alert(`Unexpected error ${data.error_code}: ${data.description}`)}
        }
    })
}

function sendMessage() { // Sends a message to the RAG, and writes the answer
    const space = document.getElementsByClassName('js-chat-space')[0]
    const query = input.value.trim();
    if (!query) return;
    if (!chatSelected) {
        popupNewChat(true);
        return;
    }
    // Add the query and delete it from the input
    space.innerHTML += `<div class="text-container-user">
							<p class="from-user">${query}</p>
							<img class="logo-ai" src="images/user.png">
						</div>`;
    input.value = ''
    button.disabled = true
    fetch('http://' + apiHost + ':13001/query/' + mode, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
          },
        body: JSON.stringify({
            prompt: query,
            chat: chatSelected
        }),
    })
    .then(response => response.json()).catch(() => alert('Backend api not ready, sendMessage'))
    .then(data => {
        if (data.success) {
            console.log(data);
            // Retrieve the answer and references used by the LLM
            const answer = data.answer;
            const references = data.references;
            let robotImage = undefined; // Choose the right image
            if (mode === 'RAG') {
                robotImage = "images/robot_docs.png";
            }
            else if (mode === 'chat') {
                robotImage = "images/robot.png";
            }
            else {
                alert('Mode error!!' + mode);
                return;
            }
            const answerHTML = `<div class="text-container-ai">
							<img class="logo-ai" src="${robotImage}">
							<div class="from-ai">${answer}</div>
						</div>`;
            space.innerHTML += answerHTML;
            if (references) {
                space.innerHTML += `<div class="references"><p>References: [${references}]</p></div>`;
            }
            console.log('LLM answer' + answer);
        }
        else { // We inform about the error
            alert("Error code: " + data.error_code + "\n Description: " + data.description);
        }
        button.disabled = input.value.trim() === ''
    })
    .catch(error => {
        console.error('Error in petition:', error);
    });
}

function loadPage () {
    fetch('http://' + apiHost + ':13001/chats', {
    method: 'GET'})
    .then(response => response.json()).catch(() => alert('Backend API not ready, loadPage'))
    .then(data => { // Generates html from the chats available
        console.log("Chats received: " + data);
        if (!data.success) { // Something did not work
            alert("Error code: " + data.error_code + "\n Description: " + data.description);
            return
            }
        
        // Create the chat buttons at the navbar
        openChats.innerHTML = ''
        data.chats.forEach((element) => {
            createChatSelector(element.realName, element.id)
        })
        console.log(chatSelected);
        if (chatSelected) {
            selectChat(chatSelected)
        }
        else {
            console.log('Borrado');
            // We open a new chat if no chat is selected 
            chatSpace.innerHTML =  `
            <div class="text-container-ai">
                <img class="logo-ai" src="images/robot.png">
                <div class="from-ai">Ask me something about the files uploaded (:</div>
            </div>`;
        }
    });
    }

function loadConversation (id) {
    fetch('http://' + apiHost + ':13001/chats/' + id, {
        method: 'GET'})
    .then(response => response.json()).catch(() => alert('Backend api not ready, loadConversation'))
    .then(data => {
        console.log(data)
        console.log("Conversation with name " + id + " received: " + data)
        if (data.success) {
            if (data.chat.conversation.length === 0) {
                chatSpace.innerHTML =  `
                    <div class="text-container-ai">
                        <img class="logo-ai" src="images/robot.png">
                        <div class="from-ai">Ask me something about the files uploaded (:</div>
                    </div>`;
            }
            else {
                chatSpace.innerHTML = '';
                const name = data.chat.name;
                const conversation = data.chat.conversation;
                conversation.forEach((comment) => {
                    if (comment.role === "user") { // We add the user comment
                        chatSpace.innerHTML += `
                        <div class="text-container-user">
                                <p class="from-user">${comment.content}</p>
                                <img class="logo-ai" src="images/user.png">
                            </div>`;
                    }
                    else if (comment.role === "assistant") { // We add the assistant comment
                        let robotImage = undefined; // Choose the right image
                        if (comment.mode === 'RAG') {
                            robotImage = "images/robot_docs.png";
                        }
                        else if (comment.mode === 'chat') {
                            console.log('chat')
                            robotImage = "images/robot.png";
                        }
                        else {
                            alert('Mode error!!' + mode);
                            console.log('Mode not found: '+mode)
                            return;
                        }
                        chatSpace.innerHTML += `
                        <div class="text-container-ai">
                            <img class="logo-ai" src="${robotImage}">
                            <div class="from-ai">${comment.content}</div>
                        </div>`
                        if (comment.references) {
                        chatSpace.innerHTML += `<div class="references"><p>References: ${comment.references} </p></div>`;
                        }
                    }
                    else {
                        alert('Unexpected role: ' + comment.role)
                    }
                        
                })
            }
            
        }
        else if (data.error_code === 105) { // Error with chatSelected doesn't exist, we unselect it and reload the page
            console.log('Conversation not found')
            chatSelected = undefined;
            localStorage.removeItem("chatSelected");
            loadPage();
        }
        else {alert(`Unexpected error ${data.error_code}: ${data.description}`)}
    })
}

function selectChat (id) {
    console.log('selectChat clicked on button: ' + id)
    const oldSelected = document.querySelector(".chat#" + chatSelected);
    if (oldSelected) {
        oldSelected.classList.remove("active");
        oldSelected.disabled = false;
    }
    const newSelected = document.querySelector(".chat#" + id);
    newSelected.classList.add("active"); 
    newSelected.disabled = true;
    chatSelected = id;
    loadConversation(id);
    localStorage.setItem("chatSelected", chatSelected);
}

function selectMode (newMode) {
    console.log("New mode selected: " + newMode);
    const oldSelected = document.querySelector(".navbar .title-left#" + mode);
    if (oldSelected) {
        oldSelected.classList.remove("active");
        oldSelected.disabled = false;
    }
    
    const newSelected = document.querySelector(".navbar .title-left#" + newMode);
    newSelected.classList.add("active");  
    newSelected.disabled = true;
    mode = newMode;

}

function popupNewQuestionnaire () {
    // selectMode
    selectMode('questionnaire');
    
    if (!files) { // Cancel button was clicked
        selectMode('RAG');
    }
    else {
        // We create the questionnaire and load it in the page
        createQuestionnaire(files);
    }

    //
}


// Declaration of elements
let mode = undefined; // Mode of the app selected
let chatSelected = localStorage.getItem("chatSelected"); // Which chat is selected
let newChatInput = undefined; // Will be defined when the newChat popup appears
const input = document.querySelector('.js-input');
const button = document.querySelector('.js-send-button');
const chatSpace = document.querySelector('.js-chat-space');
const openChats = document.querySelector('.open-chats');
const newChatButton = document.querySelector('.js-new-chat-button');
const popup = document.querySelector('.popup-container');

// Listeners
input.addEventListener('input', () => { // Listener for the input to disable the button
    button.disabled = input.value.trim() === '';
});
button.addEventListener('click', sendMessage); // Listener for sending a message

document.querySelectorAll('.navbar .js-title-left').forEach((element) => { // Listener for modes buttons
    if (element.getAttribute('id') === "questionnaire"){
        element.addEventListener('click', popupNewQuestionnaire);
    }
    else {
        element.addEventListener('click', (event) => {
            selectMode(event.currentTarget.getAttribute('id'));
        })
    }
})

newChatButton.addEventListener('click', popupNewChat)


// Code to initialize page correctly
const apiHost = 'localhost'; // It runs on the browser
selectMode('RAG');
loadPage();
button.disabled = input.value.trim() === '';



