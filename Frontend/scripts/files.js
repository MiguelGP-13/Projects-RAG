// Add listener to the form and make it invisible
const form = document.getElementById('fileForm')
hideSender();


const uploadButton = document.getElementById("js-uploadButton");
uploadButton.addEventListener("click", showSender);

const exitButton = document.getElementById("js-exit");
exitButton.addEventListener("click", hideSender);


function showSender() {
    form.style.visibility = 'visible';
}

function hideSender() {
    form.style.visibility = 'hidden';
}




// Add event listener to the button element
const sendButton = document.getElementById("js-sendButton");
sendButton.addEventListener("click", uploadFiles);

function uploadFiles(event) {
    event.preventDefault();
    const fileInput = document.getElementById("fileInput");
    const selectedFiles = fileInput.files;
    // Check if any files are selected
    if (selectedFiles.length === 0) {
      alert("Please select at least one file to upload.");
      return;
    }
    // Create a FormData object to store the form data
    const formData = new FormData();
    // Append each selected file to the FormData object
    for (let i = 0; i < selectedFiles.length; i++) {
        formData.append("files[]", selectedFiles[i]);
    }
    // Send message to python backend with FormData
    fetch('http://127.0.0.3:13001/upload', {
        method: 'POST',
        body: formData // Send the files directly
    }).then(response => response.json())
    .then(data => {
      if (data.success) {
        console.log(data)
        // Clean file input
        document.getElementById("fileInput").value = "";
        console.log("Archivos subidos correctamente!");
      }
    });
    hideSender();
}

