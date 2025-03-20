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
  analyzePdf: async (file, page) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('page_num', page.toString());
    formData.append('extract_tables', 'true');
    formData.append('extract_financial_data', 'true');
    formData.append('parse_bonds', 'true');
    formData.append('use_new_version', 'true');
    
    const response = await api.post('/pdf/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    // עיבוד נוסף של התוצאות - ארגון הנתונים בטבלה
    const result = response.data;
    if (result.pages && result.pages[page]) {
      const pageData = result.pages[page];
      
      // ארגון נתוני אגרות החוב בטבלה
      if (pageData.text) {
        const bonds = [];
        const lines = pageData.text.split('\n');
        
        let currentBond = {};
        for (const line of lines) {
          // חיפוש מידע על אגרות חוב
          if (line.includes('ISIN:')) {
            if (Object.keys(currentBond).length > 0) {
              bonds.push(currentBond);
            }
            currentBond = {
              isin: line.match(/ISIN: ([\w\d]+)/)?.[1],
              valorn: line.match(/Valorn\.: (\d+)/)?.[1]
            };
          }
          
          // חיפוש פרטים נוספים
          if (currentBond.isin) {
            if (line.includes('Maturity:')) {
              currentBond.maturity = line.match(/Maturity: ([\d\.]+)/)?.[1];
            }
            if (line.includes('Coupon:')) {
              currentBond.coupon = line.match(/Coupon: ([\d\.]+)/)?.[1];
            }
            if (line.includes('USD')) {
              const amounts = line.match(/USD ([\d,\']+)/);
              if (amounts) {
                currentBond.amount = amounts[1];
              }
            }
          }
        }
        
        // הוספת הטבלה המאורגנת לתוצאות
        if (bonds.length > 0) {
          pageData.organized_bonds = bonds;
        }
      }
    }
    
    return result;
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
  upload: async (file, metadata = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    
    if (Object.keys(metadata).length > 0) {
      formData.append('metadata', JSON.stringify(metadata));
    }
    
    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  // הורדת קובץ PDF
  download: async (id) => {
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

// מודול לניהול תבניות חכמות
const templatesApi = {
  // סריקת כותרות מהמסמך
  scanHeaders: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('scan_headers', 'true');
    
    const response = await api.post('/pdf/scan-headers', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // שמירת תבנית חדשה
  saveTemplate: async (template) => {
    return api.post('/templates', template);
  },

  // קבלת כל התבניות השמורות
  getTemplates: async () => {
    return api.get('/templates');
  },

  // הפעלת תבנית על מסמך
  applyTemplate: async (file, templateId) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('template_id', templateId);
    
    const response = await api.post('/pdf/apply-template', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // עדכון תבנית קיימת
  updateTemplate: async (templateId, template) => {
    return api.put(`/templates/${templateId}`, template);
  },

  // מחיקת תבנית
  deleteTemplate: async (templateId) => {
    return api.delete(`/templates/${templateId}`);
  }
};

// מודול לניהול הצ'אט החכם
export const chatApi = {
  // שליחת הודעה לבוט
  sendMessage: async (message, context) => {
    const formData = new FormData();
    formData.append('message', message);
    formData.append('context', context);
    const response = await api.post('/chat/message', formData);
    return response.data;
  },

  // קבלת היסטוריית שיחה
  getHistory: async () => {
    const response = await api.get('/chat/history');
    return response.data;
  },

  // מחיקת היסטוריית שיחה
  clearHistory: async () => {
    const response = await api.delete('/chat/history');
    return response.data;
  }
};

// יצוא של כל המודולים
export default {
  // ניתוח PDF
  ...pdfAnalysisApi,
  
  // ניהול מסמכים
  documents: documentsApi,
  
  // ניהול תבניות
  templates: templatesApi,
  
  // מודול הצ'אט
  chat: chatApi,
  
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

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.message || 'שגיאה בהעלאת המסמך');
  }
};

export const analyzePage = async (documentId, pageNumber) => {
  try {
    const response = await api.post(`/documents/${documentId}/analyze`, {
      pageNumber
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.message || 'שגיאה בניתוח העמוד');
  }
}; 