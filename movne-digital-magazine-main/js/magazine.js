// magazine.js - קוד JavaScript למגזין דיגיטלי (גרסה סטטית)

// רשימת תוכן העמודים
const pageContents = [
  'cover', // עמוד 1 - שער
  'intro', // עמוד 2 - פתיח
  'toc', // עמוד 3 - תוכן עניינים
  'products-intro', // עמוד 4 - מבוא למוצרים מובנים
  'products-diagram', // עמוד 5 - תרשים מוצרים מובנים
  'strategy', // עמוד 6 - אסטרטגיות השקעה
  'market-analysis', // עמוד 7 - ניתוח שוק
  'autocall-product', // עמוד 8 - מוצר אוטוקול
  'product-scenarios', // עמוד 9 - תרחישי מוצר
  'success-story', // עמוד 10 - סיפורי הצלחה
  'testimonials', // עמוד 11 - המלצות
  'contact' // עמוד 12 - צור קשר
];

// האם להציג את העמודים כזוגות (כמו אלבום)
const DISPLAY_AS_ALBUM = true;

// מספר העמודים הכולל (מותאם למצב האלבום)
const TOTAL_PAGES = DISPLAY_AS_ALBUM ? Math.ceil(pageContents.length / 2) + (pageContents.length % 2 === 0 ? 0 : 0) : pageContents.length;

// העמוד הנוכחי שמוצג
let currentPage = 1;

// שמירת עמודים שכבר נטענו במטמון
const pageCache = {};

// שם קובץ צליל הפיכת דף מותאם אישית
const CUSTOM_PAGE_TURN_SOUND = 'sounds/page-flip-47177.mp3';

// אובייקט אודיו להפיכת דף - משתמש בצליל שקט כברירת מחדל
const pageTurnSound = new Audio(CUSTOM_PAGE_TURN_SOUND);
pageTurnSound.volume = 0.7; // עוצמת קול גבוהה יותר

// משתנה לציון האם להשתמש בצליל או לא
let useSoundEffect = true;

// אתחול כשהמסמך נטען
$(document).ready(function() {
  console.log("%c מגזין דיגיטלי movne", "color: #1745ff; font-size: 20px; font-weight: bold;");
  console.log("%c מתחיל באתחול המגזין (גרסה סטטית)...", "color: #333; font-size: 14px;");
  
  // בדיקה אם קובץ האודיו קיים וטעינה מקדימה שלו
  preloadPageTurnSound();
  
  // יצירת מיכל סטטי לעמודי המגזין
  setupStaticMagazine();
  
  // טעינה ישירה של עמוד הבית - טיפול במקרה החריג הראשון
  loadHomePage();
  
  // טעינה מקדימה של העמוד הבא
  if (currentPage < TOTAL_PAGES) {
    preloadPage(currentPage + 1);
  }
  
  // הצגת קישור לדף השער בפינה
  addHomeButton();
  
  // הוספת אזורי הפיכת הדף
  addPageCornerControls();
  
  // עדכן את סגנון המגזין לפורמט אלבום אם נבחר
  if (DISPLAY_AS_ALBUM) {
    setupAlbumStyle();
  }
  
  // הסתרת מסך הטעינה
  $('#loading-overlay').hide();
  
  // הוספת אירוע התאמת גודל בעת שינוי גודל החלון
  $(window).on('resize', function() {
    adjustPageHeight();
  });
  
  console.log("%c✅ אתחול הושלם בהצלחה", "color: green; font-size: 14px;");
});

