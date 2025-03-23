document.addEventListener('DOMContentLoaded', function() {
    // Element references
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const languageSelect = document.getElementById('language-select');
    const uploadStatus = document.getElementById('upload-status');
    const documentsList = document.getElementById('documents-list');
    
    // Base URL for API
    const apiBaseUrl = window.location.origin;
    
    // Load documents list
    loadDocuments();
    
    // Setup event listeners
    uploadForm.addEventListener('submit', handleFileUpload);
    
    // Function to handle file upload
    async function handleFileUpload(event) {
        event.preventDefault();
        
        // Check if file is selected
        if (!fileInput.files || fileInput.files.length === 0) {
            showUploadStatus('נא לבחור קובץ להעלאה', 'error');
            return;
        }
        
        const file = fileInput.files[0];
        const language = languageSelect.value;
        
        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        formData.append('language', language);
        
        showUploadStatus('מעלה קובץ...', 'info');
        
        try {
            const response = await fetch(`${apiBaseUrl}/api/upload`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showUploadStatus('הקובץ הועלה בהצלחה!', 'success');
                loadDocuments(); // Refresh documents list
                fileInput.value = ''; // Clear file input
            } else {
                showUploadStatus(`שגיאה: ${data.error || 'שגיאה לא ידועה'}`, 'error');
            }
        } catch (error) {
            showUploadStatus(`שגיאה בהעלאה: ${error.message}`, 'error');
        }
    }
    
    // Function to show upload status
    function showUploadStatus(message, type) {
        uploadStatus.textContent = message;
        uploadStatus.className = 'mt-4 p-2 rounded';
        
        // Add status type styling
        if (type === 'error') {
            uploadStatus.classList.add('bg-red-100', 'text-red-800');
        } else if (type === 'success') {
            uploadStatus.classList.add('bg-green-100', 'text-green-800');
        } else {
            uploadStatus.classList.add('bg-blue-100', 'text-blue-800');
        }
        
        uploadStatus.classList.remove('hidden');
        
        // Auto hide after 5 seconds
        setTimeout(() => {
            uploadStatus.classList.add('hidden');
        }, 5000);
    }
    
    // Function to load documents list
    async function loadDocuments() {
        try {
            const response = await fetch(`${apiBaseUrl}/api/documents?language=${languageSelect.value}`);
            const data = await response.json();
            
            if (response.ok && data.documents) {
                displayDocuments(data.documents);
            } else {
                documentsList.innerHTML = '<p class="text-red-600">שגיאה בטעינת מסמכים</p>';
            }
        } catch (error) {
            documentsList.innerHTML = `<p class="text-red-600">שגיאה: ${error.message}</p>`;
        }
    }
    
    // Function to display documents
    function displayDocuments(documents) {
        if (documents.length === 0) {
            documentsList.innerHTML = '<p>אין מסמכים להצגה</p>';
            return;
        }
        
        let html = '<ul class="divide-y divide-gray-200">';
        
        documents.forEach(doc => {
            let documentType = '';
            let detailsText = '';
            
            if (doc.type === 'PDF') {
                documentType = 'PDF';
                detailsText = `טבלאות: ${doc.table_count || 0}, אורך טקסט: ${doc.text_length || 0} תווים`;
            } else if (doc.type === 'Excel') {
                documentType = 'Excel';
                detailsText = `גיליונות: ${doc.sheet_count || 0}`;
            } else if (doc.type === 'CSV') {
                documentType = 'CSV';
                detailsText = `שורות: ${doc.row_count || 0}`;
            } else {
                documentType = 'מסמך';
                detailsText = 'אין פרטים נוספים';
            }
            
            const docId = doc.document_id;
            const fileName = docId.split('/').pop();
            
            html += `
                <li class="py-4">
                    <div class="flex justify-between">
                        <div>
                            <h3 class="font-medium">${fileName}</h3>
                            <p class="text-sm text-gray-600">${documentType} - ${detailsText}</p>
                            <p class="text-xs text-gray-500">תאריך עיבוד: ${formatDate(doc.processing_date)}</p>
                        </div>
                        <div>
                            <button class="text-blue-600 hover:text-blue-800 mr-2" 
                                    onclick="viewDocument('${docId}')">צפייה</button>
                            <button class="text-red-600 hover:text-red-800" 
                                    onclick="deleteDocument('${docId}')">מחיקה</button>
                        </div>
                    </div>
                </li>
            `;
        });
        
        html += '</ul>';
        documentsList.innerHTML = html;
    }
    
    // Format date helper
    function formatDate(dateString) {
        if (!dateString) return 'לא ידוע';
        
        try {
            const date = new Date(dateString);
            return date.toLocaleString('he-IL');
        } catch (e) {
            return dateString;
        }
    }
    
    // Adding global functions for document handling
    window.viewDocument = function(docId) {
        alert(`צפייה במסמך: ${docId}`);
        // TODO: Implement document viewing
    };
    
    window.deleteDocument = async function(docId) {
        if (!confirm('האם אתה בטוח שברצונך למחוק מסמך זה?')) {
            return;
        }
        
        try {
            const response = await fetch(`${apiBaseUrl}/api/documents/${docId}?language=${languageSelect.value}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showUploadStatus('המסמך נמחק בהצלחה', 'success');
                loadDocuments(); // Refresh list
            } else {
                showUploadStatus(`שגיאה במחיקה: ${data.error || 'שגיאה לא ידועה'}`, 'error');
            }
        } catch (error) {
            showUploadStatus(`שגיאה במחיקה: ${error.message}`, 'error');
        }
    };
});
