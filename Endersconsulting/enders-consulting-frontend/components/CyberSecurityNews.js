// components/CyberSecurityNews.js
// Fixed version without ugly external link icons

"use client";

import { useState, useEffect } from 'react';

export default function CyberSecurityNews({ 
  maxArticles = 6, 
  showImages = true, 
  compact = false,
  className = '' 
}) {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

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
        setError('Failed to fetch news');
      }
    } catch (err) {
      setError('Error loading cybersecurity news');
      console.error('News fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNews();
    
    // Auto-refresh every 15 minutes
    const interval = setInterval(fetchNews, 15 * 60 * 1000);
    return () => clearInterval(interval);
  }, [maxArticles]);

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        year: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      'Data Breach': '#ef4444',
      'Vulnerability': '#f97316', 
      'Malware': '#dc2626',
      'Ransomware': '#b91c1c',
      'Cloud Security': '#3b82f6',
      'AI Security': '#8b5cf6',
      'General Security': '#6b7280'
    };
    return colors[category] || '#6b7280';
  };

  if (loading) {
    return (
      <div className={`cybersecurity-news ${className}`}>
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading latest cybersecurity news...</p>
        </div>
        
        <style jsx>{`
          .cybersecurity-news {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
          }
          
          .loading-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 60px 20px;
            text-align: center;
          }
          
          .loading-spinner {
            width: 40px;
            height: 40px;
            border: 3px solid #f3f4f6;
            border-top: 3px solid #3b82f6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 16px;
          }
          
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`cybersecurity-news ${className}`}>
        <div className="error-container">
          <div className="error-icon">⚠️</div>
          <h3>Unable to Load Security News</h3>
          <p>{error}</p>
          <button onClick={fetchNews} className="retry-button">
            Try Again
          </button>
        </div>
        
        <style jsx>{`
          .cybersecurity-news {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
          }
          
          .error-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 60px 20px;
            text-align: center;
            background: #fef2f2;
            border: 1px solid #fecaca;
            border-radius: 8px;
          }
          
          .error-icon {
            font-size: 48px;
            margin-bottom: 16px;
          }
          
          .retry-button {
            background: #3b82f6;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            margin-top: 16px;
            transition: background-color 0.2s;
          }
          
          .retry-button:hover {
            background: #2563eb;
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className={`cybersecurity-news ${className}`}>
      {/* Header with last updated info */}
      <div className="news-header">
        <div className="news-meta">
          <span className="live-indicator">🔴 LIVE</span>
          {lastUpdated && (
            <span className="last-updated">
              Updated {lastUpdated.toLocaleTimeString('en-US', { 
                hour: 'numeric', 
                minute: '2-digit',
                hour12: true 
              })}
            </span>
          )}
          <button onClick={fetchNews} className="refresh-button" title="Refresh News">
            🔄
          </button>
        </div>
      </div>

      {/* News Grid */}
      <div className={`news-grid ${compact ? 'compact' : ''}`}>
        {articles.map((article, index) => (
          <article key={index} className="news-card">
            {showImages && article.image_url && (
              <div className="news-image">
                <img 
                  src={article.image_url} 
                  alt={article.title}
                  onError={(e) => {
                    e.target.style.display = 'none';
                  }}
                />
              </div>
            )}
            
            <div className="news-content">
              <div className="news-meta-info">
                <span 
                  className="category-badge"
                  style={{ backgroundColor: getCategoryColor(article.category) }}
                >
                  {article.category}
                </span>
                <span className="publish-date">
                  {formatDate(article.published_date)}
                </span>
              </div>
              
              <h3 className="news-title">
                <a 
                  href={article.link} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="news-link"
                >
                  {article.title}
                </a>
              </h3>
              
              <p className="news-description">
                {article.description}
              </p>
              
              <div className="news-footer">
                <span className="news-source">{article.source}</span>
                <a 
                  href={article.link} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="read-more"
                >
                  Read Full Article
                </a>
              </div>
            </div>
          </article>
        ))}
      </div>

      <style jsx>{`
        .cybersecurity-news {
          max-width: 1200px;
          margin: 0 auto;
          padding: 20px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        .news-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 24px;
          padding-bottom: 16px;
          border-bottom: 2px solid #e5e7eb;
        }
        
        .news-meta {
          display: flex;
          align-items: center;
          gap: 16px;
        }
        
        .live-indicator {
          background: #dc2626;
          color: white;
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: bold;
          animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.7; }
        }
        
        .last-updated {
          color: #6b7280;
          font-size: 14px;
        }
        
        .refresh-button {
          background: none;
          border: 1px solid #d1d5db;
          padding: 6px 10px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          transition: all 0.2s;
        }
        
        .refresh-button:hover {
          background: #f3f4f6;
          transform: rotate(180deg);
        }
        
        .news-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
          gap: 24px;
        }
        
        .news-grid.compact {
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 16px;
        }
        
        .news-card {
          background: white;
          border-radius: 12px;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
          overflow: hidden;
          transition: all 0.3s ease;
          border: 1px solid #e5e7eb;
        }
        
        .news-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.1);
        }
        
        .news-image {
          width: 100%;
          height: 200px;
          overflow: hidden;
          background: #f3f4f6;
        }
        
        .news-image img {
          width: 100%;
          height: 100%;
          object-fit: cover;
          transition: transform 0.3s ease;
        }
        
        .news-card:hover .news-image img {
          transform: scale(1.05);
        }
        
        .news-content {
          padding: 20px;
        }
        
        .news-meta-info {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }
        
        .category-badge {
          color: white;
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        
        .publish-date {
          color: #6b7280;
          font-size: 12px;
        }
        
        .news-title {
          margin: 0 0 12px 0;
          font-size: 18px;
          font-weight: 600;
          line-height: 1.4;
        }
        
        .news-link {
          color: #1f2937;
          text-decoration: none;
          transition: color 0.2s;
        }
        
        .news-link:hover {
          color: #3b82f6;
        }
        
        .news-description {
          color: #4b5563;
          font-size: 14px;
          line-height: 1.6;
          margin: 0 0 16px 0;
          display: -webkit-box;
          -webkit-line-clamp: 3;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
        
        .news-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding-top: 12px;
          border-top: 1px solid #e5e7eb;
        }
        
        .news-source {
          color: #6b7280;
          font-size: 12px;
          font-weight: 500;
        }
        
        .read-more {
          color: #3b82f6;
          text-decoration: none;
          font-size: 13px;
          font-weight: 500;
          transition: color 0.2s;
        }
        
        .read-more:hover {
          color: #2563eb;
          text-decoration: underline;
        }
        
        /* Mobile Responsive */
        @media (max-width: 768px) {
          .cybersecurity-news {
            padding: 16px;
          }
          
          .news-grid {
            grid-template-columns: 1fr;
            gap: 16px;
          }
          
          .news-content {
            padding: 16px;
          }
          
          .news-title {
            font-size: 16px;
          }
          
          .news-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 12px;
          }
        }
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
          .news-card {
            background: #1f2937;
            border-color: #374151;
          }
          
          .news-link {
            color: #f9fafb;
          }
          
          .news-description {
            color: #d1d5db;
          }
          
          .news-footer {
            border-color: #374151;
          }
        }
      `}</style>
    </div>
  );
}