// הגדרת סגנון אלבום
function setupAlbumStyle() {
  $('<style>')
    .text(`
      .album-layout {
        display: flex;
        width: 100%;
        box-shadow: none;
        background-color: transparent;
        border-radius: 0;
        overflow: hidden;
        perspective: 1200px; /* מוסיף עומק לאנימציית הפיכת דף */
        min-height: 700px;
        height: 100%;
        justify-content: space-between;
        gap: 10px;
        padding: 0;
      }
      
      .album-page {
        width: 49.5%;
        min-height: 700px;
        height: 100%;
        position: relative;
        overflow-y: auto; /* מאפשר גלילה אנכית בתוכן ארוך */
        overflow-x: hidden;
        background-color: white;
        transition: transform 0.6s ease;
        backface-visibility: hidden;
        transform-origin: center right; /* נקודת מקור לאנימציית הפיכת דף - מימין */
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.2);
        border-radius: 5px;
      }
      
      /* עמוד ראשון (ימני) */
      .right-page {
        border-left: none;
        box-shadow: 0 0 20px rgba(0,0,0,0.2);
        z-index: 1;
      }
      
      /* עמוד שני (שמאלי) */
      .left-page {
        border-right: none;
        box-shadow: 0 0 20px rgba(0,0,0,0.2);
      }
      
      /* עמוד השער מוצג לבדו מימין */
      .first-page-container {
        justify-content: flex-end;
      }
      
      .first-page-container .right-page {
        width: 100%;
        max-width: 900px;
        border-left: none;
      }
      
      .first-page-container .left-page {
        display: none;
      }
      
      /* העמוד האחרון מוצג לבדו משמאל */
      .last-page-container {
        justify-content: flex-start;
      }
      
      .last-page-container .right-page {
        display: none;
      }
      
      .last-page-container .left-page {
        width: 100%;
        max-width: 900px;
        border-right: none;
      }
      
      .album-spine {
        display: none;
      }
      
      .page-curl {
        position: absolute;
        bottom: 0;
        width: 40px;
        height: 40px;
        opacity: 0.9;
        transition: all 0.3s ease;
        z-index: 10;
        cursor: pointer;
      }
      
      .left-page .page-curl {
        right: 0;
        background: linear-gradient(135deg, transparent 65%, #f0f0f0 65%);
        border-radius: 0 0 0 5px;
        box-shadow: -2px -2px 5px rgba(0,0,0,0.1);
      }
      
      .right-page .page-curl {
        left: 0;
        background: linear-gradient(225deg, transparent 65%, #f0f0f0 65%);
        border-radius: 0 0 5px 0;
        box-shadow: 2px -2px 5px rgba(0,0,0,0.1);
      }
      
      /* הנפשת הפיכת דף */
      .page-flip-right {
        animation: flipPageRight 0.6s ease-out forwards;
      }
      
      .page-flip-left {
        animation: flipPageLeft 0.6s ease-out forwards;
      }
      
      @keyframes flipPageRight {
        0% { transform: rotateY(0); z-index: 10; }
        50% { transform: rotateY(-90deg); z-index: 10; }
        51% { transform: rotateY(-90deg); z-index: 5; }
        100% { transform: rotateY(-180deg); z-index: 5; }
      }
      
      @keyframes flipPageLeft {
        0% { transform: rotateY(0); z-index: 5; }
        50% { transform: rotateY(90deg); z-index: 5; }
        51% { transform: rotateY(90deg); z-index: 10; }
        100% { transform: rotateY(180deg); z-index: 10; }
      }
    `)
    .appendTo('head');
    
  console.log("הוחל סגנון אלבום משופר - תמיכה בקריאה מימין לשמאל");
}

// טעינה מקדימה של צליל הפיכת הדף - גרסה משופרת
function preloadPageTurnSound() {
  console.log("מנסה לטעון את קובץ הצליל המותאם אישית");
  
  // מנסה לטעון את הצליל המותאם אישית
  try {
    // מגדיר את מקור הצליל
    pageTurnSound.src = CUSTOM_PAGE_TURN_SOUND;
    
    // מגדיר עוצמת שמע מתאימה
    pageTurnSound.volume = 0.7;
    
    // מגדיר טעינה אוטומטית
    pageTurnSound.preload = 'auto';
    
    // אירוע כאשר הצליל מוכן לניגון
    pageTurnSound.oncanplaythrough = function() {
      console.log("הצליל המותאם אישית נטען בהצלחה");
      useSoundEffect = true;
      pageTurnSound.oncanplaythrough = null; // מנקה את האירוע
    };
    
    // אירוע במקרה של שגיאה בטעינת הצליל
    pageTurnSound.onerror = function(e) {
      console.warn("שגיאה בטעינת הצליל המותאם אישית:", e);
      
      // ננסה לטעון צליל ברירת מחדל
      pageTurnSound.src = 'sounds/page-flip.mp3';
      pageTurnSound.load();
      
      pageTurnSound.oncanplaythrough = function() {
        console.log("נטען צליל ברירת מחדל");
        useSoundEffect = true;
        pageTurnSound.oncanplaythrough = null;
      };
      
      pageTurnSound.onerror = function() {
        console.warn("לא ניתן לטעון גם את צליל ברירת המחדל. מבטל את אפקט הצליל.");
        useSoundEffect = false;
      };
    };
    
    // טוען את הצליל
    pageTurnSound.load();
    
    // מנסה לנגן צליל קצר כדי לאתחל את מערכת האודיו
    document.addEventListener('click', function initAudio() {
      pageTurnSound.play().then(() => {
        pageTurnSound.pause();
        pageTurnSound.currentTime = 0;
        console.log("מערכת האודיו אותחלה בהצלחה");
      }).catch(e => {
        console.warn("לא ניתן לאתחל את מערכת האודיו:", e);
      });
      document.removeEventListener('click', initAudio);
    }, { once: true });
    
  } catch (e) {
    console.error("שגיאה בהגדרת צליל הפיכת דף:", e);
    useSoundEffect = false; // מבטל את השימוש בצליל
  }
}

