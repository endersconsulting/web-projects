// NewsTicker.js
// Breaking news ticker for urgent cybersecurity alerts

import React, { useState, useEffect, useRef } from 'react';

const NewsTicker = ({ 
  maxArticles = 5, 
  speed = 50, // pixels per second
  pauseOnHover = true,
  showBreakingOnly = false,
  height = '40px'
}) => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isPaused, setIsPaused] = useState(false);
  const tickerRef = useRef(null);
  const contentRef = useRef(null);

  useEffect(() => {
    fetchNews();
    // Refresh every 10 minutes for ticker
    const interval = setInterval(fetchNews, 10 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (articles.length > 0 && contentRef.current) {
      startAnimation();
    }
  }, [articles, isPaused]);

  const fetchNews = async () => {
    try {
      const response = await fetch('/api/news/cybersecurity');
      const data = await response.json();
      
      if (data.status === 'success') {
        let filteredArticles = data.data.articles;
        
        // Filter for breaking news if requested
        if (showBreakingOnly) {
          filteredArticles = filteredArticles.filter(article => 
            isBreakingNews(article)
          );
        }
        
        setArticles(filteredArticles.slice(0, maxArticles));
        setLoading(false);
      }
    } catch (err) {
      console.error('Failed to fetch news:', err);
      setLoading(false);
    }
  };

  const isBreakingNews = (article) => {
    const breakingKeywords = [
      'breaking', 'urgent', 'alert', 'warning', 'critical', 'zero-day',
      'actively exploited', 'emergency', 'immediate', 'cisa warns'
    ];
    
    const content = (article.title + ' ' + article.description).toLowerCase();
    return breakingKeywords.some(keyword => content.includes(keyword));
  };

  const startAnimation = () => {
    if (!contentRef.current || isPaused) return;

    const content = contentRef.current;
    const containerWidth = tickerRef.current.offsetWidth;
    const contentWidth = content.scrollWidth;
    
    // Reset position
    content.style.transform = `translateX(${containerWidth}px)`;
    
    // Calculate animation duration based on speed
    const duration = (containerWidth + contentWidth) / speed;
    
    // Apply animation
    content.style.transition = `transform ${duration}s linear`;
    content.style.transform = `translateX(-${contentWidth}px)`;
    
    // Restart animation when it completes
    setTimeout(() => {
      if (!isPaused) {
        startAnimation();
      }
    }, duration * 1000);
  };

  const handleMouseEnter = () => {
    if (pauseOnHover) {
      setIsPaused(true);
      if (contentRef.current) {
        const computedStyle = window.getComputedStyle(contentRef.current);
        const matrix = computedStyle.transform;
        contentRef.current.style.transition = 'none';
        contentRef.current.style.transform = matrix;
      }
    }
  };

  const handleMouseLeave = () => {
    if (pauseOnHover) {
      setIsPaused(false);
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      'Data Breach': 'text-red-600',
      'Ransomware': 'text-purple-600',
      'Vulnerability': 'text-orange-600',
      'Malware': 'text-yellow-600',
      'Cyber Attack': 'text-red-600',
      'Mobile Security': 'text-blue-600',
      'Cloud Security': 'text-cyan-600',
      'AI Security': 'text-green-600',
      'Critical Infrastructure': 'text-gray-600',
      'Privacy': 'text-indigo-600',
      'Phishing': 'text-pink-600',
      'General Security': 'text-gray-600'
    };
    return colors[category] || 'text-gray-600';
  };

  if (loading) {
    return (
      <div 
        className="bg-red-600 text-white overflow-hidden relative"
        style={{ height }}
      >
        <div className="flex items-center h-full px-4">
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            <span className="text-sm font-medium">Loading security alerts...</span>
          </div>
        </div>
      </div>
    );
  }

  if (articles.length === 0) {
    return (
      <div 
        className="bg-green-600 text-white overflow-hidden relative"
        style={{ height }}
      >
        <div className="flex items-center h-full px-4">
          <div className="flex items-center space-x-2">
            <span className="text-green-200">✓</span>
            <span className="text-sm font-medium">No critical security alerts at this time</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div 
      ref={tickerRef}
      className="bg-red-600 text-white overflow-hidden relative cursor-pointer"
      style={{ height }}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {/* Breaking News Label */}
      <div className="absolute left-0 top-0 h-full bg-red-700 px-3 flex items-center z-10">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
          <span className="text-sm font-bold uppercase tracking-wide">
            {showBreakingOnly ? 'Breaking' : 'Security News'}
          </span>
        </div>
      </div>

      {/* Scrolling Content */}
      <div 
        ref={contentRef}
        className="flex items-center h-full whitespace-nowrap ml-24"
      >
        {articles.map((article, index) => (
          <div key={index} className="inline-flex items-center">
            <a 
              href={article.link} 
              target="_blank" 
              rel="noopener noreferrer"
              className="hover:text-red-200 transition-colors duration-200"
            >
              <span className="flex items-center space-x-2">
                <span className={`text-xs px-2 py-1 rounded ${getCategoryColor(article.category)} bg-white bg-opacity-20`}>
                  {article.category}
                </span>
                <span className="text-sm font-medium">
                  {article.title}
                </span>
                <span className="text-xs text-red-200">
                  ({new Date(article.published_date).toLocaleDateString()})
                </span>
              </span>
            </a>
            {index < articles.length - 1 && (
              <span className="mx-8 text-red-300">•</span>
            )}
          </div>
        ))}
      </div>

      {/* Gradient Fade Effect */}
      <div className="absolute right-0 top-0 h-full w-12 bg-gradient-to-l from-red-600 to-transparent pointer-events-none"></div>
    </div>
  );
};

export default NewsTicker;

// Usage Examples:
/*
// Basic breaking news ticker
<NewsTicker />

// Custom speed and height
<NewsTicker speed={30} height="50px" />

// Breaking news only
<NewsTicker showBreakingOnly={true} maxArticles={3} />

// Slower ticker that doesn't pause on hover
<NewsTicker speed={20} pauseOnHover={false} />

// At the top of your website
<div className="fixed top-0 left-0 right-0 z-50">
  <NewsTicker showBreakingOnly={true} />
</div>
*/

