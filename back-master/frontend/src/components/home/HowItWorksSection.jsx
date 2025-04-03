import React from 'react';
import './HowItWorksSection.css';

const HowItWorksSection = () => {
  const steps = [
    {
      number: 1,
      title: 'העלאת המסמך',
      description: 'העלה מסמך PDF, Excel או CSV למערכת',
      icon: 'fa-file-upload' // Font Awesome class
    },
    {
      number: 2,
      title: 'עיבוד אוטומטי',
      description: 'הבינה המלאכותית מעבדת את המסמך ומחלצת מידע',
      icon: 'fa-cogs' // Font Awesome class
    },
    {
      number: 3,
      title: 'סקירת התוצאות',
      description: 'סקור את הטבלאות, הישויות והמדדים שחולצו',
      icon: 'fa-search' // Font Awesome class
    },
    {
      number: 4,
      title: 'חקירה ושאילתות',
      description: 'שאל שאלות וצור טבלאות מותאמות אישית',
      icon: 'fa-comments' // Font Awesome class
    },
    {
      number: 5,
      title: 'ייצוא ושיתוף',
      description: 'ייצא את הנתונים המעובדים בפורמט המועדף עליך',
      icon: 'fa-share-alt' // Font Awesome class
    }
  ];

  return (
    <section id="how-it-works" className="how-it-works-section">
      <div className="container">
        <div className="section-header">
          <h2>איך זה עובד</h2>
          <p className="section-subheading">תהליך פשוט בחמישה שלבים</p>
        </div>

        <div className="steps-container">
          {/* קו תהליך אופקי שיוצג רק במסכים בינוניים וגדולים */}
          <div className="timeline-line"></div>

          <div className="steps">
            {steps.map((step) => (
              <div className="step-item" key={step.number}>
                <div className="step-number">
                  <span>{step.number}</span>
                </div>
                <h3 className="step-title">{step.title}</h3>
                <p className="step-description">{step.description}</p>
                <div className="step-icon">
                  {/* Using Font Awesome icons */}
                  <i className={`fas ${step.icon}`}></i>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Optional CTA Button */}
        {/*
        <div className="cta-container">
          <button className="cta-button">
            התחל עכשיו
          </button>
        </div>
        */}
      </div>
    </section>
  );
};

export default HowItWorksSection;