// app/page.js
// This is the main frontend component, redesigned to model langtech.com.

"use client";

import { useState } from 'react';
import styles from '../styles/Home.module.css';

export default function Home() {
  // State for the detailed contact form
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    website: '',
    phone: '',
    inquiry: ''
  });
  
  const [response, setResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Handler for input changes in the contact form
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handler for the contact form submission
  const handleContactSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name.trim() || !formData.email.trim() || !formData.inquiry.trim()) {
      setResponse({
        category: 'error',
        message: 'Please fill out all required fields: Name, Email, and Inquiry.'
      });
      return;
    }

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

      await fetch('https://rainerai.app.n8n.cloud/webhook/7e51e32e-4819-45e8-a12b-de784f97f71f', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(webhookPayload)
      });

      setResponse({
          category: 'success',
          message: 'Thank you for your inquiry! We have received your information and will get back to you shortly.'
      });
      
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
          <a href="mailto:info@endersconsulting.cloud" className={styles.contactButton}>Contact Us</a>
        </nav>
      </header>

      <main>
        {/* Hero Section */}
        <section className={styles.hero}>
          <div className={styles.heroContent}>
            <h2>AI-Powered Security and Business Transformation</h2>
            <p>We deliver cutting-edge Cybersecurity and AI solutions to protect your assets and accelerate your growth.</p>
          </div>
        </section>

        {/* NEW Services Section */}
        <section className={styles.servicesSection}>
            <h3 className={styles.sectionTitle}>Our Services</h3>
            <div className={styles.servicesGrid}>
                <div className={styles.serviceCard}>
                    <div className={styles.serviceIcon}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 14l9-5-9-5-9 5 9 5z"/><path d="M12 14l6.16-3.422a12.03 12.03 0 0 1 0-1.156L12 14z"/><path d="M12 14l-6.16-3.422a12.03 12.03 0 0 0 0-1.156L12 14z"/><path d="M12 14v7l9-5v-7l-9 5z"/><path d="M12 21v-7l-9-5v7l9 5z"/></svg>
                    </div>
                    <h4>Cybersecurity & AI Training</h4>
                    <p>Empower your team with the knowledge to navigate the complexities of modern cyber threats and leverage AI for a competitive advantage.</p>
                </div>
                <div className={styles.serviceCard}>
                    <div className={styles.serviceIcon}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                    </div>
                    <h4>Cybersecurity & AI Solutions</h4>
                    <p>We design and implement robust security architectures, including advanced IAM and PAM, integrated with intelligent AI-driven threat detection.</p>
                </div>
                <div className={styles.serviceCard}>
                    <div className={styles.serviceIcon}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><polyline points="17 11 19 13 23 9"/></svg>
                    </div>
                    <h4>Cybersecurity & CISO Services</h4>
                    <p>Gain executive-level security leadership with our virtual CISO services, providing strategic guidance, risk management, and compliance oversight.</p>
                </div>
            </div>
        </section>

        {/* Detailed Inquiry Section */}
        <section className={styles.inquirySection}>
            <div className={styles.sectionHeader}>
                <h3 className={styles.sectionTitle}>What is on your mind or To Do list?</h3>
                <p className={styles.sectionSubtitle}>Please provide us with some information, and we will get back to you to discuss how we can assist.</p>
            </div>

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
      </main>

      {/* Footer Section */}
      <footer className={styles.footer}>
        <p>&copy; 2025 endersconsulting.cloud. All Rights Reserved.</p>
      </footer>
    </div>
  );
}
