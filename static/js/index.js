
document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.querySelector("#loginForm");
    const alertBox = document.querySelector("#loginAlert");

    loginForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        const formData = new FormData(loginForm);
        const response = await fetch("/login", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            window.location.href = result.redirect_url;
        } else {
            alertBox.innerHTML = `<div class="alert alert-danger">${result.message}</div>`;
        }
    });
});

