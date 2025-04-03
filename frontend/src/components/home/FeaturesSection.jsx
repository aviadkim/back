// src/components/home/FeaturesSection.jsx
import React from 'react';
import FeatureCard from './FeatureCard';
import './FeaturesSection.css';

function FeaturesSection() {
  const features = [
    {
      icon: 'language',
      title: 'עיבוד מסמכים רב-לשוני',
      description: 'זיהוי טקסט בדיוק גבוה בעברית ובאנגלית, כולל מסמכים מעורבים',
      link: '/features/multilingual'
    },
    {
      icon: 'table',
      title: 'חילוץ טבלאות אוטומטי',
      description: 'זיהוי וחילוץ אוטומטי של טבלאות באמצעות אלגוריתמי AI מתקדמים',
      link: '/features/tables'
    },
    {
      icon: 'barcode',
      title: 'זיהוי מספרי ISIN',
      description: 'זיהוי אוטומטי של מספרי ISIN, שמות חברות ומדדים פיננסיים בדיוק גבוה',
      link: '/features/isin'
    },
    {
      icon: 'chart',
      title: 'חקירת נתונים אינטראקטיבית',
      description: 'חקירת נתונים שחולצו באמצעות לוחות מחוונים אינטראקטיביים ומסננים מתקדמים',
      link: '/features/data-exploration'
    },
    {
      icon: 'robot',
      title: 'עוזר מסמכים חכם',
      description: 'שאל שאלות על המסמכים שלך בשפה טבעית וקבל תשובות מדויקות באופן מיידי',
      link: '/features/chat'
    },
    {
      icon: 'export',
      title: 'ייצוא וניתוח מתקדם',
      description: 'ייצוא נתונים לפורמטים מובנים וניתוח מתקדם למציאת תובנות חבויות במסמכים',
      link: '/features/export'
    }
  ];

  return (
    <section id="features" className="features-section">
      <div className="container">
        <div className="section-header">
          <h2 className="section-title">יכולות המערכת</h2>
          <p className="section-description">טכנולוגיה מתקדמת לטיפול במסמכים פיננסיים</p>
        </div>
        <div className="features-grid">
          {features.map((feature, index) => (
            <FeatureCard key={index} feature={feature} />
          ))}
        </div>
      </div>
    </section>
  );
}

export default FeaturesSection;