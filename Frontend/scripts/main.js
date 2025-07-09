// Functions
function newChat (send = false) {
    // Include the HTML to ask for the name of the new chat
    // Include the send attribute
    const popup = document.querySelector('.popup-container')
    popup.innerHTML = '';
}

function cancelNewChat () {
    document.querySelector('.popup-container').innerHTML = '';
}

function createChat (event) {
    // Creates the chat in the list
    if (event.target.getAttribute('send') === 'true') {
        sendMessage();
    }
}


function sendMessage() { // Sends a message to the RAG, and writes the answer
    const space = document.getElementsByClassName('js-chat-space')[0]
    const query = input.value.trim();
    if (!query) return;
    if (!chatSelected) {
        newChat(true);
        return;
    }
    console.log(space.innerHTML);
    // Add the query and delete it from the input
    space.innerHTML += `<div class="text-container-user">
							<p class="from-user">${query}</p>
							<img class="logo-ai" src="images/user.png">
						</div>`;
    input.value = ''
    button.disabled = true
    fetch('http://127.0.0.3:13001/query/' + mode, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
          },
        body: JSON.stringify({
            prompt: query,
            chat: chatSelected
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Retrieve the answer and references used by the LLM
            const answer = data.answer
            const references = data.references
            const answerHTML = `<div class="text-container-ai">
							<img class="logo-ai" src="images/robot.png">
							<p class="from-ai">${answer}</p>
						</div>`
            space.innerHTML += answerHTML
            if (references) {
                space.innerHTML += `<div class="references"><p>References: [${references}]</p></div>`
            }
            console.log(answer)
        }
        else { // We inform about the error
            alert("Error code: " + data.error_code + "\n Description: " + data.description);
        }
        button.disabled = input.value.trim() === ''
    })
    .catch(error => {
        const loading = document.getElementsByClassName('js-loading')[0]
        loading.innerHTML = ''
        console.error('Error in petition:', error);
    });
}

function loadPage () {
    fetch('http://127.0.0.3:13001/chats', {
    method: 'GET'}).then(response => response.json())
    .then(data => { // Generates html from the chats available
        if (!data.success) { // Something did not work
            alert("Error code: " + data.error_code + "\n Description: " + data.description);
            return
        }
        if (data.chats.length === 0) {
            
        }
        else {;
        
        };
        // We add a new chat
        chatSpace.innerHTML =  `<div class="text-container-ai">
                                        <img class="logo-ai" src="images/robot.png">
                                        <p class="from-ai">Ask me something about the files uploaded (:</p>
                                    </div>`;
    });
    }

function loadConversation (conversation) {
    conversation.forEach((chat) => {
        const name = chat.name;
        const conversation = chat.conversation;
        conversation.forEach((comment) => {
            if (comment.role === "user") { // We add the user comment
                chatSpace.innerHTML += `
                <div class="text-container-user">
                        <p class="from-user">${content}</p>
                        <img class="logo-ai" src="images/user.png">
                    </div>`;
            }
            else if (comment.role === "assistant") { // 
                chatSpace.innerHTML += `
                <div class="text-container-ai">
                    <img class="logo-ai" src="images/robot.png">
                    <p class="from-ai">${comment.content}</p>
                </div>`
                if (references) {
                chatSpace.innerHTML += `<div class="references"><p>References: [${comment.references}]</p></div>`;
                }
            }
            else {
                alert('Unexpected role: ' + comment.role)
            }
            
        })
    })
}

// Declaration of elements
let mode = 'RAG'; // Mode of the app selected
let chatSelected = undefined; // Which chat is selected
const input = document.getElementById('js-input');
const button = document.getElementById('js-send-button');
const chatSpace = document.getElementById('chat-space');
const newChatExit = document.querySelector('.new-chat .exit');

// Listeners
input.addEventListener('input', () => { // Listener for the input to disable the button
    console.log('input:'+input.value.trim())
    button.disabled = input.value.trim() === '';
});
button.addEventListener('click', sendMessage); // Listener for sending a message
document.querySelectorAll('.navbar .title-left').forEach(() => { // Listener for modes buttons
    addEventListener('click', (event) => {
        mode = event.target.getAttribute('id')
    })
})

// Popup listeners
newChatExit.addEventListener('click', cancelNewChat)

// Code to initialize page correctly

button.disabled = input.value.trim() === '';