// ניגון צליל הפיכת דף - גרסה משופרת
function playPageTurnSound() {
  // אם אפקט הצליל מבוטל, לא מנגן כלום
  if (!useSoundEffect) {
    return;
  }
  
  try {
    // ריסט של האודיו ונגינה מחדש
    if (pageTurnSound.readyState >= 2) {  // לפחות HAVE_CURRENT_DATA
      // וידוא שהעוצמה מוגדרת נכון
      pageTurnSound.volume = 0.7;
      
      // ריסט וניגון
      pageTurnSound.currentTime = 0;
      
      // ניגון הצליל עם טיפול בשגיאות
      const playPromise = pageTurnSound.play();
      
      if (playPromise !== undefined) {
        playPromise.then(() => {
          console.log("מנגן צליל הפיכת דף");
        }).catch(error => {
          console.warn("לא ניתן לנגן אפקט קולי:", error);
          
          // ניסיון להפעיל את הניגון לאחר אינטראקציית משתמש
          $(document).one('click', function() {
            pageTurnSound.play().catch(e => console.warn("ניסיון שני נכשל:", e));
          });
        });
      }
    } else {
      console.warn("צליל עדיין לא מוכן לניגון");
      
      // ננסה לטעון שוב את הצליל
      pageTurnSound.load();
      
      // ננסה לנגן מיד אחרי הטעינה
      pageTurnSound.oncanplaythrough = function() {
        pageTurnSound.play().catch(e => console.warn("שגיאת ניגון אחרי טעינה:", e));
        pageTurnSound.oncanplaythrough = null; // מנקה את האירוע
      };
    }
  } catch (e) {
    console.warn("שגיאה בהפעלת אפקט קולי:", e);
    useSoundEffect = false; // מבטל את השימוש בצליל במקרה של שגיאה
  }
}

// הוספת אזורי הפיכת דף בפינות
function addPageCornerControls() {
  // מוסיף את אזורי הפינות כאלמנטים שקופים בפינות העמוד
  $('#magazine').append(`
    <div id="right-corner" class="page-corner right-corner" title="לעמוד הקודם">
      <div class="corner-arrow right-arrow">&#10094;</div>
    </div>
    <div id="left-corner" class="page-corner left-corner" title="לעמוד הבא">
      <div class="corner-arrow left-arrow">&#10095;</div>
    </div>
  `);
  
  // הוספת אירועים לפינות
  $('#left-corner').off('click').on('click', function() {
    if (currentPage < TOTAL_PAGES) {
      playPageTurnSound();
      applyAlbumPageFlip('next');
    }
  });
  
  $('#right-corner').off('click').on('click', function() {
    if (currentPage > 1) {
      playPageTurnSound();
      applyAlbumPageFlip('prev');
    }
  });
}

