// Initialize the map when the page loads
window.onload = function () {
  var map = L.map('map').setView([1.3733, 32.2903], 7);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  // Add markers for each region
  L.marker([0.3136, 32.5811]).addTo(map)  // Central
    .bindPopup("<b>Central Region</b><br>Buganda Kingdom")
    .openPopup();
  
  L.marker([1.0667, 34.1667]).addTo(map)  // Eastern
    .bindPopup("<b>Eastern Region</b><br>Imbalu Ceremony");
  
  L.marker([-0.6167, 30.6667]).addTo(map)  // Western
    .bindPopup("<b>Western Region</b><br>Ankole Cattle");
  
  L.marker([2.7746, 32.2980]).addTo(map)  // Northern
    .bindPopup("<b>Northern Region</b><br>Acholi Culture");

  // Initialize sliders
  initSliders();
  
  // Set up back to top button
  setupBackToTop();
};

// Initialize image sliders
function initSliders() {
  const sliders = document.querySelectorAll('.slider');
  
  sliders.forEach(slider => {
    const container = slider.querySelector('.slider-container');
    const slides = container.querySelectorAll('img');
    const dots = slider.querySelectorAll('.slider-dot');
    let currentIndex = 0;
    const slideCount = slides.length;
    
    // Set container width to accommodate all slides
    container.style.width = `${slideCount * 100}%`;
    
    // Set initial active dot
    dots[0].classList.add('active');
    
    // Navigation dots click event
    dots.forEach((dot, index) => {
      dot.addEventListener('click', () => {
        currentIndex = index;
        updateSlider();
      });
    });
    
    function updateSlider() {
      // Move container to show current slide
      container.style.transform = `translateX(-${currentIndex * (100 / slideCount)}%)`;
      
      // Update active dot
      dots.forEach((dot, i) => {
        dot.classList.toggle('active', i === currentIndex);
      });
    }
    
    // Auto-advance slides every 5 seconds
    setInterval(() => {
      currentIndex = (currentIndex + 1) % slideCount;
      updateSlider();
    }, 5000);
  });
}

// Filter regions based on selections
function filterRegions() {
  const regionFilter = document.getElementById('regionFilter').value;
  const interestFilter = document.getElementById('interestFilter').value;
  const keywordSearch = document.getElementById('keywordSearch').value.toLowerCase();
  
  const regions = document.querySelectorAll('.region');
  
  regions.forEach(region => {
    const regionId = region.id;
    const regionContent = region.textContent.toLowerCase();
    
    // Check if region matches all filters
    const regionMatch = regionFilter === 'all' || regionId === regionFilter;
    const interestMatch = interestFilter === 'all' || 
                         (interestFilter === 'food' && regionContent.includes('food')) ||
                         (interestFilter === 'dance' && regionContent.includes('dance')) ||
                         (interestFilter === 'clothing' && regionContent.includes('dress')) ||
                         (interestFilter === 'festival' && regionContent.includes('festival'));
    const keywordMatch = keywordSearch === '' || regionContent.includes(keywordSearch);
    
    // Show/hide based on filters
    if (regionMatch && interestMatch && keywordMatch) {
      region.style.display = '';
    } else {
      region.style.display = 'none';
    }
  });
}

// Set up back to top button
function setupBackToTop() {
  const backToTopButton = document.getElementById('backToTop');
  
  window.addEventListener('scroll', function() {
    if (window.pageYOffset > 300) {
      backToTopButton.classList.add('visible');
    } else {
      backToTopButton.classList.remove('visible');
    }
  });
  
  // Smooth scroll to top
  backToTopButton.addEventListener('click', function(e) {
    e.preventDefault();
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });
}