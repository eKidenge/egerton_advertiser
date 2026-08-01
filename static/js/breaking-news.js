// Breaking News Ticker

document.addEventListener('DOMContentLoaded', function() {
    loadBreakingNews();
    setInterval(loadBreakingNews, 30000); // Refresh every 30 seconds
});

function loadBreakingNews() {
    const tickerContainer = document.getElementById('breakingTicker');
    if (!tickerContainer) return;
    
    fetch('/articles/api/breaking-news/')
        .then(response => response.json())
        .then(data => {
            if (data.articles && data.articles.length > 0) {
                let html = '';
                data.articles.forEach((article, index) => {
                    const separator = index < data.articles.length - 1 ? ' &bull; ' : '';
                    html += `
                        <span class="ticker-item">
                            <a href="${article.url}" target="_blank">${article.title}</a>
                            <span class="ticker-time">${article.published_at}</span>
                        </span>
                        ${separator}
                    `;
                });
                tickerContainer.innerHTML = html;
            } else {
                tickerContainer.innerHTML = '<span class="ticker-item">No breaking news at the moment</span>';
            }
        })
        .catch(error => {
            console.error('Error loading breaking news:', error);
            tickerContainer.innerHTML = '<span class="ticker-item">Unable to load breaking news</span>';
        });
}