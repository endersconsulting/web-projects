"use client";

import { useEffect } from 'react';

export default function WebinarTool() {
  useEffect(() => {
    // Redirect to the Flask backend webinar tool
    window.location.href = '/api/webinar-tool';
  }, []);

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh',
      fontFamily: 'Arial, sans-serif'
    }}>
      <div>
        <h2>Loading Webinar Discovery Tool...</h2>
        <p>Redirecting to secure login...</p>
      </div>
    </div>
  );
}
