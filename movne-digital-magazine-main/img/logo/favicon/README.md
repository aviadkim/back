# קבצי Favicon למגזין הדיגיטלי

תיקייה זו מיועדת לאייקונים שיוצגו בכרטיסיות הדפדפן ובסימניות של המשתמשים.

## קבצים מומלצים להכניס כאן:

1. **favicon.ico** - אייקון מסורתי בפורמט ICO (בגדלים 16x16, 32x32, 48x48)
2. **favicon-16x16.png** - אייקון PNG בגודל 16x16 פיקסלים
3. **favicon-32x32.png** - אייקון PNG בגודל 32x32 פיקסלים
4. **apple-touch-icon.png** - אייקון למכשירי אפל (180x180 פיקסלים)
5. **android-chrome-192x192.png** - אייקון לאנדרואיד בגודל 192x192 פיקסלים
6. **android-chrome-512x512.png** - אייקון לאנדרואיד בגודל 512x512 פיקסלים

## שימוש:

כדי לשלב את האייקונים באתר, יש להוסיף את הקוד הבא ל`<head>` של קובץ ה-HTML:

```html
<link rel="apple-touch-icon" sizes="180x180" href="img/logo/favicon/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="32x32" href="img/logo/favicon/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="img/logo/favicon/favicon-16x16.png">
<link rel="manifest" href="img/logo/favicon/site.webmanifest">
<link rel="shortcut icon" href="img/logo/favicon/favicon.ico">
```

## טיפ ליצירת Favicon:
ניתן להשתמש בכלים אונליין כמו [Favicon Generator](https://realfavicongenerator.net/) ליצירת כל הקבצים הנדרשים מתמונה אחת של הלוגו. 