// פונקציה חדשה להצגת אפקט הפיכת דף ריאליסטי במצב אלבום
function applyRealisticPageFlip(direction) {
  // מוחק את אנימציית הפיכת הדף הקיימת אם יש
  $('#page-flip-effect').remove();
  
  if (DISPLAY_AS_ALBUM) {
    // אפקט הפיכת דף מיוחד למצב אלבום
    applyAlbumPageFlip(direction);
    return;
  }
  
  // אפקט הפיכת דף רגיל לעמוד בודד
  // הגדרת הכיוון של האנימציה
  const transformOrigin = direction === 'right' ? 'left center' : 'right center';
  const startPos = direction === 'right' ? 'right' : 'left';
  const shadow = direction === 'right' ? 'drop-shadow(-10px 0 20px rgba(0,0,0,0.3))' : 'drop-shadow(10px 0 20px rgba(0,0,0,0.3))';
  
  // יוצר העתק של הדף הנוכחי
  const pageClone = $('#magazine').html();
  const flipElement = $('<div id="page-flip-effect"></div>').html(pageClone);
  
  // מוסיף סגנון ייחודי לאלמנט הפיכת הדף
  flipElement.css({
    position: 'absolute',
    top: $('#magazine').position().top,
    left: $('#magazine').position().left,
    width: $('#magazine').width(),
    height: $('#magazine').height(),
    backgroundColor: 'white',
    transformOrigin: transformOrigin,
    zIndex: 9999,
    boxShadow: '0 0 20px rgba(0,0,0,0.3)',
    overflow: 'hidden'
  });
  
  // הסתרת התוכן המקורי
  $('#magazine').css('opacity', '0');
  
  // הוספת אלמנט האנימציה
  $('body').append(flipElement);
  
  // יצירת אנימציה
  flipElement.animate({
    transform: direction === 'right' ? 
      ['rotateY(0deg)', 'rotateY(15deg)', 'rotateY(90deg)', 'rotateY(120deg)', 'rotateY(180deg)'] : 
      ['rotateY(0deg)', 'rotateY(-15deg)', 'rotateY(-90deg)', 'rotateY(-120deg)', 'rotateY(-180deg)'],
    opacity: [1, 1, 0.8, 0.5, 0],
    filter: ['none', shadow, shadow, shadow, 'none']
  }, {
    duration: 600,
    easing: 'easeOutQuad',
    step: function(now, fx) {
      // אפקט נוסף במהלך האנימציה
      if (fx.prop === 'transform') {
        const percent = fx.pos * 100;
        if (percent > 90) {
          flipElement.css('filter', 'none');
        }
      }
    },
    complete: function() {
      // לאחר סיום האנימציה - הסרת אלמנט ההפיכה והחזרת התוכן המקורי
      flipElement.remove();
      $('#magazine').css('opacity', '1');
    }
  });
}

// פונקציה משופרת לאפקט הפיכת דף במצב אלבום
function applyAlbumPageFlip(direction) {
  // משתנים לאפקטים חזותיים
  const flipDuration = 600; // משך האנימציה במילישניות
  const flipDelay = 50;     // השהייה קצרה לסנכרון האנימציה עם הקול
  
  // הפעלת צליל הפיכת דף
  playPageTurnSound();
  
  // מעטפת האנימציה - מחכה שהצליל יתחיל לפני האנימציה
  setTimeout(() => {
    if (direction === 'next') {
      // מעבר לעמוד הבא - הדף השמאלי מתהפך ימינה
      
      // יוצר העתק של העמוד השמאלי הנוכחי לאנימציית הפיכה
      const leftPage = $('.left-page').clone();
      const cloneContainer = $('<div class="page-flip-container"></div>');
      
      // מיקום ועיצוב ההעתק
      cloneContainer.css({
        position: 'absolute',
        top: $('.left-page').offset().top - $('#magazine').offset().top,
        left: $('.left-page').offset().left - $('#magazine').offset().left,
        width: $('.left-page').width(),
        height: $('.left-page').height(),
        zIndex: 100,
        overflow: 'hidden'
      });
      
      // הוספת העתק לדף הנוכחי
      cloneContainer.append(leftPage);
      $('#magazine').append(cloneContainer);
      
      // הסתרת העמוד המקורי
      $('.left-page').css('visibility', 'hidden');
      
      // הפעלת האנימציה
      leftPage.addClass('page-flip-left');
      
      // עדכון אפקטי צל במהלך האנימציה
      leftPage.css('box-shadow', '5px 0 15px rgba(0,0,0,0.3)');
      
      // טעינת העמוד הבא אחרי האנימציה
      setTimeout(() => {
        loadPage(currentPage + 1);
        cloneContainer.remove();
      }, flipDuration);
      
    } else {
      // מעבר לעמוד הקודם - הדף הימני מתהפך שמאלה
      
      // יוצר העתק של העמוד הימני הנוכחי לאנימציית הפיכה
      const rightPage = $('.right-page').clone();
      const cloneContainer = $('<div class="page-flip-container"></div>');
      
      // מיקום ועיצוב ההעתק
      cloneContainer.css({
        position: 'absolute',
        top: $('.right-page').offset().top - $('#magazine').offset().top,
        left: $('.right-page').offset().left - $('#magazine').offset().left,
        width: $('.right-page').width(),
        height: $('.right-page').height(),
        zIndex: 100,
        overflow: 'hidden'
      });
      
      // הוספת העתק לדף הנוכחי
      cloneContainer.append(rightPage);
      $('#magazine').append(cloneContainer);
      
      // הסתרת העמוד המקורי
      $('.right-page').css('visibility', 'hidden');
      
      // הפעלת האנימציה
      rightPage.addClass('page-flip-right');
      
      // עדכון אפקטי צל במהלך האנימציה
      rightPage.css('box-shadow', '-5px 0 15px rgba(0,0,0,0.3)');
      
      // טעינת העמוד הקודם אחרי האנימציה
      setTimeout(() => {
        loadPage(currentPage - 1);
        cloneContainer.remove();
      }, flipDuration);
    }
  }, flipDelay);
}

