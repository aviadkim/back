#!/usr/bin/env node
// scripts/setup.js - סקריפט התקנה מהירה
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const readline = require('readline');
const crypto = require('crypto');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

const question = (query) => new Promise((resolve) => rl.question(query, resolve));

// פונקציה ליצירת משתמש התחלתי
async function createInitialUser(db) {
  return new Promise((resolve, reject) => {
    rl.question('האם ליצור משתמש ראשוני? (כן/לא): ', (answer) => {
      if (answer.toLowerCase() === 'כן' || answer.toLowerCase() === 'y' || answer.toLowerCase() === 'yes') {
        const User = require('../backend/models/User');
        
        const testUser = {
          id: crypto.randomUUID(),
          email: 'test@example.com',
          password: 'password123',
          name: 'משתמש לדוגמה',
          organization: 'ארגון לדוגמה',
          role: 'user'
        };
        
        User.create(testUser)
          .then(user => {
            console.log('משתמש ראשוני נוצר בהצלחה:');
            console.log(`אימייל: ${testUser.email}`);
            console.log(`סיסמה: ${testUser.password}`);
            resolve();
          })
          .catch(error => {
            console.error('שגיאה ביצירת משתמש ראשוני:', error);
            resolve();
          });
      } else {
        resolve();
      }
    });
  });
}

// פונקציה ראשית
async function main() {
  try {
    console.log('מתחיל תהליך התקנה...');
    
    // יצירת תיקיות נדרשות
    const dirs = [
      './storage',
      './data',
      './models',
      './backend/routes',
      './backend/controllers',
      './backend/config',
      './backend/middleware',
      './backend/services'
    ];
    
    dirs.forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
        console.log(`נוצרה תיקייה: ${dir}`);
      }
    });
    
    // יצירת קובץ .env
    const envContent = fs.readFileSync('.env', 'utf8');
    fs.writeFileSync('.env', envContent);
    console.log('קובץ .env עודכן');
    
    // התקנת תלויות Node.js
    console.log('מתקין תלויות Node.js...');
    execSync('npm install', { stdio: 'inherit' });
    
    // התקנת תלויות Python
    console.log('מתקין תלויות Python...');
    execSync('pip install -r requirements.txt', { stdio: 'inherit' });
    
    // התקנת EasyOCR
    console.log('מתקין EasyOCR...');
    try {
      execSync('pip install easyocr', { stdio: 'inherit' });
      console.log('EasyOCR הותקן בהצלחה');
    } catch (error) {
      console.error('שגיאה בהתקנת EasyOCR:', error);
      console.log('אנא התקן ידנית: pip install easyocr');
    }
    
    // הורדת מודלים בסיסיים
    console.log('האם להוריד מודלים בסיסיים? תהליך זה עשוי לקחת מספר דקות (כן/לא):');
    const downloadModels = await new Promise((resolve) => {
      rl.question('', (answer) => {
        resolve(answer.toLowerCase() === 'כן' || answer.toLowerCase() === 'y' || answer.toLowerCase() === 'yes');
      });
    });
    
    if (downloadModels) {
      console.log('מוריד מודלים בסיסיים...');
      execSync('python scripts/download_models.py', { stdio: 'inherit' });
    }
    
    // יצירת משתמש ראשוני
    await createInitialUser();
    
    console.log('התקנה הושלמה בהצלחה!');
    console.log('הפעל את המערכת עם הפקודה: npm start');
    console.log('וגש אל http://localhost:5000 בדפדפן שלך');
    
    rl.close();
  } catch (error) {
    console.error('שגיאה בהתקנה:', error);
    process.exit(1);
  }
}

main(); 