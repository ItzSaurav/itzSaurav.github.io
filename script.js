// Typing animation
const typedTextSpan = document.querySelector(".typed-text");
const cursorSpan = document.querySelector(".cursor");

const textArray = ["Developer", "AI Enthusiast", "Problem Solver", "Tech Explorer"];
const typingDelay = 100;
const erasingDelay = 50;
const newTextDelay = 2000;
let textArrayIndex = 0;
let charIndex = 0;

function type() {
    if (charIndex < textArray[textArrayIndex].length) {
        if (!cursorSpan.classList.contains("typing")) cursorSpan.classList.add("typing");
        typedTextSpan.textContent += textArray[textArrayIndex].charAt(charIndex);
        charIndex++;
        setTimeout(type, typingDelay);
    } else {
        cursorSpan.classList.remove("typing");
        setTimeout(erase, newTextDelay);
    }
}

function erase() {
    if (charIndex > 0) {
        if (!cursorSpan.classList.contains("typing")) cursorSpan.classList.add("typing");
        typedTextSpan.textContent = textArray[textArrayIndex].substring(0, charIndex - 1);
        charIndex--;
        setTimeout(erase, erasingDelay);
    } else {
        cursorSpan.classList.remove("typing");
        textArrayIndex++;
        if (textArrayIndex >= textArray.length) textArrayIndex = 0;
        setTimeout(type, typingDelay + 1100);
    }
}

document.addEventListener("DOMContentLoaded", function() {
    if (textArray.length) setTimeout(type, newTextDelay + 250);
});

// Theme toggle
const themeToggle = document.querySelector('.theme-toggle');
themeToggle.addEventListener('click', () => {
    document.body.dataset.theme = document.body.dataset.theme === 'dark' ? 'light' : 'dark';
    themeToggle.querySelector('i').classList.toggle('fa-moon');
    themeToggle.querySelector('i').classList.toggle('fa-sun');
});

// Smooth scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Active navigation
const sections = document.querySelectorAll('section');
const navLinks = document.querySelectorAll('.nav-links a');

window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (pageYOffset >= sectionTop - 200) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href').slice(1) === current) {
            link.classList.add('active');
        }
    });
});

// News loading and filtering
let newsData = [];
let currentPage = 1;
const itemsPerPage = 6;

async function loadNews() {
    try {
        const response = await fetch('news.json');
        newsData = await response.json();
        displayNews();
    } catch (error) {
        console.error('Error loading news:', error);
        document.getElementById('newsGrid').innerHTML = `
            <div class="error-message">
                <p>Unable to load news at this time. Please try again later.</p>
            </div>
        `;
    }
}

function displayNews(filteredData = newsData) {
    const newsGrid = document.getElementById('newsGrid');
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedData = filteredData.slice(startIndex, endIndex);

    if (paginatedData.length === 0) {
        newsGrid.innerHTML = `
            <div class="no-news-message">
                <p>No news articles found.</p>
            </div>
        `;
        return;
    }

    newsGrid.innerHTML = paginatedData.map(article => `
        <div class="news-card fade-in">
            <div class="news-card-content">
                <h3>${article.title}</h3>
                <p>${article.description}</p>
                <div class="meta">
                    <span>${article.source}</span>
                    <span>${new Date(article.publishedAt).toLocaleDateString()}</span>
                </div>
                <a href="${article.url}" target="_blank" class="btn secondary">Read More</a>
            </div>
        </div>
    `).join('');

    updatePagination(filteredData.length);
}

function updatePagination(totalItems) {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    document.getElementById('pageInfo').textContent = `Page ${currentPage} of ${totalPages}`;
    document.getElementById('prevPage').disabled = currentPage === 1;
    document.getElementById('nextPage').disabled = currentPage === totalPages;
}

// News filtering
const searchInput = document.getElementById('newsSearch');
const filterButtons = document.querySelectorAll('.news-filters .filter-btn');

searchInput.addEventListener('input', filterNews);
filterButtons.forEach(button => {
    button.addEventListener('click', () => {
        filterButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        filterNews();
    });
});

function filterNews() {
    const searchTerm = searchInput.value.toLowerCase();
    const activeFilter = document.querySelector('.news-filters .filter-btn.active').dataset.filter;

    const filteredData = newsData.filter(article => {
        const matchesSearch = article.title.toLowerCase().includes(searchTerm) ||
                            article.description.toLowerCase().includes(searchTerm);
        const matchesFilter = activeFilter === 'all' || article.source.toLowerCase().includes(activeFilter);
        return matchesSearch && matchesFilter;
    });

    currentPage = 1;
    displayNews(filteredData);
}

// Pagination
document.getElementById('prevPage').addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        displayNews();
    }
});

document.getElementById('nextPage').addEventListener('click', () => {
    const totalPages = Math.ceil(newsData.length / itemsPerPage);
    if (currentPage < totalPages) {
        currentPage++;
        displayNews();
    }
});

// Project filtering
const projectFilters = document.querySelectorAll('.project-filters .filter-btn');
projectFilters.forEach(button => {
    button.addEventListener('click', () => {
        projectFilters.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        filterProjects(button.dataset.filter);
    });
});

function filterProjects(category) {
    const projects = document.querySelectorAll('.project-card');
    projects.forEach(project => {
        if (category === 'all' || project.dataset.category === category) {
            project.style.display = 'block';
                    } else {
            project.style.display = 'none';
        }
    });
}

// Contact Form Handling
const contactForm = document.getElementById('contactForm');
if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const message = document.getElementById('message').value;

        try {
            const response = await fetch('http://localhost:5000/submit-contact', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name, email, message })
            });

            const data = await response.json();

            if (response.ok) {
                // Show success message
                const successMessage = document.createElement('div');
                successMessage.className = 'success-message';
                successMessage.innerHTML = `
                    <i class="fas fa-check-circle"></i>
                    <p>Thank you for your message! I'll get back to you soon.</p>
                `;
                contactForm.reset();
                contactForm.appendChild(successMessage);
                
                // Remove success message after 5 seconds
                setTimeout(() => {
                    successMessage.remove();
                }, 5000);
            } else {
                throw new Error(data.error || 'Something went wrong');
            }
        } catch (error) {
            // Show error message
            const errorMessage = document.createElement('div');
            errorMessage.className = 'error-message';
            errorMessage.innerHTML = `
                <i class="fas fa-exclamation-circle"></i>
                <p>${error.message}</p>
            `;
            contactForm.appendChild(errorMessage);
            
            // Remove error message after 5 seconds
            setTimeout(() => {
                errorMessage.remove();
            }, 5000);
        }
    });
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadNews();
});

// Scroll Reveal Animation
function revealOnScroll() {
    const elements = document.querySelectorAll('.section-header, .about-text, .skill-tags, .project-card, .news-card, .contact-form, .contact-info');
    
    elements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const elementVisible = 150;
        
        if (elementTop < window.innerHeight - elementVisible) {
            element.classList.add('reveal', 'active');
        }
    });
}

// Add reveal class to elements
document.addEventListener('DOMContentLoaded', () => {
    const elements = document.querySelectorAll('.section-header, .about-text, .skill-tags, .project-card, .news-card, .contact-form, .contact-info');
    elements.forEach(element => element.classList.add('reveal'));
});

// Listen for scroll events
window.addEventListener('scroll', revealOnScroll);

// Initial check for elements in view
revealOnScroll();