// הגדרת המגזין הסטטי 
function setupStaticMagazine() {
  // מחיקת כל התוכן הקיים במגזין
  $('#magazine').empty();
  
  // יצירת הקונטיינר החדש
  $('#magazine').addClass('static-magazine');
  
  // טעינת העמוד הראשון
  loadPage(currentPage);
  
  // הגדרת המספר הכולל של העמודים
  $('#total-pages').text(TOTAL_PAGES);
  
  // הגדרת אירועי הלחצנים
  setupEventListeners();
}

// הוספת לוגו פינתי לכל עמוד
function addCornerLogo() {
  if (DISPLAY_AS_ALBUM) {
    // במצב אלבום, מוסיף לוגו לכל עמוד בנפרד
    $('.album-page .page-content').each(function(index) {
      // מוסיף לוגו רק אם זה לא עמוד השער
      const isFirstPageOfAlbum = index === 0 && currentPage === 1;
      if (!isFirstPageOfAlbum && $(this).find('.corner-logo').length === 0) {
        $(this).prepend(`
          <div class="corner-logo">
            <img src="img/logo/movne_profile_800px-03.jpg" alt="מובנה" class="small-corner-logo">
          </div>
        `);
      }
    });
  } else {
    // במצב רגיל - בודק אם הלוגו כבר קיים בעמוד
    if ($('#magazine .corner-logo').length === 0 && currentPage !== 1) {
      $('#magazine .page-content').prepend(`
        <div class="corner-logo">
          <img src="img/logo/movne_profile_800px-03.jpg" alt="מובנה" class="small-corner-logo">
        </div>
      `);
    }
  }
}

// טעינת עמוד ספציפי
function loadPage(pageNumber) {
  if (pageNumber < 1 || pageNumber > TOTAL_PAGES) {
    return;
  }
  
  // עדכון העמוד הנוכחי
  currentPage = pageNumber;
  $('#current-page').text(currentPage);
  
  if (DISPLAY_AS_ALBUM) {
    // במצב אלבום, טוען שני עמודים זה לצד זה
    loadAlbumPages(pageNumber);
  } else {
    // במצב רגיל, טוען עמוד אחד
    loadSinglePage(pageNumber);
  }
  
  // טעינה מקדימה של העמודים הסמוכים (קודם ובא)
  preloadAdjacentPages(pageNumber);
}

// טעינת שני עמודים זה לצד זה (מצב אלבום)
function loadAlbumPages(pageNumber) {
  console.log(`טוען אלבום עמודים ${pageNumber}...`);
  
  // חישוב האינדקסים של שני העמודים שיוצגו
  const leftPageIndex = (pageNumber - 1) * 2 + 1; // עמוד שמאלי (אי-זוגי)
  const rightPageIndex = (pageNumber - 1) * 2;    // עמוד ימני (זוגי)
  
  // קבלת התוכן של העמודים
  const rightPageContent = rightPageIndex < pageContents.length ? pageContents[rightPageIndex] : null;
  const leftPageContent = leftPageIndex < pageContents.length ? pageContents[leftPageIndex] : null;
  
  // יוצר את המסגרת של האלבום עם קלאס מיוחד לעמוד ראשון או אחרון
  let albumClass = 'album-layout';
  if (pageNumber === 1) {
    albumClass += ' first-page-container';
  } else if (pageNumber === TOTAL_PAGES) {
    albumClass += ' last-page-container';
  }
  
  const albumLayout = $(`<div class="${albumClass}"></div>`);
  
  // יוצר את העמוד הימני (ראשון בקריאה מימין לשמאל)
  const rightPage = $('<div class="album-page right-page"></div>');
  if (rightPageContent) {
    loadPageContent(rightPageContent, rightPage);
    // מוסיף אפקט פינת דף לעמוד הימני
    rightPage.append('<div class="page-curl right-curl"></div>');
  } else {
    rightPage.html('<div class="empty-page"><p>סוף המגזין</p></div>');
  }
  
  // יוצר את העמוד השמאלי
  const leftPage = $('<div class="album-page left-page"></div>');
  if (leftPageContent) {
    loadPageContent(leftPageContent, leftPage);
    // מוסיף אפקט פינת דף לעמוד השמאלי
    leftPage.append('<div class="page-curl left-curl"></div>');
  } else {
    leftPage.html('<div class="empty-page"><p>סוף המגזין</p></div>');
  }
  
  // שם את העמודים באלבום בסדר הנכון: ימין לשמאל
  albumLayout.append(rightPage);
  albumLayout.append(leftPage);
  
  // החלפת התוכן
  $('#magazine').html(albumLayout);
  $('#magazine').addClass('page-load-animation');
  
  // התאמת גובה הדפים לגובה המיכל
  adjustPageHeight();
  
  // הוספת סימון שהעמוד נטען
  setTimeout(function() {
    $('body').addClass('page-loaded');
    
    // הוספת אזורי פינות העמוד
    addPageCornerControls();
    
    // הוספת לוגו פינתי
    addCornerLogo();
    
    // הוספת אירועי קליק לפינות הדפים
    $('.right-curl').off('click').on('click', function() {
      if (currentPage < TOTAL_PAGES) {
        playPageTurnSound();
        applyAlbumPageFlip('next');
      }
    });
    
    $('.left-curl').off('click').on('click', function() {
      if (currentPage > 1) {
        playPageTurnSound();
        applyAlbumPageFlip('prev');
      }
    });
    
  }, 300);
}

