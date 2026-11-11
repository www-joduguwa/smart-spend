console.log("SmartSpend is running.");

document.addEventListener("click", (event) => {
    const closeButton = event.target.closest(".flash-close");

    if (!closeButton) {
        return;
    }

    const message = closeButton.closest(".flash-message");
    message.classList.add("is-dismissing");
    message.addEventListener("animationend", () => message.remove(), { once: true });
});

function deleteExpense(expenseId) {
    fetch('/delete-expense', {
        method: 'POST',
        body: JSON.stringify({ expenseId: expenseId})
    }).then((_res) => {
        window.location.href = '/expenses';
    });
}


// date-picker.js

const dateInput = document.getElementById("dateInput");
const calendar = document.getElementById("calendar");
const calendarToggle = document.getElementById("calendarToggle");

const monthYear = document.getElementById("monthYear");
const calendarDays = document.getElementById("calendarDays");

const prevMonth = document.getElementById("prevMonth");
const nextMonth = document.getElementById("nextMonth");
const todayBtn = document.getElementById("todayBtn");

let currentDate = new Date();
let selectedDate = null;


/* --------------------------------
   Format date
-------------------------------- */

function formatDate(date) {
    const day = String(date.getDate()).padStart(2, "0");
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const year = date.getFullYear();

    return `${day}-${month}-${year}`;
}


/* --------------------------------
   Render calendar
-------------------------------- */

function renderCalendar() {

    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    const monthName = currentDate.toLocaleString("default", {
        month: "long"
    });

    monthYear.textContent = `${monthName} ${year}`;

    calendarDays.innerHTML = "";

    const firstDay = new Date(year, month, 1).getDay();

    const daysInMonth = new Date(
        year,
        month + 1,
        0
    ).getDate();


    /* Empty spaces before first day */

    for (let i = 0; i < firstDay; i++) {

        const emptyDay = document.createElement("div");

        emptyDay.classList.add(
            "calendar-day",
            "empty"
        );

        calendarDays.appendChild(emptyDay);
    }


    /* Days */

    const today = new Date();

    for (let day = 1; day <= daysInMonth; day++) {

        const dayButton = document.createElement("button");

        dayButton.type = "button";

        dayButton.textContent = day;

        dayButton.classList.add("calendar-day");


        const thisDate = new Date(
            year,
            month,
            day
        );


        /* Today */

        if (
            day === today.getDate() &&
            month === today.getMonth() &&
            year === today.getFullYear()
        ) {
            dayButton.classList.add("today");
        }


        /* Selected */

        if (
            selectedDate &&
            day === selectedDate.getDate() &&
            month === selectedDate.getMonth() &&
            year === selectedDate.getFullYear()
        ) {
            dayButton.classList.add("selected");
        }


        /* Click */

        dayButton.addEventListener("click", () => {

            selectedDate = thisDate;

            dateInput.value = formatDate(thisDate);

            calendar.classList.remove("active");

            renderCalendar();
        });


        calendarDays.appendChild(dayButton);
    }
}


/* --------------------------------
   Open / close calendar
-------------------------------- */

calendarToggle.addEventListener("click", () => {

    calendar.classList.toggle("active");

    if (calendar.classList.contains("active")) {
        renderCalendar();
    }
});


dateInput.addEventListener("click", () => {

    calendar.classList.toggle("active");

    if (calendar.classList.contains("active")) {
        renderCalendar();
    }
});


/* --------------------------------
   Previous month
-------------------------------- */

prevMonth.addEventListener("click", () => {

    currentDate.setMonth(
        currentDate.getMonth() - 1
    );

    renderCalendar();
});


/* --------------------------------
   Next month
-------------------------------- */

nextMonth.addEventListener("click", () => {

    currentDate.setMonth(
        currentDate.getMonth() + 1
    );

    renderCalendar();
});


/* --------------------------------
   Today
-------------------------------- */

todayBtn.addEventListener("click", () => {

    const today = new Date();

    currentDate = new Date(today);

    selectedDate = new Date(today);

    dateInput.value = formatDate(today);

    calendar.classList.remove("active");

    renderCalendar();
});


/* --------------------------------
   Close when clicking outside
-------------------------------- */

document.addEventListener("click", (event) => {

    if (!event.target.closest(".date-picker")) {
        calendar.classList.remove("active");
    }
});


/* Initial render */

renderCalendar();

document.querySelectorAll(
    '.category-option input'
).forEach(input => {

    input.addEventListener('change', function () {

        document.getElementById(
            'selectedCategory'
        ).textContent = this.value;

        document.querySelector(
            '.category-menu'
        ).removeAttribute('open');
    });

});

document.querySelectorAll("[data-category]").forEach(button => {

    button.addEventListener("click", function () {

        const category = this.dataset.category;

        // Change what is displayed in the button
        document.getElementById("selectedCategory").textContent = category;

        // Give Flask the actual value
        document.getElementById("category").value = category;

        // Close dropdown
        document.querySelector(".category-menu").removeAttribute("open");
    });

});


