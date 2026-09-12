// =========================================================
// K-MAP SIMPLIFIER - FRONTEND JAVASCRIPT
// =========================================================


// =========================================================
// 1. GET HTML ELEMENTS
// =========================================================

const input = document.getElementById("minterms");
const button = document.getElementById("solvebutton");
const result = document.getElementById("result");
const steps = document.getElementById("steps");
const table = document.querySelector("table");


// =========================================================
// 2. PARSE AND VALIDATE MINTERMS
// =========================================================

function parseMinterms(text) {

    // Validate the input and convert the entered minterms into numbers.

    if (text.trim() === "") {
        return {
            success: false,
            message: "PLEASE ENTER ATLEAST ONE MINTERM."
        };
    }

    const parts = text.split(",");
    const minterms = [];

    // Validate each entered minterm individually.

    for (const part of parts) {

        const value = part.trim();

        if (value === "") {
            return {
                success: false,
                message: "AN EMPTY MINTERM WAS FOUND! CHECK THE COMMAS."
            };
        }

        const number = Number(value);

        if (Number.isNaN(number)) {
            return {
                success: false,
                message: `"${value}" IS NOT A VALID NUMBER!`
            };
        }

        if (!Number.isInteger(number)) {
            return {
                success: false,
                message: `MINTERM ${value} MUST BE AN INTEGER!`
            };
        }

        if (number < 0 || number > 15) {
            return {
                success: false,
                message:
                    `MINTERM ${number} IS OUT OF RANGE! USE VALUES FROM 0 TO 15.`
            };
        }

        minterms.push(number);
    }

    // Ensure that every minterm appears only once.

    const uniqueMinterms = new Set(minterms);

    if (uniqueMinterms.size !== minterms.length) {
        return {
            success: false,
            message: "DUPLICATE MINTERMS ARE NOT ALLOWED!"
        };
    }

    return {
        success: true,
        minterms: minterms
    };
}


// =========================================================
// 3. DISPLAY K-MAP
// =========================================================

function displayKMap(kmap) {

    // Map the backend K-map matrix to the corresponding HTML table cells.

    const rows = table.querySelectorAll("tr");

    for (let row = 0; row < 4; row++) {

        const cells = rows[row + 1].querySelectorAll("td");

        for (let column = 0; column < 4; column++) {
            cells[column].textContent = kmap[row][column];
        }
    }
}


// =========================================================
// 4. CLEAR K-MAP
// =========================================================

function clearKMap() {

    // Reset all K-map cells and remove highlighting from the previous solution.

    const rows = table.querySelectorAll("tr");

    for (let row = 0; row < 4; row++) {

        const cells = rows[row + 1].querySelectorAll("td");

        for (let column = 0; column < 4; column++) {
            cells[column].textContent = "0";
        }
    }

    clearGroupHighlighting();
}


// =========================================================
// 5. CLEAR GROUP HIGHLIGHTING
// =========================================================

function clearGroupHighlighting() {

    // Remove all CSS classes used to visualize K-map groups.

    const cells = table.querySelectorAll("td");

    for (const cell of cells) {

        cell.classList.remove("group-1");
        cell.classList.remove("group-2");
        cell.classList.remove("group-3");
        cell.classList.remove("group-4");
        cell.classList.remove("group-5");
        cell.classList.remove("group-6");
        cell.classList.remove("group-7");
        cell.classList.remove("group-8");
    }
}


// =========================================================
// 6. DISPLAY GROUPS
// =========================================================

function displayGroups(groups) {

    // Remove the highlighting from the previous K-map solution.

    clearGroupHighlighting();

    // CSS classes used to visually distinguish different K-map groups.

    const colors = [
        "group-1",
        "group-2",
        "group-3",
        "group-4",
        "group-5",
        "group-6",
        "group-7",
        "group-8"
    ];

    // Apply a different CSS class to each selected group.

    groups.forEach(function(group, groupIndex) {

        const className = colors[groupIndex % colors.length];

        group.cells.forEach(function(cell) {

            const row = cell[0];
            const column = cell[1];
            const rows = table.querySelectorAll("tr");

            const tableCell =
                rows[row + 1].querySelectorAll("td")[column];

            tableCell.classList.add(className);
        });
    });
}


// =========================================================
// 7. DISPLAY SOLUTION STEPS
// =========================================================

function displaySteps(solutionSteps) {

    // Replace the previous solution steps with the newly generated steps.

    steps.innerHTML = "";

    for (const step of solutionSteps) {

        const listItem = document.createElement("li");

        listItem.textContent = step;
        steps.appendChild(listItem);
    }
}


// =========================================================
// 8. CLEAR SOLUTION STEPS
// =========================================================

function clearSteps() {

    steps.innerHTML = "";
}


// =========================================================
// 9. DISPLAY BOOLEAN EXPRESSION
// =========================================================

function displayResult(expression) {

    result.textContent = expression;
}


// =========================================================
// 10. SOLVE K-MAP
// =========================================================

async function solveKMap() {

    // Read the user's input and clear the previous solution.

    const text = input.value;

    clearKMap();
    clearSteps();

    // Validate and convert the entered minterms before sending them to Flask.

    const parsed = parseMinterms(text);

    if (!parsed.success) {
        result.textContent = parsed.message;
        return;
    }

    const minterms = parsed.minterms;

    // Inform the user that the K-map calculation is in progress.

    result.textContent = "Solving K-Map...";

    try {

        // Send the validated minterms to the Flask backend for processing.

        const response = await fetch("/solve", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                minterms: minterms
            })
        });

        if (!response.ok) {
            throw new Error("Server returned an error.");
        }

        // Convert the server's JSON response into a JavaScript object.

        const data = await response.json();

        // Display the complete backend response for development and debugging.

        console.log("K-Map solution:", data);

        // Update every part of the interface using the new solution.

        displayKMap(data.kmap);
        displayGroups(data.groups);
        displayResult(data.expression);
        displaySteps(data.steps);
    }

    catch (error) {

        // Log the error for development and debugging.

        console.log("Error:", error);

        // Remove any incomplete solution from the interface.

        clearKMap();
        clearSteps();

        // Display a user-friendly error message.

        result.textContent =
            "Unable to solve K-Map. Please try again.";
    }
}


// =========================================================
// 11. BUTTON EVENT
// =========================================================

// Start the K-map solving process when the Solve button is clicked.

button.addEventListener("click", solveKMap);

