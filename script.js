document.addEventListener("DOMContentLoaded", function() {
    const newsContainer = document.getElementById("news-container");
    const loadingMessage = document.querySelector(".loading-message");
    const errorMessage = document.getElementById("error-message");
    const noNewsMessage = document.getElementById("no-news-message");

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

    // Fetch news data
    fetch("news.json")
        .then(response => {
            if (!response.ok) {
                // If news.json is not found or other HTTP error
                throw new Error(`HTTP error! Status: ${response.status}. Could not fetch news data.`);
            }
            return response.json();
        })
        .then(data => {
            hideAllMessages(); // Hide loading message once data is fetched

            if (data && data.length > 0) {
                newsContainer.innerHTML = ''; // Clear any existing content (like the loading message)

                data.forEach(article => {
                    const articleDiv = document.createElement("div");
                    articleDiv.classList.add("news-article");

                    const articleContent = document.createElement("div");
                    articleContent.classList.add("article-content");

                    const title = document.createElement("h3"); // Changed to h3 for semantic hierarchy
                    title.classList.add("article-title");
                    const link = document.createElement("a");
                    link.href = article.url;
                    link.target = "_blank"; // Open in new tab
                    link.rel = "noopener noreferrer"; // Security best practice for target="_blank"
                    link.textContent = article.title || "No Title Available"; // Fallback text
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
                    let metaText = '';

                    if (article.source) {
                        metaText += `Source: ${article.source}`;
                    }

                    if (article.publishedAt) {
                        try {
                            const date = new Date(article.publishedAt);
                            // Format date nicely, e.g., "May 28, 2025" or "5/28/2025"
                            // Using toLocaleDateString for user-friendly format
                            metaText += `${metaText ? ' | ' : ''}Published: ${date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}`;
                        } catch (e) {
                            console.warn("Invalid date format:", article.publishedAt, e);
                            // Fallback if date parsing fails
                            metaText += `${metaText ? ' | ' : ''}Published: Date N/A`;
                        }
                    } else {
                        metaText += `${metaText ? ' | ' : ''}Published: Date N/A`;
                    }
                    meta.textContent = metaText;
                    articleContent.appendChild(meta);

                    articleDiv.appendChild(articleContent);
                    newsContainer.appendChild(articleDiv);
                });
            } else {
                showMessage(noNewsMessage); // Show "No news found" message
            }
        })
        .catch(error => {
            console.error("Error fetching or parsing news:", error);
            // Display an error message to the user
            showMessage(errorMessage);
            newsContainer.innerHTML = ''; // Clear loading message in case of error
        });
});
