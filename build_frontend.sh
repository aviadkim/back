#!/bin/bash

echo "===== בונה את הפרונטאנד העשיר בעברית ====="

# יצירת תיקיית frontend אם לא קיימת
mkdir -p frontend/src/components
mkdir -p frontend/src/assets
mkdir -p frontend/public

# נקה קבצים שגויים אם קיימים
rm -f frontend/src/components/Navbar.jsx

# יצירת קובץ logo.svg
cat > frontend/src/assets/logo.svg << 'EOF'
<svg width="200" height="50" xmlns="http://www.w3.org/2000/svg">
  <rect width="200" height="50" fill="#4A90E2"/>
  <text x="20" y="35" font-family="Arial" font-size="24" fill="white">FinDoc Analyzer</text>
</svg>
EOF

# יצירת קובץ package.json בסיסי
cat > frontend/package.json << 'EOF'
{
  "name": "findoc-analyzer-frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
EOF

# יצירת public/index.html
cat > frontend/public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="he" dir="rtl">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#4A90E2" />
    <meta
      name="description"
      content="FinDoc Analyzer - מערכת לניתוח מסמכים פיננסיים"
    />
    <title>FinDoc Analyzer</title>
    <style>
      body {
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
        direction: rtl;
      }
      
      .app-header {
        background-color: #4A90E2;
        color: white;
        padding: 1rem;
        text-align: center;
      }
      
      .app-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
      }
      
      .hero-section {
        background-color: #f5f9ff;
        padding: 4rem 2rem;
        text-align: center;
        margin-bottom: 2rem;
        border-radius: 8px;
      }
      
      .hero-title {
        font-size: 2.5rem;
        margin-bottom: 1rem;
      }
      
      .hero-description {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
      }
      
      .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 2rem;
      }
      
      .feature-card {
        background-color: white;
        border-radius: 8px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
      }
      
      .feature-icon {
        background-color: rgba(74, 144, 226, 0.1);
        width: 80px;
        height: 80px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1.5rem;
        font-size: 2rem;
        color: #4A90E2;
      }
      
      .btn-primary {
        background-color: #4A90E2;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 4px;
        font-size: 1.1rem;
        cursor: pointer;
        display: inline-block;
        text-decoration: none;
      }
      
      .footer {
        background-color: #2C3E50;
        color: white;
        padding: 2rem;
        text-align: center;
        margin-top: 3rem;
      }
    </style>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root">
      <!-- תוכן ברירת המחדל במקרה שהריאקט לא נטען -->
      <header class="app-header">
        <h1>FinDoc Analyzer</h1>
      </header>
      
      <main class="app-container">
        <section class="hero-section">
          <h1 class="hero-title">הפיכת מסמכים פיננסיים לתובנות פעילות</h1>
          <p class="hero-description">
            פלטפורמה מבוססת בינה מלאכותית המחלצת, מנתחת ומארגנת מידע ממסמכים פיננסיים בעברית ובאנגלית
          </p>
          <a href="/documents" class="btn-primary">העלה מסמך</a>
        </section>
        
        <section>
          <h2 style="text-align: center; margin-bottom: 2rem;">יכולות המערכת</h2>
          <div class="features-grid">
            <div class="feature-card">
              <div class="feature-icon">📄</div>
              <h3>עיבוד מסמכים רב-לשוני</h3>
              <p>זיהוי טקסט בדיוק גבוה בעברית ובאנגלית, כולל מסמכים מעורבים</p>
            </div>
            <div class="feature-card">
              <div class="feature-icon">📊</div>
              <h3>חילוץ טבלאות אוטומטי</h3>
              <p>זיהוי וחילוץ אוטומטי של טבלאות באמצעות אלגוריתמי AI מתקדמים</p>
            </div>
            <div class="feature-card">
              <div class="feature-icon">🤖</div>
              <h3>עוזר מסמכים חכם</h3>
              <p>שאל שאלות על המסמכים שלך בשפה טבעית וקבל תשובות מדויקות באופן מיידי</p>
            </div>
          </div>
        </section>
      </main>
      
      <footer class="footer">
        <p>© 2025 FinDoc Analyzer. כל הזכויות שמורות.</p>
      </footer>
    </div>
  </body>
</html>
EOF

# יצירת המבנה הבסיסי של תיקיית build
mkdir -p frontend/build

# העתקת index.html לתיקיית build
cp frontend/public/index.html frontend/build/index.html

# העתקת הלוגו לתיקיית build
mkdir -p frontend/build/static/media
cp frontend/src/assets/logo.svg frontend/build/static/media/

echo "===== בניית הפרונטאנד הסתיימה ====="
echo "כעת אפשר להריץ את האפליקציה עם הפקודה:"
echo "python simple_app.py"
