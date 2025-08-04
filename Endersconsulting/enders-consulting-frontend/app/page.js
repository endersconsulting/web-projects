// app/page.js
// This is the main frontend component for the homepage, updated with new service descriptions.

"use client"; // This directive is essential for components using hooks like useState.

import { useState } from 'react';
import styles from '../styles/Home.module.css';

export default function Home() {
  // State variables to manage the form input and the response from the API
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Function to handle the form submission
  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent default form submission behavior
    if (!query.trim()) return; // Don't submit if the query is empty

    setIsLoading(true);
    setResponse(null);

    try {
      // Send a POST request to our Flask backend API
      const res = await fetch('http://localhost:5001/api/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!res.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await res.json();
      setResponse(data); // Store the response from the API
    } catch (error) {
      // Handle errors (e.g., network issue or API error)
      setResponse({
        category: 'error',
        message: 'Sorry, something went wrong. Please try again later.',
      });
      console.error("Failed to fetch from API:", error);
    } finally {
      setIsLoading(false); // Stop the loading indicator
    }
  };

  return (
    <div className={styles.container}>
      {/* Header Section */}
      <header className={styles.header}>
        <div className={styles.logo}>
          <h1>Enders Consulting</h1>
        </div>
        <nav className={styles.navigation}>
          <a href="#">Home</a>
          <a href="#">About Us</a>
          <a href="#">Services</a>
          <a href="#">Contact</a>
        </nav>
      </header>

      <main>
        {/* Hero Section */}
        <section className={styles.hero}>
          <div className={styles.heroContent}>
            <h2>Achieving Excellence, Together.</h2>
            <p>We partner with visionary leaders to solve their most critical challenges, leveraging AI-powered solutions and implementing fortress-level security for your digital assets.</p>
          </div>
        </section>

        {/* New Services Section */}
        <section className={styles.servicesSection}>
            <h3 className={styles.sectionTitle}>Our Core Expertise</h3>
            <div className={styles.servicesGrid}>
                <div className={styles.serviceCard}>
                    <h4>AI-Powered Business Solutions</h4>
                    <p>We harness the power of artificial intelligence to unlock new efficiencies, drive innovation, and create intelligent workflows. From predictive analytics to automated processes, our solutions are tailored to give your business a competitive edge.</p>
                </div>
                <div className={styles.serviceCard}>
                    <h4>High-Security Identity & Access Management</h4>
                    <p>In a world of evolving threats, we design and implement high-security Identity Access Management (IAM) and Privileged Access & Endpoint Management (PAM/PEDM) solutions to protect your most critical systems and data.</p>
                </div>
            </div>
        </section>

        {/* AI Agent Interaction Section */}
        <section className={styles.agentSection}>
          <h3>Have a Question? Ask Our AI Assistant.</h3>

          {/* Response Message Display Area */}
          {response && (
            <div className={`${styles.flash} ${styles[response.category]}`}>
              {response.message}
            </div>
          )}

          {/* Form for submitting inquiries */}
          <form onSubmit={handleSubmit} className={styles.agentForm}>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Type your inquiry here... e.g., 'What services do you offer?'"
              rows="4"
              disabled={isLoading}
            />
            <button type="submit" className={styles.submitBtn} disabled={isLoading}>
              {isLoading ? 'Submitting...' : 'Submit Inquiry'}
            </button>
          </form>
        </section>
      </main>

      {/* Footer Section */}
      <footer className={styles.footer}>
        <p>&copy; 2025 endersconsulting.cloud. All Rights Reserved.</p>
      </footer>
    </div>
  );
}
