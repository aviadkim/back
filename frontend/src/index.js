import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { RTL } from './rtlConfig';

// שורש האפליקציה
const root = ReactDOM.createRoot(document.getElementById('root'));

// עטיפת האפליקציה בקומפוננט RTL לתמיכה מלאה בעברית
root.render(
  <React.StrictMode>
    <RTL>
      <App />
    </RTL>
  </React.StrictMode>
); 