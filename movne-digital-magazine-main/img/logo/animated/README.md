# לוגואים מונפשים של movne

תיקייה זו מיועדת לגרסאות מונפשות של הלוגו שיכולות להוסיף חיים ותנועה למגזין הדיגיטלי.

## קבצים מומלצים להכניס כאן:

1. **movne-logo-animated.gif** - גרסה מונפשת של הלוגו בפורמט GIF
2. **movne-logo-animated.svg** - גרסה מונפשת של הלוגו בפורמט SVG (מומלץ לביצועים טובים יותר)
3. **movne-logo-loading.gif** - גרסה מונפשת קטנה לשימוש כאנימציית טעינה
4. **movne-logo-pulse.gif** - גרסה מונפשת של הלוגו עם אפקט פעימה

## כיצד לשלב באתר:

לשילוב לוגו מונפש בדף הראשי בזמן טעינה:

```html
<div class="loading-container">
  <img src="img/logo/animated/movne-logo-loading.gif" alt="טוען..." class="loading-logo">
</div>
```

לשילוב לוגו SVG מונפש בעמוד הבית:

```html
<object type="image/svg+xml" data="img/logo/animated/movne-logo-animated.svg" class="animated-logo">
  <!-- גיבוי במקרה שהדפדפן לא תומך ב-SVG -->
  <img src="img/logo/movne-logo-dark.png" alt="movne" class="logo-fallback">
</object>
```

## טיפ:
אנימציות קלות ומעודנות עובדות הכי טוב - למשל הבהוב עדין, פעימה, או תנועה קלה של אלמנטים בלוגו. 