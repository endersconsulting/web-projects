// app/page.js
// This is the main frontend component, updated with the new contact form.

"use client";

import { useState } from 'react';
import styles from '../styles/Home.module.css';

export default function Home() {
  // State to handle the new, more detailed form fields
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    website: '',
    phone: '',
    inquiry: ''
  });

  // State for the general AI assistant form at the bottom
  const [query, setQuery] = useState('');
  
  const [response, setResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // A single handler for input changes in the detailed contact form
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handler for the detailed contact form submission
  const handleContactSubmit = async (e) => {
    e.preventDefault();
    
    // Basic validation for required fields
    if (!formData.name.trim() || !formData.email.trim() || !formData.inquiry.trim()) {
      setResponse({
        category: 'error',
        message: 'Please fill out all required fields: Name, Email, and Inquiry.'
      });
      return;
    }

    // Email format validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setResponse({
        category: 'error',
        message: 'Please enter a valid email address.'
      });
      return;
    }

    setIsLoading(true);
    setResponse(null);

    // --- Trigger n8n Webhook with detailed prospect data ---
    try {
      const webhookPayload = {
        source: 'endersconsulting.cloud-contact-form',
        name: formData.name.trim(),
        email: formData.email.trim(),
        website: formData.website.trim(),
        phone: formData.phone.trim(),
        inquiry: formData.inquiry.trim(),
        timestamp: new Date().toISOString()
      };

      // Using the new webhook URL you provided
      await fetch('https://rainerai.app.n8n.cloud/webhook-test/7e51e32e-4819-45e8-a12b-de784f97f71f', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(webhookPayload)
      });

      setResponse({
          category: 'success',
          message: 'Thank you for your inquiry! We have received your information and will get back to you shortly.'
      });
      
      // Clear form after successful submission
      setFormData({ name: '', email: '', website: '', phone: '', inquiry: '' });

    } catch (n8nError) {
      console.error("Failed to trigger n8n webhook:", n8nError);
      setResponse({
        category: 'error',
        message: 'Sorry, we encountered an issue submitting your form. Please try again later.'
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Handler for the simple AI assistant form at the bottom
  const handleQuerySubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setResponse(null);
    
    try {
      const res = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      if (!res.ok) throw new Error('Network response was not ok');

      const data = await res.json();
      setResponse(data);
      setQuery(''); // Clear query input
    } catch (error) {
      setResponse({
        category: 'error',
        message: 'Sorry, something went wrong. Please try again later.',
      });
      console.error("Failed to fetch from API:", error);
    } finally {
      setIsLoading(false);
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
          <a href="mailto:info@endersconsulting.cloud">Contact</a>
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

        {/* Existing Services Section - MOVED UP */}
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

        {/* Detailed Inquiry Section - MOVED DOWN */}
        <section className={styles.inquirySection}>
            <div className={styles.sectionHeader}>
                <h3 className={styles.sectionTitle}>What is on your mind or To Do list?</h3>
                <p className={styles.sectionSubtitle}>How can we assist you? Please provide us with some pieces of information and we will get back to you to discuss.</p>
            </div>

            {/* Response Message Display Area for this form */}
            {response && (
              <div className={`${styles.flash} ${styles[response.category]}`}>
                {response.message}
              </div>
            )}

            <form onSubmit={handleContactSubmit} className={styles.contactForm}>
                <div className={styles.formGrid}>
                    <div className={styles.formGroup}>
                        <label htmlFor="name">Your Name *</label>
                        <input type="text" id="name" name="name" value={formData.name} onChange={handleInputChange} placeholder="e.g., Jane Doe" required disabled={isLoading} />
                    </div>
                    <div className={styles.formGroup}>
                        <label htmlFor="email">Your Email *</label>
                        <input type="email" id="email" name="email" value={formData.email} onChange={handleInputChange} placeholder="e.g., jane.doe@example.com" required disabled={isLoading} />
                    </div>
                    <div className={styles.formGroup}>
                        <label htmlFor="website">Your Company Website</label>
                        <input type="url" id="website" name="website" value={formData.website} onChange={handleInputChange} placeholder="https://your-company.com" disabled={isLoading} />
                    </div>
                    <div className={styles.formGroup}>
                        <label htmlFor="phone">Your Phone Number</label>
                        <input type="tel" id="phone" name="phone" value={formData.phone} onChange={handleInputChange} placeholder="(555) 123-4567" disabled={isLoading} />
                    </div>
                </div>
                <div className={styles.formGroup}>
                    <label htmlFor="inquiry">Your Inquiry *</label>
                    <textarea id="inquiry" name="inquiry" value={formData.inquiry} onChange={handleInputChange} placeholder="Tell us about your project or how we can help..." rows="5" required disabled={isLoading} />
                </div>
                <button type="submit" className={styles.submitBtn} disabled={isLoading}>
                    {isLoading ? 'Submitting...' : 'Submit Inquiry'}
                </button>
            </form>
        </section>

        {/* AI Agent Interaction Section */}
        <section className={styles.agentSection}>
          <h3>Have a Quick Question?</h3>
          <p>Ask our AI assistant for a fast response.</p>
          
          <form onSubmit={handleQuerySubmit} className={styles.agentForm}>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Type your general question here..."
              rows="4"
              disabled={isLoading}
            />
            <button type="submit" className={styles.submitBtn} disabled={isLoading}>
              {isLoading ? 'Asking...' : 'Ask AI'}
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
