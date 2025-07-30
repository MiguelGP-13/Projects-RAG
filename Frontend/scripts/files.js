//Declarate functions
function showSender() { // Shows the form and changes the background color as the same as the one of the form
    console.log('mostrar');
    form.style.visibility = 'visible';
    uploadButton.style.backgroundColor = '#c9ddf4';
    uploadButton.disabled = true;
}

function activeteFilesButtons () { // Creates the listener for the new buttons generated (delete and open)
  document.querySelectorAll(".js-delete-file").forEach(element => {
    element.addEventListener("click", deleteFile)
  });
  document.querySelectorAll(".js-open-file").forEach(element => {
    element.addEventListener("click", openFile)});
    console.log(document.querySelectorAll(".js-delete-file"))
    console.log(document.querySelectorAll(".js-open-file"))
}

function hideSender() { // Hides the send form and changes colour to normal
    console.log('hide')
    form.style.visibility = 'hidden';
    uploadButton.style.backgroundColor = '#ffeccc';
    uploadButton.disabled = false;
}

function getFiles () {
  fetch('http://' + apiHost + ':13001/files', {
    method: 'GET'}).then(response => response.json()).catch(() => alert('Backend api not ready, getFiles'))
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
              <button class="button js-delete-file" pdf="${pdfName}">Delete</button>
              <button class="button js-open-file" pdf="${pdfName}">Open</button>
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
  fetch('http://' + apiHost + ':13001/upload', {
      method: 'POST',
      body: formData // Send the files directly
  }).then(response => response.json()).catch(() => alert('Backend api not ready, uploadFiles'))
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
  fetch('http://' + apiHost + ':13001/remove_doc', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({'file_name':pdfName, 'clear_database':true}) // Send the files directly
  }).then(response => response.json()).catch(() => alert('Backend api not ready, deleteFile'))
  .then(data => {
    if (data.success) {
      console.log(data);
      getFiles();
    }
  });
}

function openFile(event) {
  const filename = event.target.getAttribute('pdf');
  console.log('Se mostrará ' + filename);

  fetch('http://' + apiHost + ':13001' + `/file/${filename}`).catch(() => alert('Backend api not ready, openFile'))
    .then(response => {
      if (response.success === false) {
        alert('Error');
      }
      return response.blob(); // Convert to binary
    })
    .then(blob => {
      const fileURL = URL.createObjectURL(blob);
      window.open(fileURL, '_blank'); // Open PDF in new tab
    })
    .catch(error => {
      console.error('Error al mostrar el archivo:', error);
    });
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
const apiHost = 'localhost';
hideSender();
getFiles();