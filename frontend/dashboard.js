// Dashboard JavaScript

const results = JSON.parse(sessionStorage.getItem('results') || '[]');

window.addEventListener('DOMContentLoaded', () => {
    const loading = document.getElementById('loading');
    const resultsContainer = document.getElementById('results');
    const noResults = document.getElementById('noResults');

    loading.style.display = 'none';

    if (results.length === 0) {
        noResults.style.display = 'block';
    } else {
        displayResults(results);
    }
});

function displayResults(stories) {
    const container = document.getElementById('results');

    stories.forEach((story, index) => {
        const card = createStoryCard(story, index + 1);
        container.appendChild(card);
    });
}

function createStoryCard(story, rank) {
    const card = document.createElement('div');
    card.className = 'story-card';

    const score = story.virality_score || 0;
    const scoreClass = score >= 80 ? 'score-high' : score >= 50 ? 'score-medium' : 'score-low';

    card.innerHTML = `
        <div class="card-header">
            <span class="rank">#${rank}</span>
            <span class="platform-badge">${getPlatformIcon(story.platform)} ${story.platform}</span>
            <span class="score-badge ${scoreClass}">${score}/100</span>
        </div>
        
        <div class="card-content">
            <h3 class="story-headline">${truncate(story.text, 100) || 'No headline available'}</h3>
            
            <div class="engagement-metrics">
                <span>❤️ ${formatNumber(story.likes)} likes</span>
                <span>🔄 ${formatNumber(story.shares)} shares</span>
                <span>💬 ${formatNumber(story.comments)} comments</span>
            </div>
            
            <div class="category-tag">${story.category}</div>
            
            <div class="ai-brief">
                <h4>AI Brief</h4>
                <div class="brief-content">${formatBrief(story.ai_brief)}</div>
            </div>
            
            <div class="card-actions">
                <a href="${story.url}" target="_blank" class="btn-primary">View Source →</a>
                <span class="author-info">By ${story.author}</span>
            </div>
        </div>
    `;

    return card;
}

function getPlatformIcon(platform) {
    const icons = {
        'TikTok': '📱',
        'Instagram': '📷',
        'Facebook': '👥',
        'Twitter': '🐦',
        'RSS': '📰'
    };
    return icons[platform] || '📌';
}

function formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num;
}

function truncate(text, length) {
    if (!text) return '';
    return text.length > length ? text.substring(0, length) + '...' : text;
}

function formatBrief(brief) {
    if (!brief) return '<p>No AI brief available</p>';

    // Convert markdown-style formatting to HTML
    return brief
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>')
        .replace(/^•/gm, '&bull;');
}
