const input = document.getElementById('js-input');
const button = document.getElementById('js-send-button');
const chatSpace = document.getElementById('chat-space');

button.disabled = input.value.trim() === '';

input.addEventListener('input', () => {
    console.log('input:'+input.value.trim())
    button.disabled = input.value.trim() === '';
});

button.addEventListener('click', sendMessage);


function sendMessage() {
    const space = document.getElementsByClassName('js-chat-space')[0]
    const query = input.value.trim();
    if (!query) return;
    console.log(space.innerHTML);
    // Add the query and delete it from the input
    space.innerHTML += `<div class="text-container-user">
							<p class="from-user">${query}</p>
							<img class="logo-ai" src="images/user.png">
						</div>`;
    input.value = ''
    button.disabled = true
    // const loading = document.getElementById('loading');
    // loading.style.display = 'block'; // ← Show loading
    // Send message to python backend
    fetch('http://127.0.0.3:13001/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
          },
        body: JSON.stringify({
            prompt: query,
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Retrieve the answer and references used byt LLM
            const answer = data.answer
            const references = data.references
            const answerHTML = `<div class="text-container-ai">
							<img class="logo-ai" src="images/robot.png">
							<p class="from-ai">${answer}</p>
						</div>
						<div class="references"><p>References: [${references}]</p></div>
						`
            space.innerHTML += answerHTML
            console.log(answer)
        }
        else {
            alert(data.error_code + ': ' + data.description);
        }
        button.disabled = input.value.trim() === ''
    })
    .catch(error => {
        const loading = document.getElementsByClassName('js-loading')[0]
        loading.innerHTML = ''
        console.error('Error in petition:', error);
    });
}
