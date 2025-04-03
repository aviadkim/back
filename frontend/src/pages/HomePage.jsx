import React from 'react';
import HeroSection from '../components/home/HeroSection';
import FeaturesSection from '../components/home/FeaturesSection';
import HowItWorksSection from '../components/home/HowItWorksSection';
import UseCasesSection from '../components/home/UseCasesSection';
import DemoSection from '../components/home/DemoSection';
import FaqSection from '../components/home/FaqSection';
import CtaSection from '../components/home/CtaSection';
import './HomePage.css'; // Ensure CSS is imported

/**
 * דף הבית של האפליקציה
 */
const HomePage = () => {
  return (
    <div className="home-page">
      <HeroSection />
      <FeaturesSection />
      <HowItWorksSection />
      <UseCasesSection />
      <DemoSection /> {/* Placeholder content */}
      <FaqSection /> {/* Placeholder content */}
      <CtaSection /> {/* Placeholder content */}
    </div>
  );
};

export default HomePage;