// NewsWidget.js
// Compact cybersecurity news widget for sidebars or smaller spaces

import React, { useState, useEffect } from 'react';

const NewsWidget = ({ maxArticles = 3, showRefresh = true }) => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchNews();
    // Refresh every 30 minutes for widget
    const interval = setInterval(fetchNews, 30 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchNews = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/news/cybersecurity');
      const data = await response.json();
      
      if (data.status === 'success') {
        setArticles(data.data.articles.slice(0, maxArticles));
        setError(null);
      } else {
        setError('Failed to load news');
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  const getCategoryIcon = (category) => {
    const icons = {
      'Data Breach': '🔓',
      'Ransomware': '🔒',
      'Vulnerability': '⚠️',
      'Malware': '🦠',
      'Cyber Attack': '🎯',
      'Mobile Security': '📱',
      'Cloud Security': '☁️',
      'AI Security': '🤖',
      'Critical Infrastructure': '🏭',
      'Privacy': '🛡️',
      'Phishing': '🎣',
      'General Security': '🔐'
    };
    return icons[category] || '🔐';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Security News</h3>
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
        </div>
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
              <div className="h-2 bg-gray-200 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Security News</h3>
          {showRefresh && (
            <button 
              onClick={fetchNews}
              className="text-blue-600 hover:text-blue-800 text-xs"
            >
              Retry
            </button>
          )}
        </div>
        <div className="text-center py-4">
          <div className="text-red-500 text-sm">Unable to load news</div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Security News</h3>
        {showRefresh && (
          <button 
            onClick={fetchNews}
            className="text-blue-600 hover:text-blue-800 text-xs flex items-center"
            disabled={loading}
          >
            <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        )}
      </div>

      {/* Articles */}
      <div className="space-y-3">
        {articles.map((article, index) => (
          <div key={index} className="group">
            <a 
              href={article.link} 
              target="_blank" 
              rel="noopener noreferrer"
              className="block hover:bg-gray-50 rounded-lg p-2 -m-2 transition-colors duration-200"
            >
              {/* Category and Date */}
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-gray-500 flex items-center">
                  <span className="mr-1">{getCategoryIcon(article.category)}</span>
                  {article.category}
                </span>
                <span className="text-xs text-gray-400">
                  {new Date(article.published_date).toLocaleDateString('en-US', { 
                    month: 'short', 
                    day: 'numeric' 
                  })}
                </span>
              </div>
              
              {/* Title */}
              <h4 className="text-sm font-medium text-gray-900 group-hover:text-blue-600 transition-colors duration-200 leading-tight mb-1">
                {article.title.length > 80 ? article.title.substring(0, 80) + '...' : article.title}
              </h4>
              
              {/* Description */}
              <p className="text-xs text-gray-600 leading-relaxed">
                {article.description.length > 100 ? article.description.substring(0, 100) + '...' : article.description}
              </p>
            </a>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="mt-4 pt-3 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-500">The Hacker News</span>
          <a 
            href="https://thehackernews.com" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-xs text-blue-600 hover:text-blue-800 font-medium"
          >
            View All →
          </a>
        </div>
      </div>
    </div>
  );
};

export default NewsWidget;

// Usage Examples:
/*
// Basic widget
<NewsWidget />

// Custom number of articles
<NewsWidget maxArticles={5} />

// Without refresh button
<NewsWidget showRefresh={false} />

// In a sidebar
<div className="w-80">
  <NewsWidget maxArticles={4} />
</div>
*/

