// app/page.js
// This is the main frontend component, redesigned to model langtech.com.

"use client";

import { useState } from 'react';
import styles from '../styles/Home.module.css';
import CybersecurityNews from '../components/CyberSecurityNews';

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

        {/* Enhanced Security in the News Section - Now with Real Data */}
        <section className={styles.newsSection}>
          <div className={styles.newsHeader}>
            <h3 className={styles.sectionTitle}>Security in the News</h3>
            <p className={styles.newsSubtitle}>Stay informed about the latest cybersecurity threats and developments</p>
          </div>
          
          {/* Real-time cybersecurity news feed */}
          <div className={styles.realNewsContainer}>
            <CybersecurityNews maxArticles={6} showImages={true} compact={false} />
          </div>
        </section>

        {/* Services Section */}
        <section className={styles.servicesSection}>
            <h3 className={styles.sectionTitle}>Our Services</h3>
            <div className={styles.servicesGrid}>
                <div className={styles.serviceCard}>
                    <div className={styles.serviceIcon}><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 14l9-5-9-5-9 5 9 5z"/><path d="M12 14l6.16-3.422a12.03 12.03 0 0 1 0-1.156L12 14z"/><path d="M12 14l-6.16-3.422a12.03 12.03 0 0 0 0-1.156L12 14z"/><path d="M12 14v7l9-5v-7l-9 5z"/><path d="M12 21v-7l-9-5v7l9 5z"/></svg></div>
                    <h4>Cybersecurity & AI Training</h4>
                    <p>Empower your team with the knowledge to navigate the complexities of modern cyber threats and leverage AI for a competitive advantage.</p>
                </div>
                <div className={styles.serviceCard}>
                    <div className={styles.serviceIcon}><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div>
                    <h4>Cybersecurity & AI Solutions</h4>
                    <p>We design and implement robust security architectures, including advanced IAM and PAM, integrated with intelligent AI-driven threat detection.</p>
                </div>
                <div className={styles.serviceCard}>
                    <div className={styles.serviceIcon}><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><polyline points="17 11 19 13 23 9"/></svg></div>
                    <h4>Cybersecurity & CISO Services</h4>
                    <p>Gain executive-level security leadership with our virtual CISO services, providing strategic guidance, risk management, and compliance oversight.</p>
                </div>
            </div>
        </section>

        {/* =============================================================== */}
        {/* ==================== AI AGENCY SECTION ======================= */}
        {/* =============================================================== */}
        <section className={styles.aiAgencySection}>
          <div className={styles.aiAgencyHeader}>
            <h3 className={styles.sectionTitle}>From our AI Agency Team</h3>
            <h4 className={styles.aiAgencySubtitle}>Never Miss a Customer Again: The AI Voice & Chat Agent Solution</h4>
            <p className={styles.aiAgencyIntro}>Every day, businesses lose money on missed calls, after-hours inquiries, and delayed responses. Our AI Agents transform this vulnerability into your greatest competitive advantage.</p>
          </div>
          
          <div className={styles.aiGrid}>
            {/* Box 1: The Problem */}
            <div className={`${styles.aiCard} ${styles.aiCardHighlight}`}>
              <h5>The Hidden Cost of Missed Opportunities</h5>
              <p>Customer inquiries pour in 24/7. When they're met with silence, it doesn't just create a poor experience—it hemorrhages revenue.</p>
              <div className={styles.aiFact}>
                <strong>The stark reality:</strong> Just one missed high-value inquiry can cost more than an entire year of AI automation.
              </div>
            </div>

            {/* Box 2: The Solution */}
            <div className={styles.aiCard}>
              <h5>The 24/7/365 Solution</h5>
              <p>Our AI Voice & Chat Agents work tirelessly to ensure no customer is ever ignored. They provide:</p>
              <ul>
                <li><span>✅</span> Instant, professional responses, day or night</li>
                <li><span>✅</span> Zero missed opportunities, even on holidays</li>
                <li><span>✅</span> Seamless lead capture and qualification</li>
              </ul>
            </div>

            {/* Box 3: The Economics */}
            <div className={styles.aiCard}>
              <h5>The Undeniable Economics</h5>
              <p>Transform customer service from a cost center into a profit engine. Your AI agent requires:</p>
              <ul>
                <li><span>❌</span> No salary, benefits, or sick days</li>
                <li><span>❌</span> No training costs or turnover</li>
                <li><span>❌</span> No breaks or shift changes</li>
              </ul>
            </div>

            {/* Box 4: The Features */}
            <div className={`${styles.aiCard} ${styles.aiCardFullWidth}`}>
              <h5>From Answering Questions to Driving Revenue</h5>
              <p>Our AI agents do more than just talk. They are fully integrated into your workflow to:</p>
              <div className={styles.featureGrid}>
                <ul>
                  <li>Capture leads when your sales team is unavailable</li>
                  <li>Schedule appointments automatically</li>
                  <li>Provide instant quotes and product information</li>
                </ul>
                <ul>
                  <li>Process orders around the clock</li>
                  <li>Answer questions from your knowledge base</li>
                  <li>Escalate urgent issues to the right team member</li>
                </ul>
              </div>
            </div>
          </div>

          <div className={styles.aiBottomLine}>
            <h5>The Bottom Line</h5>
            <p>Every hour you operate without an AI agent is an hour you're giving customers to your competitors. In today's economy, 24/7 availability isn't a luxury—it's a necessity. Your investment pays for itself the moment you capture that first after-hours lead that would have otherwise been lost forever.</p>
          </div>
        </section>
        {/* =============================================================== */}
        {/* ===================== AI AGENCY SECTION ENDS ================== */}
        {/* =============================================================== */}

        {/* Detailed Inquiry Section */}
        <section className={styles.inquirySection}>
            <div className={styles.sectionHeader}>
                <h3 className={styles.sectionTitle}>What is on your mind or To Do list?</h3>
                <p className={styles.sectionSubtitle}>Please provide us with some information, and we will get back to you to discuss how we can assist.</p>
            </div>
            {response && (<div className={`${styles.flash} ${styles[response.category]}`}>{response.message}</div>)}
            <form onSubmit={handleContactSubmit} className={styles.contactForm}>
                <div className={styles.formGrid}><div className={styles.formGroup}><label htmlFor="name">Your Name *</label><input type="text" id="name" name="name" value={formData.name} onChange={handleInputChange} placeholder="e.g., Jane Doe" required disabled={isLoading} /></div><div className={styles.formGroup}><label htmlFor="email">Your Email *</label><input type="email" id="email" name="email" value={formData.email} onChange={handleInputChange} placeholder="e.g., jane.doe@example.com" required disabled={isLoading} /></div><div className={styles.formGroup}><label htmlFor="website">Your Company Website</label><input type="url" id="website" name="website" value={formData.website} onChange={handleInputChange} placeholder="https://your-company.com" disabled={isLoading} /></div><div className={styles.formGroup}><label htmlFor="phone">Your Phone Number</label><input type="tel" id="phone" name="phone" value={formData.phone} onChange={handleInputChange} placeholder="(555) 123-467" disabled={isLoading} /></div></div>
                <div className={styles.formGroup}><label htmlFor="inquiry">Your Inquiry *</label><textarea id="inquiry" name="inquiry" value={formData.inquiry} onChange={handleInputChange} placeholder="Tell us about your project or how we can help..." rows="5" required disabled={isLoading} /></div>
                <button type="submit" className={styles.submitBtn} disabled={isLoading}>{isLoading ? 'Submitting...' : 'Submit Inquiry'}</button>
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

