function getColorFromValue(value, max = 10) { // For the grade colouring
  const percentage = Math.max(0, Math.min(value / max, 1)); // Clamp between 0 and 1
  const hue = percentage * 100; // 0 = red, 120 = green
  return `hsl(${hue}, 100%, 50%)`;
}


function downloadHTML() { // To download the HTML
    const htmlContent = document.documentElement.outerHTML;
    const blob = new Blob([htmlContent], { type: 'text/html' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    const title = document.querySelector("#quiz-title").innerHTML;
    link.download = title + '.html';
    link.click();
}

function buildQuestionnaire (data) {
    let html = '';
    let nQuestion = 0; // To track which question is being added
    let correctOptions = []
    data.forEach(question => { // For each question we write the question and we add the options in a HTML form
        html += `<p class="js-question">${nQuestion + 1}. ${question.question}</p><form class="js-question-form question-form" id="question-${nQuestion}" data-question-id="${nQuestion}">`
        let nOption = 0;
        question.options.forEach(option => {
            html += `
                        <input type="radio" name="${nQuestion}" id="option-${nQuestion}-${nOption}" data-option-id="${nOption}">
                        <label for="option-${nQuestion}-${nOption}" data-label-option-id="${nOption}">${option}</label><br>
                    `
            nOption += 1;
        });
        nQuestion += 1;
        html += '</form><br>'
        correctOptions.push(question.correctOption)
    });

    console.log(correctOptions)
    return {html, correctOptions}
}

function submitQuiz () {
  console.log('grading');
    let grade = 0;
    document.querySelectorAll('#content .js-question-form').forEach( questionForm => {
        let selectedOption = questionForm.querySelector('input[type="radio"]:checked');
        // console.log(selectedOption);
        if (selectedOption) {
			const labelSelectedOption = questionForm.querySelector(`label[data-label-option-id="${selectedOption.dataset.optionId}"]`);
            console.log(parseInt(selectedOption.dataset.optionId), correctOptions[parseInt(questionForm.dataset.questionId)]);
            if (parseInt(selectedOption.dataset.optionId) === correctOptions[parseInt(questionForm.dataset.questionId)]) { // Correct answer
                labelSelectedOption.style.backgroundColor = "#d4edda";
                grade += 1;
            }
            else { // Incorrect
                console.log(`label[data-label-option-id="${correctOptions[parseInt(questionForm.dataset.questionId)]}"]`);
                const correct = questionForm.querySelector(`label[data-label-option-id="${correctOptions[parseInt(questionForm.dataset.questionId)]}"]`);
                correct.style.backgroundColor = "#d4edda";
                labelSelectedOption.style.backgroundColor = "#f8d7da";
            }
        }
        else { // Not answered
            const correct = questionForm.querySelector(`label[data-label-option-id="${correctOptions[parseInt(questionForm.dataset.questionId)]}"]`);
            correct.style.backgroundColor = "#d4edda";
        }
    });
    const Finalgrade = grade/quizData.length*10
    console.log(grade + "/" + quizData.length, Finalgrade)
    gradeDisclaimer.innerHTML = `Grade: ${Math.round(Finalgrade*100)/100}/10`; // Only 2 decimals
    gradeDisclaimer.style.color = getColorFromValue(Finalgrade);
}

function clearQuiz() {
  document.querySelectorAll('input[type="radio"]:checked').forEach((radio) => {
    radio.checked = false;
  });
  gradeDisclaimer.innerHTML = ''
  document.querySelectorAll('label').forEach((label) => {
    label.style.backgroundColor = '';
  });
}
// 
// window.addEventListener('beforeunload', (event) => { // Update the questionnaire name
//     fetch('http://' + apiHost + ':13001/saveQuestionnaireName' , {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//           },
//         body: JSON.stringify({
//             "name":document.querySelector("#quiz-title").innerHTML
//         }),
//     })
//     .catch(()=>alert('Backend api not ready, beforeunload'))
// });
const title = document.getElementById("quiz-title");

  title.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();         // Prevent new line
      title.blur();               // Remove focus to end editing
    }
  });


// Initialize page
const apiHost = 'localhost'; // It runs on the browser
let quizData = null;
let correctOptions = null;
content = document.querySelector('#content');
gradeDisclaimer = document.querySelector('.grade');

const params = new URLSearchParams(window.location.search);
const quizId = params.get('id');
fetch('http://' + apiHost + ':13001/questionnaire/'+quizId, {
    method: 'GET'})
    .then(response => response.json()).catch(() => alert('Backend API not ready, loadQuestionnaire'))
    .then(data => { 
      if (data.success) {
        quizData = data.questions;
        const {html, correctOptions: c } = buildQuestionnaire(quizData);
        correctOptions = c;
        console.log(correctOptions, c)
        content.innerHTML = html;
      }
      else {
        alert("Error code: " + data.error_code + "\n Description: " + data.description);
      }
      })