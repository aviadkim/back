import axios from 'axios';

// קביעת כתובת בסיסית לשרת ה-API
const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// יצירת מופע axios עם הגדרות ברירת מחדל
const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 שניות מקסימום לבקשה
});

// הוספת interceptor לבקשות יוצאות
api.interceptors.request.use(
  (config) => {
    // הוספת טוקן אימות אם קיים
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// הוספת interceptor לתשובות נכנסות
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // טיפול בשגיאות ספציפיות
    if (error.response) {
      // השרת הגיב עם קוד שגיאה
      const { status } = error.response;
      
      // במקרה של שגיאת אימות, ניתוב חזרה לדף הכניסה
      if (status === 401 || status === 403) {
        // ניקוי מידע מקומי
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
        
        // אם יש צורך בניתוב לדף לוגין, יש להוסיף כאן
        // window.location = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// מודול עם כל הפונקציות לניתוח PDF
const pdfAnalysisApi = {
  // ניתוח PDF
  analyzePdf: (file, pages) => {
    const formData = new FormData();
    formData.append('file', file);
    
    if (pages) {
      formData.append('pages', pages);
    }
    
    return api.post('/pdf/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // חילוץ טקסט מ-PDF
  extractText: (file, pages) => {
    const formData = new FormData();
    formData.append('file', file);
    
    if (pages) {
      formData.append('pages', pages);
    }
    
    return api.post('/pdf/extract-text', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // חילוץ טבלאות מ-PDF
  extractTables: (file, pages) => {
    const formData = new FormData();
    formData.append('file', file);
    
    if (pages) {
      formData.append('pages', pages);
    }
    
    return api.post('/pdf/extract-tables', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // ניתוח השוואתי בין גרסאות
  compareBenchmark: (file, pages, useNewVersion = true) => {
    const formData = new FormData();
    formData.append('file', file);
    
    if (pages) {
      formData.append('pages', pages);
    }
    
    formData.append('use_new_version', useNewVersion ? 'true' : 'false');
    
    return api.post('/analyze/benchmark', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

// מודול עם כל הפונקציות לניהול מסמכים
const documentsApi = {
  // קבלת רשימת כל המסמכים
  getAll: (page = 1, limit = 10) => {
    return api.get('/documents', { params: { page, limit } });
  },
  
  // קבלת מסמך לפי מזהה
  getById: (id) => {
    return api.get(`/documents/${id}`);
  },
  
  // קבלת מסמך לפי שם קובץ
  getByFilename: (filename) => {
    return api.get('/documents/search', { params: { filename } });
  },
  
  // העלאת מסמך חדש
  upload: (file, metadata = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    
    // הוספת מטא-דאטה אם קיים
    if (Object.keys(metadata).length > 0) {
      formData.append('metadata', JSON.stringify(metadata));
    }
    
    return api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // הורדת קובץ PDF
  download: (id) => {
    return api.get(`/documents/${id}/download`, {
      responseType: 'blob',
    });
  },
  
  // מחיקת מסמך
  delete: (id) => {
    return api.delete(`/documents/${id}`);
  },
  
  // עדכון מטא-דאטה של מסמך
  updateMetadata: (id, metadata) => {
    return api.patch(`/documents/${id}/metadata`, { metadata });
  },
};

// יצוא של כל המודולים
export default {
  // ניתוח PDF
  ...pdfAnalysisApi,
  
  // ניהול מסמכים
  documents: documentsApi,
  
  // גישה ישירה למופע axios המוגדר
  instance: api,
  
  // גישה נוחה להגדרות
  getBaseUrl: () => BASE_URL,
  
  // העלאת קובץ כללי
  uploadFile: (file, endpoint, params = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    
    Object.entries(params).forEach(([key, value]) => {
      formData.append(key, value);
    });
    
    return api.post(endpoint, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
}; 