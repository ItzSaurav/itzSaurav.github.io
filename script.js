document.addEventListener("DOMContentLoaded", function() {
    const newsContainer = document.getElementById("news-container");
    const loadingMessage = document.querySelector(".loading-message");
    const errorMessage = document.getElementById("error-message");
    const noNewsMessage = document.getElementById("no-news-message");
    let lastFetchTime = null;
    const REFRESH_INTERVAL = 5 * 60 * 1000; // 5 minutes

    // Set current year in footer
    document.getElementById("current-year").textContent = new Date().getFullYear();

    // Function to hide all messages
    function hideAllMessages() {
        if (loadingMessage) loadingMessage.style.display = 'none';
        if (errorMessage) errorMessage.style.display = 'none';
        if (noNewsMessage) noNewsMessage.style.display = 'none';
    }

    // Function to show a specific message
    function showMessage(element) {
        hideAllMessages();
        if (element) element.style.display = 'block';
    }

    // Function to format relative time
    function getRelativeTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) return 'just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }

    // Function to create article element
    function createArticleElement(article) {
        const articleDiv = document.createElement("div");
        articleDiv.classList.add("news-article");

        const articleContent = document.createElement("div");
        articleContent.classList.add("article-content");

        const title = document.createElement("h3");
        title.classList.add("article-title");
        const link = document.createElement("a");
        link.href = article.url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = article.title || "No Title Available";
        title.appendChild(link);
        articleContent.appendChild(title);

        if (article.description) {
            const description = document.createElement("p");
            description.classList.add("article-description");
            description.textContent = article.description;
            articleContent.appendChild(description);
        }

        const meta = document.createElement("p");
        meta.classList.add("article-meta");
        
        const sourceSpan = document.createElement("span");
        sourceSpan.textContent = article.source ? `Source: ${article.source}` : '';
        
        const timeSpan = document.createElement("span");
        timeSpan.textContent = article.publishedAt ? getRelativeTime(article.publishedAt) : 'Date N/A';
        
        meta.appendChild(sourceSpan);
        meta.appendChild(timeSpan);
        articleContent.appendChild(meta);

        articleDiv.appendChild(articleContent);
        return articleDiv;
    }

    // Function to fetch and display news
    async function fetchAndDisplayNews() {
        try {
            showMessage(loadingMessage);
            const response = await fetch("news.json");
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            hideAllMessages();

            if (data && data.length > 0) {
                newsContainer.innerHTML = '';
                data.forEach(article => {
                    const articleElement = createArticleElement(article);
                    newsContainer.appendChild(articleElement);
                });
            } else {
                showMessage(noNewsMessage);
            }
            
            lastFetchTime = new Date();
        } catch (error) {
            console.error("Error fetching or parsing news:", error);
            showMessage(errorMessage);
            newsContainer.innerHTML = '';
        }
    }

    // Initial fetch
    fetchAndDisplayNews();

    // Set up periodic refresh
    setInterval(() => {
        if (!lastFetchTime || (new Date() - lastFetchTime) >= REFRESH_INTERVAL) {
            fetchAndDisplayNews();
        }
    }, REFRESH_INTERVAL);

    // Add refresh button functionality
    const refreshButton = document.createElement("button");
    refreshButton.classList.add("refresh-button");
    refreshButton.innerHTML = "🔄 Refresh News";
    refreshButton.addEventListener("click", fetchAndDisplayNews);
    document.querySelector(".section-title").appendChild(refreshButton);

    // Add smooth scroll to top button
    const scrollButton = document.createElement("button");
    scrollButton.classList.add("scroll-top-button");
    scrollButton.innerHTML = "↑";
    scrollButton.style.display = "none";
    document.body.appendChild(scrollButton);

    window.addEventListener("scroll", () => {
        if (window.pageYOffset > 300) {
            scrollButton.style.display = "block";
        } else {
            scrollButton.style.display = "none";
        }
    });

    scrollButton.addEventListener("click", () => {
        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    });
});
