const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const dotenv = require('dotenv');

// טען משתני סביבה
dotenv.config();

// תהליכים שרצים במקביל
let backendProcess = null;
let frontendProcess = null;

// פונקציה להפעלת השרת האחורי
function startBackend() {
  console.log('מפעיל שרת אחורי...');
  
  backendProcess = spawn('node', ['app.js'], {
    stdio: 'inherit',
    env: process.env
  });
  
  backendProcess.on('close', (code) => {
    if (code !== 0 && code !== null) {
      console.error(`שרת אחורי נסגר עם קוד שגיאה: ${code}`);
      setTimeout(startBackend, 5000);
    }
  });
}

// פונקציה להפעלת צד לקוח
function startFrontend() {
  // בדוק אם יש תיקיית frontend
  if (!fs.existsSync(path.join(__dirname, '../frontend'))) {
    console.warn('תיקיית frontend לא נמצאה, מדלג על הפעלת שרת פיתוח קדמי');
    return;
  }
  
  console.log('מפעיל שרת פיתוח קדמי...');
  
  frontendProcess = spawn('npm', ['start'], {
    stdio: 'inherit',
    cwd: path.join(__dirname, '../frontend'),
    env: { ...process.env, BROWSER: 'none' }
  });
  
  frontendProcess.on('close', (code) => {
    if (code !== 0 && code !== null) {
      console.error(`שרת קדמי נסגר עם קוד שגיאה: ${code}`);
      setTimeout(startFrontend, 5000);
    }
  });
}

// טיפול בסגירת תכנית
function cleanup() {
  console.log('סוגר תהליכים...');
  
  if (backendProcess) {
    backendProcess.kill();
  }
  
  if (frontendProcess) {
    frontendProcess.kill();
  }
  
  process.exit(0);
}

// רישום לאירועי סגירה
process.on('SIGINT', cleanup);
process.on('SIGTERM', cleanup);

// הפעלת שרתים
startBackend();
startFrontend();

console.log('שרתי פיתוח פועלים. לחץ Ctrl+C לסיום.'); 