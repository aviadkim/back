import React from 'react';
import './UseCasesSection.css';

/**
 * רכיב המציג מקרי שימוש של המערכת
 */
const UseCasesSection = () => {
  // מערך מקרי שימוש
  const useCases = [
    {
      id: 'portfolio',
      title: 'ניתוח תיק השקעות',
      description: 'העלאת דוחות תיק השקעות למעקב אחר ביצועים במספר חשבונות וניתוח מגמות לאורך זמן.',
      icon: 'fa-chart-pie', // Font Awesome class
      imageSrc: '/assets/portfolio-analysis.png', // Path relative to public folder
      imageAlt: 'לוח מחוונים ניתוח תיק השקעות'
    },
    {
      id: 'reporting',
      title: 'דיווח פיננסי',
      description: 'חילוץ מדדים מרכזיים מדוחות פיננסיים לניתוח מהיר יותר והשוואה בין תקופות ומתחרים.',
      icon: 'fa-file-invoice-dollar', // Font Awesome class
      imageSrc: '/assets/financial-reporting.png', // Path relative to public folder
      imageAlt: 'מדדים שחולצו מדוח שנתי'
    },
    {
      id: 'compliance',
      title: 'עמידה ברגולציה',
      description: 'מעקב אוטומטי אחר מספרי ISIN וניירות ערך במסמכים לצורך עמידה בדרישות רגולטוריות.',
      icon: 'fa-tasks', // Font Awesome class
      imageSrc: '/assets/compliance-dashboard.png', // Path relative to public folder
      imageAlt: 'לוח מחוונים למעקב עמידה ברגולציה'
    }
  ];

  // Fallback image handler
  const handleImageError = (e) => {
      // Replace with a generic placeholder if the specific image fails to load
      e.target.src = '/assets/placeholder-image.svg'; // Ensure placeholder exists
      e.target.alt = 'תמונה לא זמינה';
  };


  return (
    <section id="use-cases" className="use-cases-section">
      <div className="container">
        <div className="section-header">
          <h2>שימושים נפוצים</h2>
          <p className="section-subheading">אופנים שונים לשימוש במערכת לצרכים פיננסיים</p>
        </div>

        <div className="use-cases-grid">
          {useCases.map((useCase) => (
            <div key={useCase.id} className="use-case-card">
              <div className="use-case-icon">
                <i className={`fas ${useCase.icon}`}></i> {/* Use Font Awesome */}
              </div>
              <h3 className="use-case-title">{useCase.title}</h3>
              <p className="use-case-description">{useCase.description}</p>
              <div className="use-case-image-container">
                <img
                  src={useCase.imageSrc}
                  alt={useCase.imageAlt}
                  className="use-case-image"
                  onError={handleImageError} // Add error handler
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default UseCasesSection;