// פונקציה חדשה להתאמת גובה הדפים
function adjustPageHeight() {
  const containerHeight = $('#magazine').height();
  const containerWidth = $('#magazine').width();
  
  // התאמת גובה הדפים
  $('.album-page').css({
    'min-height': containerHeight + 'px',
    'max-height': containerHeight + 'px'
  });
  
  // התאמת גובה התוכן
  $('.page-content').css({
    'min-height': (containerHeight - 40) + 'px',
    'max-height': (containerHeight - 40) + 'px'
  });
  
  // התאמת רוחב הדפים במצב עמוד ראשון או אחרון
  if ($('.album-layout').hasClass('first-page-container') || $('.album-layout').hasClass('last-page-container')) {
    const singlePageWidth = Math.min(900, containerWidth * 0.8);
    
    if ($('.album-layout').hasClass('first-page-container')) {
      $('.right-page').css('width', singlePageWidth + 'px');
    } else {
      $('.left-page').css('width', singlePageWidth + 'px');
    }
  }
}

// פונקציית טעינה של עמוד בודד לתוך מיכל
function loadPageContent(pageContent, container) {
  const pageUrl = `pages/${pageContent}.html`;
  
  // בדיקה אם העמוד קיים במטמון
  if (pageCache[pageContent]) {
    container.html(pageCache[pageContent]);
    return;
  }
  
  // טעינת העמוד
  $.ajax({
    url: pageUrl,
    type: 'GET',
    dataType: 'html',
    cache: true,
    async: false, // טעינה סינכרונית לצורך האלבום
    success: function(data) {
      // תיקון נתיבים יחסיים
      let fixedData = data
        .replace(/src="img\//g, 'src="img/')
        .replace(/src="\.\.\/img\//g, 'src="img/')
        .replace(/href="img\//g, 'href="img/')
        .replace(/href="\.\.\/img\//g, 'href="img/');
      
      // שמירת העמוד במטמון
      pageCache[pageContent] = fixedData;
      container.html(fixedData);
    },
    error: function(xhr, status, error) {
      container.html(`
        <div class="page-content">
          <div class="page-header">
            <h1>שגיאה</h1>
          </div>
          <div class="page-body">
            <p>שגיאה בטעינת התוכן. ${status}: ${error}</p>
            <p>נתיב: ${pageUrl}</p>
          </div>
        </div>
      `);
    }
  });
}

// פונקציה לטעינת עמוד בודד (מצב רגיל, לא אלבום)
function loadSinglePage(pageNumber) {
  // קבלת התוכן של העמוד
  const pageContent = pageContents[pageNumber - 1];
  const pageUrl = `pages/${pageContent}.html`;
  
  console.log(`טוען את העמוד ${pageNumber}: ${pageUrl}`);
  
  // עדכון העמוד הנוכחי
  currentPage = pageNumber;
  $('#current-page').text(currentPage);
  
  // בדיקה אם העמוד קיים במטמון
  if (pageCache[pageContent]) {
    $('#magazine').html(pageCache[pageContent]);
    $('#magazine').addClass('page-load-animation');
    
    // הוספת סימון שהעמוד נטען
    setTimeout(function() {
      $('body').addClass('page-loaded');
      // הוספת אזורי פינות העמוד לאחר טעינה מהמטמון
      addPageCornerControls();
      // הוספת לוגו פינתי אם צריך (מלבד עמוד שער)
      if (pageNumber !== 1) {
        addCornerLogo();
      }
    }, 500);
    
    console.log(`עמוד ${pageNumber} נטען מהמטמון`);
    
    // טעינה מקדימה של העמודים הסמוכים (קודם ובא)
    preloadAdjacentPages(pageNumber);
    return;
  }
  
  // טעינת העמוד
  $.ajax({
    url: pageUrl,
    type: 'GET',
    dataType: 'html',
    cache: true,
    crossDomain: false,
    timeout: 10000,  // 10 seconds timeout
    beforeSend: function() {
      console.log(`מתחיל לטעון את ${pageUrl}...`);
    },
    success: function(data) {
      // שמירת העמוד במטמון
      pageCache[pageContent] = data;
      
      console.log(`נטען בהצלחה: ${pageUrl}, גודל התוכן: ${data.length}`);
      
      // עדכון נתיבים יחסיים
      let fixedData = data
        .replace(/src="img\//g, 'src="img/')
        .replace(/src="\.\.\/img\//g, 'src="img/')
        .replace(/href="img\//g, 'href="img/')
        .replace(/href="\.\.\/img\//g, 'href="img/');
      
      $('#magazine').html(fixedData);
      $('#magazine').addClass('page-load-animation');
      
      // הוספת סימון שהעמוד נטען
      setTimeout(function() {
        $('body').addClass('page-loaded');
        // הוספת אזורי פינות העמוד
        addPageCornerControls();
        // הוספת לוגו פינתי אם צריך (מלבד עמוד שער)
        if (pageNumber !== 1) {
          addCornerLogo();
        }
      }, 500);
      
      console.log(`עמוד ${pageNumber} נטען בהצלחה`);
      
      // טעינה מקדימה של העמודים הסמוכים (קודם ובא)
      preloadAdjacentPages(pageNumber);
    },
    error: function(xhr, status, error) {
      console.error(`שגיאה בטעינת עמוד ${pageNumber}: ${status} - ${error}`);
      console.error(`URL: ${pageUrl}`);
      
      $('#magazine').html(`
        <div class="page-content">
          <div class="page-header">
            <h1>עמוד ${pageNumber}</h1>
          </div>
          <div class="page-body">
            <p>שגיאה בטעינת התוכן. ${status}: ${error}</p>
            <p>נתיב: ${pageUrl}</p>
          </div>
          <div class="page-footer">
            <div class="page-number">${pageNumber}</div>
          </div>
        </div>
      `);
      
      // הוספת אזורי פינות גם במקרה של שגיאה
      addPageCornerControls();
    }
  });
}

// טעינה מקדימה של העמודים הסמוכים (קודם ובא)
function preloadAdjacentPages(currentPageNum) {
  // טעינה מקדימה של העמוד הבא
  if (currentPageNum < TOTAL_PAGES) {
    preloadPage(currentPageNum + 1);
  }
  
  // טעינה מקדימה של העמוד הקודם
  if (currentPageNum > 1) {
    preloadPage(currentPageNum - 1);
  }
}

// פונקציית טעינה מקדימה
function preloadPage(pageNumber) {
  if (DISPLAY_AS_ALBUM) {
    // במצב אלבום טוען שני עמודים
    const leftPageIndex = (pageNumber - 1) * 2;
    const rightPageIndex = leftPageIndex + 1;
    
    // טעינת העמוד השמאלי
    if (leftPageIndex < pageContents.length) {
      const leftPageContent = pageContents[leftPageIndex];
      if (!pageCache[leftPageContent]) {
        preloadSinglePage(leftPageContent);
      }
    }
    
    // טעינת העמוד הימני
    if (rightPageIndex < pageContents.length) {
      const rightPageContent = pageContents[rightPageIndex];
      if (!pageCache[rightPageContent]) {
        preloadSinglePage(rightPageContent);
      }
    }
  } else {
    // במצב רגיל טוען עמוד אחד
    const pageContent = pageContents[pageNumber - 1];
    if (!pageCache[pageContent]) {
      preloadSinglePage(pageContent);
    }
  }
}

// פונקציה לטעינה מקדימה של עמוד יחיד
function preloadSinglePage(pageContent) {
  const pageUrl = `pages/${pageContent}.html`;
  
  console.log(`טעינה מקדימה של עמוד ${pageContent}: ${pageUrl}`);
  
  $.ajax({
    url: pageUrl,
    type: 'GET',
    success: function(data) {
      // עדכון נתיבים יחסיים
      let fixedData = data
        .replace(/src="img\//g, 'src="img/')
        .replace(/src="\.\.\/img\//g, 'src="img/')
        .replace(/href="img\//g, 'href="img/')
        .replace(/href="\.\.\/img\//g, 'href="img/');
      
      // שמירת העמוד במטמון
      pageCache[pageContent] = fixedData;
      console.log(`עמוד ${pageContent} נטען מקדימה בהצלחה`);
    },
    error: function() {
      console.error(`שגיאה בטעינה מקדימה של עמוד ${pageContent}`);
    }
  });
}

// הגדרת אירועי הלחצנים
function setupEventListeners() {
  // לחצן הבא (חץ שמאלה בעברית)
  $('#next-btn').on('click', function() {
    if (currentPage < TOTAL_PAGES) {
      playPageTurnSound();
      applyAlbumPageFlip('next');
    }
  });
  
  // לחצן הקודם (חץ ימינה בעברית)
  $('#prev-btn').on('click', function() {
    if (currentPage > 1) {
      playPageTurnSound();
      applyAlbumPageFlip('prev');
    }
  });
  
  // מקשי מקלדת - מותאם לכיוון קריאה בעברית (מימין לשמאל)
  $(document).on('keydown', function(e) {
    // חץ שמאלה - עמוד הבא בגלל כיוון קריאה מימין לשמאל
    if (e.keyCode === 37) {
      if (currentPage < TOTAL_PAGES) {
        playPageTurnSound();
        applyAlbumPageFlip('next');
      }
    }
    // חץ ימינה - עמוד הקודם בגלל כיוון קריאה מימין לשמאל
    else if (e.keyCode === 39) {
      if (currentPage > 1) {
        playPageTurnSound();
        applyAlbumPageFlip('prev');
      }
    }
  });
  
  // לחצני זום
  $('#zoom-in-btn').on('click', function() {
    zoom(0.1);
  });
  
  $('#zoom-out-btn').on('click', function() {
    zoom(-0.1);
  });
  
  // לחצן מסך מלא
  $('#fullscreen-btn').on('click', function() {
    toggleFullScreen();
  });
  
  // לחצן הפעלה/כיבוי צליל
  $('#sound-toggle-btn').on('click', function() {
    toggleSound();
  });
  
  // אירוע פתיחת המגזין בפעם הראשונה
  setTimeout(function() {
    // הוספת אנימציית פתיחה למגזין
    $('#magazine').addClass('magazine-opening');
    
    // ניגון צליל פתיחה
    playPageTurnSound();
  }, 500);
}

// פונקציית זום פשוטה
let zoomLevel = 1;
function zoom(increment) {
  zoomLevel = Math.max(0.5, Math.min(2, zoomLevel + increment));
  $('.static-magazine').css('transform', `scale(${zoomLevel})`);
}

// מעבר למסך מלא
function toggleFullScreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(err => {
      console.error(`שגיאה במעבר למסך מלא: ${err.message}`);
    });
  } else {
    document.exitFullscreen();
  }
}

// טעינת עמוד הבית
function loadHomePage() {
  console.log("טוען את עמוד הבית...");
  loadPage(1);
}

// הוספת כפתור בית
function addHomeButton() {
  if ($('#home-btn').length === 0) {
    const homeButton = $('<button id="home-btn" class="control-btn home-btn" title="לעמוד הראשון"><i class="fas fa-home"></i></button>');
    $('.controls').prepend(homeButton);
    
    homeButton.on('click', function() {
      if (currentPage !== 1) {
        playPageTurnSound();
        applyRealisticPageFlip('left');
        setTimeout(() => {
          loadPage(1);
        }, 500);
      }
    });
  }
}

// יצירת תיקיית סאונד ב-run time אם היא לא קיימת
function createSoundFolder() {
  const soundDir = 'sounds';
  $.ajax({
    url: soundDir,
    type: 'HEAD',
    error: function() {
      console.log("יוצר תיקיית סאונד...");
      // כאן היינו רוצים קוד שיוצר תיקייה, אבל זה לא אפשרי בדפדן מסיבות אבטחה
    },
    success: function() {
      console.log("תיקיית סאונד קיימת");
    }
  });
}

// פונקציה להפעלה/כיבוי של הצליל
function toggleSound() {
  useSoundEffect = !useSoundEffect;
  
  // עדכון האייקון
  if (useSoundEffect) {
    $('#sound-toggle-btn i').removeClass('fa-volume-mute').addClass('fa-volume-up');
    $('#sound-toggle-btn').attr('title', 'כבה צליל');
    console.log("צליל הפיכת דף מופעל");
  } else {
    $('#sound-toggle-btn i').removeClass('fa-volume-up').addClass('fa-volume-mute');
    $('#sound-toggle-btn').attr('title', 'הפעל צליל');
    console.log("צליל הפיכת דף מושתק");
  }
}