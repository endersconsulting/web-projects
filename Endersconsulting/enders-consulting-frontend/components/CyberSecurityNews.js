// CybersecurityNews.js
// React component for displaying The Hacker News cybersecurity feed

import React, { useState, useEffect } from 'react';

const CybersecurityNews = ({ maxArticles = 6, showImages = true, compact = false }) => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    fetchNews();
    // Refresh every 15 minutes
    const interval = setInterval(fetchNews, 15 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchNews = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/news/cybersecurity');
      const data = await response.json();
      
      if (data.status === 'success') {
        setArticles(data.data.articles.slice(0, maxArticles));
        setLastUpdated(new Date(data.data.last_updated));
        setError(null);
      } else {
        setError(data.message || 'Failed to fetch news');
      }
    } catch (err) {
      setError('Network error: Unable to fetch news');
      console.error('News fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      'Data Breach': 'bg-red-100 text-red-800',
      'Ransomware': 'bg-purple-100 text-purple-800',
      'Vulnerability': 'bg-orange-100 text-orange-800',
      'Malware': 'bg-yellow-100 text-yellow-800',
      'Cyber Attack': 'bg-red-100 text-red-800',
      'Mobile Security': 'bg-blue-100 text-blue-800',
      'Cloud Security': 'bg-cyan-100 text-cyan-800',
      'AI Security': 'bg-green-100 text-green-800',
      'Critical Infrastructure': 'bg-gray-100 text-gray-800',
      'Privacy': 'bg-indigo-100 text-indigo-800',
      'Phishing': 'bg-pink-100 text-pink-800',
      'General Security': 'bg-gray-100 text-gray-800'
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };

  const formatTimeAgo = (date) => {
    const now = new Date();
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Less than an hour ago';
    if (diffInHours < 24) return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`;
    
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Security in the News</h2>
          <div className="flex items-center text-sm text-gray-500">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
            Loading latest news...
          </div>
        </div>
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="flex space-x-4">
                <div className="rounded-lg bg-gray-200 h-20 w-32 flex-shrink-0"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  <div className="h-3 bg-gray-200 rounded w-full"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Security in the News</h2>
          <button 
            onClick={fetchNews}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            Try Again
          </button>
        </div>
        <div className="text-center py-8">
          <div className="text-red-600 mb-2">⚠️ Unable to load news</div>
          <div className="text-gray-600 text-sm">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Security in the News</h2>
          <p className="text-gray-600 text-sm mt-1">Latest cybersecurity threats and updates</p>
        </div>
        <div className="flex items-center space-x-4">
          {lastUpdated && (
            <div className="text-xs text-gray-500">
              Updated {formatTimeAgo(lastUpdated)}
            </div>
          )}
          <button 
            onClick={fetchNews}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center"
            disabled={loading}
          >
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>
      </div>

      {/* Articles */}
      <div className="space-y-6">
        {articles.map((article, index) => (
          <article 
            key={index} 
            className={`group hover:bg-gray-50 rounded-lg p-4 transition-colors duration-200 ${
              compact ? 'border-b border-gray-200 last:border-b-0' : 'border border-gray-200'
            }`}
          >
            <div className="flex space-x-4">
              {/* Article Image */}
              {showImages && article.image_url && (
                <div className="flex-shrink-0">
                  <img 
                    src={article.image_url} 
                    alt={article.title}
                    className="w-24 h-20 object-cover rounded-lg"
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                </div>
              )}
              
              {/* Article Content */}
              <div className="flex-1 min-w-0">
                {/* Category Badge */}
                <div className="flex items-center space-x-2 mb-2">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getCategoryColor(article.category)}`}>
                    {article.category}
                  </span>
                  <span className="text-xs text-gray-500">
                    {article.published_date}
                  </span>
                </div>
                
                {/* Title */}
                <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors duration-200">
                  <a 
                    href={article.link} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="hover:underline"
                  >
                    {article.title}
                  </a>
                </h3>
                
                {/* Description */}
                <p className="text-gray-600 text-sm mb-3 leading-relaxed">
                  {article.description}
                </p>
                
                {/* Footer */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center text-xs text-gray-500">
                    <span className="font-medium">{article.source}</span>
                  </div>
                  <a 
                    href={article.link} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    Read More
                    <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </div>
              </div>
            </div>
          </article>
        ))}
      </div>

      {/* Footer */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <div className="text-xs text-gray-500">
            Powered by <a href="https://thehackernews.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">The Hacker News</a>
          </div>
          <a 
            href="https://thehackernews.com" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            View All News →
          </a>
        </div>
      </div>
    </div>
  );
};

export default CybersecurityNews;

// Usage Examples:
/*
// Basic usage
<CybersecurityNews />

// Compact version with fewer articles
<CybersecurityNews maxArticles={4} compact={true} />

// Without images
<CybersecurityNews showImages={false} />

// Custom styling
<CybersecurityNews 
  maxArticles={8} 
  showImages={true} 
  compact={false} 
/>
*/

