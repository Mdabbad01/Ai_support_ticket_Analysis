const questionInput = document.getElementById("question");

const askButton = document.getElementById("askButton");

const loading = document.getElementById("loading");

const resultSection = document.getElementById("resultSection");

const errorSection = document.getElementById("error");

const errorMessage = document.getElementById("errorMessage");

const questionResult = document.getElementById("questionResult");

const answerResult = document.getElementById("answerResult");

const queryPlan = document.getElementById("queryPlan");

const exampleQuestions = document.querySelectorAll(
    ".example-question"
);


// --------------------------------------------------
// ASK QUESTION
// --------------------------------------------------

async function askQuestion() {

    const question = questionInput.value.trim();


    if (!question) {

        showError("Please enter a question.");

        return;

    }


    // Reset UI

    hideError();

    resultSection.classList.add("hidden");

    loading.classList.remove("hidden");

    askButton.disabled = true;


    try {

        const response = await fetch("/query", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question
            })

        });


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail || "Something went wrong."
            );

        }


        displayResult(data);


    } catch (error) {

        showError(error.message);

    } finally {

        loading.classList.add("hidden");

        askButton.disabled = false;

    }

}


// --------------------------------------------------
// DISPLAY RESULT
// --------------------------------------------------

function displayResult(data) {

    questionResult.textContent = data.question;


    const result = data.result;


    // COUNT

    if (result.count !== undefined) {

        answerResult.textContent =
            result.count + " tickets";

    }


    // AVERAGE

    else if (result.average !== undefined) {

        answerResult.textContent =
            result.average;

    }


    // SUM

    else if (result.sum !== undefined) {

        answerResult.textContent =
            result.sum;

    }


    // MIN

    else if (result.min !== undefined) {

        answerResult.textContent =
            result.min;

    }


    // MAX

    else if (result.max !== undefined) {

        answerResult.textContent =
            result.max;

    }


    // GROUP COUNT

    else if (result.groups !== undefined) {

        answerResult.textContent =
            JSON.stringify(
                result.groups,
                null,
                2
            );

    }


    // LIST

    else if (result.rows !== undefined) {

        answerResult.textContent =
            JSON.stringify(
                result.rows,
                null,
                2
            );

    }


    else {

        answerResult.textContent =
            JSON.stringify(
                result,
                null,
                2
            );

    }


    queryPlan.textContent =
        JSON.stringify(
            data.query_plan,
            null,
            2
        );


    resultSection.classList.remove("hidden");

}


// --------------------------------------------------
// SHOW ERROR
// --------------------------------------------------

function showError(message) {

    errorMessage.textContent = message;

    errorSection.classList.remove("hidden");

}


// --------------------------------------------------
// HIDE ERROR
// --------------------------------------------------

function hideError() {

    errorSection.classList.add("hidden");

}


// --------------------------------------------------
// ASK BUTTON
// --------------------------------------------------

askButton.addEventListener(
    "click",
    askQuestion
);


// --------------------------------------------------
// ENTER KEY
// --------------------------------------------------

questionInput.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Enter"
            && !event.shiftKey
        ) {

            event.preventDefault();

            askQuestion();

        }

    }
);


// --------------------------------------------------
// EXAMPLE QUESTIONS
// --------------------------------------------------

exampleQuestions.forEach(
    function (button) {

        button.addEventListener(
            "click",
            function () {

                questionInput.value =
                    button.textContent.trim();

                questionInput.focus();

            }
        );

    }
);