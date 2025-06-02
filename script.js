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

// News Loading and Filtering
async function loadNews() {
    try {
        const response = await fetch('ai_news.json');
        const data = await response.json();
        const articles = data.articles || [];
        
        // Update last updated time
        const lastUpdated = document.createElement('div');
        lastUpdated.className = 'last-updated';
        lastUpdated.innerHTML = `
            <i class="fas fa-sync-alt"></i>
            <span>Last updated: ${formatDate(data.lastUpdated)}</span>
            <span class="article-count">${data.totalArticles} articles</span>
        `;
        document.querySelector('.news-controls').appendChild(lastUpdated);
        
        displayNews(articles);
        setupNewsAnimations();
    } catch (error) {
        console.error('Error loading news:', error);
        const newsGrid = document.getElementById('newsGrid');
        newsGrid.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-circle"></i>
                <p>Failed to load news. Please try again later.</p>
                <button onclick="loadNews()" class="retry-btn">
                    <i class="fas fa-redo"></i> Retry
                </button>
            </div>
        `;
    }
}

function displayNews(articles) {
    const newsGrid = document.getElementById('newsGrid');
    newsGrid.innerHTML = '';
    
    articles.forEach((article, index) => {
        const card = document.createElement('div');
        card.className = 'news-card';
        card.style.animationDelay = `${index * 0.1}s`;
        
        const imageHtml = article.image ? 
            `<div class="news-image">
                <img src="${article.image}" alt="${article.title}" loading="lazy">
            </div>` : '';
        
        card.innerHTML = `
            ${imageHtml}
            <div class="news-content">
                <div class="news-category ${article.category}">${article.category}</div>
                <h3>${article.title}</h3>
                <p>${article.description}</p>
                <div class="news-meta">
                    <div class="meta-left">
                        <span class="news-source">
                            <i class="fas fa-newspaper"></i>
                            ${article.source}
                        </span>
                        <span class="news-date">
                            <i class="far fa-clock"></i>
                            ${formatDate(article.publishedAt)}
                        </span>
                    </div>
                    <div class="meta-right">
                        <span class="reading-time">
                            <i class="fas fa-book-reader"></i>
                            ${article.readingTime} min read
                        </span>
                    </div>
                </div>
                <a href="${article.url}" target="_blank" class="read-more">
                    Read More <i class="fas fa-arrow-right"></i>
                </a>
            </div>
        `;
        newsGrid.appendChild(card);
    });
}

function setupNewsAnimations() {
    const cards = document.querySelectorAll('.news-card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1
    });

    cards.forEach(card => observer.observe(card));
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    // If less than 24 hours ago, show relative time
    if (diff < 24 * 60 * 60 * 1000) {
        const hours = Math.floor(diff / (60 * 60 * 1000));
        if (hours === 0) {
            const minutes = Math.floor(diff / (60 * 1000));
            return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
        }
        return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
    }
    
    // Otherwise show full date
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Enhanced search functionality
function searchNews(query) {
    const newsCards = document.querySelectorAll('.news-card');
    const searchTerm = query.toLowerCase();
    let visibleCount = 0;
    
    newsCards.forEach(card => {
        const title = card.querySelector('h3').textContent.toLowerCase();
        const description = card.querySelector('p').textContent.toLowerCase();
        const category = card.querySelector('.news-category').textContent.toLowerCase();
        const source = card.querySelector('.news-source').textContent.toLowerCase();
        
        const isVisible = title.includes(searchTerm) || 
                         description.includes(searchTerm) ||
                         category.includes(searchTerm) ||
                         source.includes(searchTerm);
        
        card.style.display = isVisible ? 'block' : 'none';
        if (isVisible) visibleCount++;
    });
    
    // Show no results message if needed
    const noResults = document.querySelector('.no-results');
    if (visibleCount === 0) {
        if (!noResults) {
            const message = document.createElement('div');
            message.className = 'no-results';
            message.innerHTML = `
                <i class="fas fa-search"></i>
                <p>No articles found matching "${query}"</p>
                <button onclick="clearSearch()" class="clear-search">
                    Clear Search
                </button>
            `;
            document.getElementById('newsGrid').appendChild(message);
        }
    } else if (noResults) {
        noResults.remove();
    }
}

function clearSearch() {
    document.getElementById('newsSearch').value = '';
    document.querySelectorAll('.news-card').forEach(card => {
        card.style.display = 'block';
    });
    document.querySelector('.no-results')?.remove();
}

// Enhanced filter functionality
function filterNews(category) {
    const newsCards = document.querySelectorAll('.news-card');
    const filterButtons = document.querySelectorAll('.news-filters .filter-btn');
    
    filterButtons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.filter === category);
    });
    
    newsCards.forEach(card => {
        if (category === 'all' || card.querySelector('.news-category').textContent === category) {
            card.style.display = 'block';
            card.classList.add('filtered');
        } else {
            card.style.display = 'none';
            card.classList.remove('filtered');
        }
    });
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Load news when page loads
    loadNews();
    
    // Filter buttons
    document.querySelectorAll('.news-filters .filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            filterNews(btn.dataset.filter);
        });
    });
    
    // Search input with debounce
    const searchInput = document.getElementById('newsSearch');
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            searchNews(e.target.value);
        }, 300);
    });
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'f') {
            e.preventDefault();
            searchInput.focus();
        }
    });
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
