document.addEventListener("DOMContentLoaded", function () {
    // === LOGIN FORM HANDLER ===
    const loginForm = document.querySelector("#loginForm");
    const alertBox = document.querySelector("#loginAlert");

    if (loginForm) {
        loginForm.addEventListener("submit", async function (e) {
            e.preventDefault();

            const formData = new FormData(loginForm);
            try {
                const response = await fetch("/login", {
                    method: "POST",
                    body: formData,
                });

                const result = await response.json();

                if (result.success) {
                    window.location.href = result.redirect_url;
                } else {
                    alertBox.innerHTML = `<div class="alert alert-danger">${result.message}</div>`;
                }
            } catch (err) {
                alertBox.innerHTML = `<div class="alert alert-danger">An error occurred. Please try again later.</div>`;
                console.error("Login error:", err);
            }
        });
    }

    // === STAT COUNTER ANIMATION ===
    const counters = document.querySelectorAll(".stat-number");

    if (counters.length > 0) {
        const animateCount = (counter) => {
            const target = +counter.innerText.replace(/[+,]/g, "");
            let count = 0;
            const speed = 200;
            const increment = Math.ceil(target / speed);

            const updateCount = () => {
                count += increment;
                if (count < target) {
                    counter.innerText = count.toLocaleString() + "+";
                    requestAnimationFrame(updateCount);
                } else {
                    counter.innerText = target.toLocaleString() + "+";
                }
            };

            updateCount();
        };

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        animateCount(entry.target);
                    }
                });
            },
            { threshold: 1.0 }
        );

        counters.forEach((counter) => {
            observer.observe(counter);
        });
    }
});
