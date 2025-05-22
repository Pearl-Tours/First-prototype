document.querySelectorAll('.carousel').forEach(carousel => {
    new bootstrap.Carousel(carousel, {
        interval: 5000,
        wrap: true
    });
});