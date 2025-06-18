
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

document.addEventListener("DOMContentLoaded", () => {
    const counters = document.querySelectorAll('.stat-number');

    const animateCount = (counter) => {
        const target = +counter.innerText.replace(/[+,]/g, '');
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

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCount(entry.target);
                // Removed unobserve, so it animates every time visible
            }
        });
    }, { threshold: 1.0 });

    counters.forEach(counter => {
        observer.observe(counter);
    });
});

