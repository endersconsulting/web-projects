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

        {/* Security in the News Section */}
        <section className={styles.newsSection}>
          <h3 className={styles.sectionTitle}>Security in the News</h3>
          <div className={styles.newsGrid}>
            <div className={styles.newsCard}>
              <h4>Major Tech Firm Breached</h4>
              <p>A significant data breach affecting millions highlights the importance of multi-factor authentication and proactive threat monitoring...</p>
              <a href="#" className={styles.readMoreLink}>Read More</a>
            </div>
            <div className={styles.newsCard}>
              <h4>Rise of AI in Phishing Attacks</h4>
              <p>Cybercriminals are now leveraging generative AI to create more convincing phishing emails, making employee training more critical than ever.</p>
              <a href="#" className={styles.readMoreLink}>Read More</a>
            </div>
            <div className={styles.newsCard}>
              <h4>New Compliance Regulations</h4>
              <p>A new set of data privacy regulations will come into effect next quarter, impacting how businesses handle customer information.</p>
              <a href="#" className={styles.readMoreLink}>Read More</a>
            </div>
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
        {/* ==================== NEW SECTION STARTS HERE ================== */}
        {/* =============================================================== */}
        <section className={styles.aiAgencySection}>
          <div className={styles.aiAgencyContent}>
            <h3 className={styles.sectionTitle}>From our AI Agency Team</h3>
            
            <h4 className={styles.aiAgencySubtitle}>Never Miss Another Customer Again: The AI Voice & Chat Agent Solution</h4>
            
            <div className={styles.aiAgencyBlock}>
              <h5>The Hidden Cost of Missed Opportunities</h5>
              <p>Every day, your business loses money while you sleep. Customer inquiries pour in at 2 AM, potential clients call during lunch breaks, and prospects reach out over weekends—only to be met with silence. These missed touchpoints don't just create poor customer experiences; they hemorrhage revenue.</p>
              <p><strong>The stark reality:</strong> Just one missed high-value customer inquiry can cost more than an entire year's investment in AI automation.</p>
            </div>

            <div className={styles.aiAgencyBlock}>
              <h5>The 24/7/365 Solution That Pays for Itself</h5>
              <p>Our AI Voice & Chat Agent transforms your customer engagement from a liability into your greatest competitive advantage:</p>
              <div className={styles.featureGrid}>
                <div>
                  <h6>Always-On Customer Engagement</h6>
                  <ul>
                    <li>No downtime: While your competitors sleep, your AI agent closes deals</li>
                    <li>Instant response: Every inquiry answered in seconds, not hours or days</li>
                    <li>Perfect consistency: Professional, knowledgeable responses every single time</li>
                  </ul>
                </div>
                <div>
                  <h6>Immediate ROI Through Revenue Protection</h6>
                  <ul>
                    <li>Zero missed opportunities: Capture every lead, even at 3 AM on holidays</li>
                    <li>Qualified lead generation: Pre-screen and route high-value prospects automatically</li>
                    <li>Customer retention: Resolve issues instantly before they escalate to cancellations</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className={styles.aiAgencyBlock}>
              <h5>The Economics Are Undeniable</h5>
              <p>Unlike human staff, your AI agent requires:</p>
              <ul className={styles.economicsList}>
                <li><span>❌</span> No salary or benefits</li>
                <li><span>❌</span> No vacation time or sick days</li>
                <li><span>❌</span> No training costs or turnover</li>
                <li><span>❌</span> No breaks or shift changes</li>
                <li><span>✅</span> Just one recovered deal breaks even on your entire investment</li>
              </ul>
            </div>

            <div className={styles.aiAgencyBlock}>
              <h5>From Cost Center to Profit Engine</h5>
              <p>Transform customer service from an expense into a revenue-generating machine. Your AI agent doesn't just answer questions—it:</p>
              <ul>
                <li>Captures leads when your sales team is unavailable</li>
                <li>Schedules appointments automatically</li>
                <li>Provides instant quotes and product information</li>
                <li>Processes orders around the clock</li>
                <li>Answers key questions from your Knowledge Base and FAQ</li>
                <li>Escalates urgent issues to the right team member immediately</li>
              </ul>
            </div>

            <div className={styles.aiAgencyBlock}>
              <h5>The Bottom Line</h5>
              <p>Every hour your business operates without AI voice and chat agents, you're voluntarily giving competitors access to your potential customers. In today's always-connected economy, availability isn't just a convenience—it's a competitive necessity.</p>
              <p><strong>Your investment pays for itself the moment you capture that first after-hours lead that would have otherwise walked away.</strong></p>
              <p>Ready to stop losing customers to missed opportunities? Let's discuss how AI agents can transform your business operations and protect your revenue 24/7.</p>
            </div>
          </div>
        </section>
        {/* =============================================================== */}
        {/* ===================== NEW SECTION ENDS HERE =================== */}
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