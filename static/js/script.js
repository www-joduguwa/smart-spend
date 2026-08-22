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
