//Declarate functions
function showSender() { // Shows the form and changes the background color as the same as the one of the form
    console.log('mostrar');
    form.style.visibility = 'visible';
    uploadButton.style.backgroundColor = '#c9ddf4';
    uploadButton.disabled = true;
}

function activeteFilesButtons () { // Creates the listener for the new buttons generated (delete and open)
  document.querySelectorAll(".js-delete").forEach(element => {
    element.addEventListener("click", deleteFile)
  });
  document.querySelectorAll(".js-open").forEach(element => {
    element.addEventListener("click", openFile)});
    console.log(document.querySelectorAll(".js-delete"))
    console.log(document.querySelectorAll(".js-open"))
}

function hideSender() { // Hides the send form and changes colour to normal
    console.log('hide')
    form.style.visibility = 'hidden';
    uploadButton.style.backgroundColor = '#ffeccc';
    uploadButton.disabled = false;
}

function getFiles () {
  fetch('http://127.0.0.3:13001/files', {
    method: 'GET'}).then(response => response.json())
    .then(data => { // Generates html from the files available
      if (data.files.length === 0) {
        content.innerHTML = '<h1 class="files">Files</h1><h2 style="text-align:center">There are no files in the database</h2>';
      }
      else {
        content.innerHTML = '<h1 class="files">Files</h1>';
        data.files.forEach((pdfName) => {
          content.innerHTML += `
          <div class="fileContainer">
            <p>${pdfName}</p>
            <div class="fileButtons">
              <button class="button js-delete" pdf="${pdfName}">Delete</button>
              <button class="button js-open" pdf="${pdfName}">Open</button>
            </div>
          </div>`;
        })
      };
    activeteFilesButtons();
  });
}

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
  getFiles();
}

function deleteFile (event) {
  console.log('deleting')
  const pdfName = event.target.getAttribute('pdf')
  fetch('http://127.0.0.3:13001/remove_doc', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({'file_name':pdfName, 'clear_database':true}) // Send the files directly
  }).then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log(data);
      getFiles();
    }
  });
}

function openFile (event) {
  console.log('Se mostrará '+event.target.getAttribute('pdf'))
}

// Add listeners and eventListeners
const form = document.getElementsByClassName('js-fileForm')[0]
const content = document.getElementsByClassName('content')[0];

const uploadButton = document.getElementsByClassName("js-uploadButton")[0];
uploadButton.addEventListener("click", showSender);

const exitButton = document.getElementsByClassName("js-exit")[0];
exitButton.addEventListener("click", hideSender);

const sendButton = document.getElementsByClassName("js-sendButton")[0];
sendButton.addEventListener("click", uploadFiles);



// Initializing code
hideSender();
getFiles();