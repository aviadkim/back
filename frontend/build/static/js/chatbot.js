document.addEventListener('DOMContentLoaded', function() {
    const chatbotContainer = document.getElementById('chatbot-container');
    const apiBaseUrl = window.location.origin;
    
    // Check if API is available
    fetch(apiBaseUrl + '/api/health')
        .then(response => {
            if (!response.ok) {
                throw new Error('API health check failed');
            }
            return response.json();
        })
        .then(data => {
            console.log('API Health check response:', data);
            if (data.status === 'ok' || data.status === 'warning') {
                // API is available (even if using dummy model), initialize chatbot
                initializeChatbot(data.status === 'warning');
            } else {
                showError('API unavailable: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error checking API health:', error);
            // Try fallback to the regular health endpoint
            fetch(apiBaseUrl + '/health')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'ok') {
                        initializeChatbot(true); // Initialize with warning
                    } else {
                        showError('API health check failed: ' + error.message);
                    }
                })
                .catch(e => {
                    showError('API health check failed: ' + error.message);
                });
        });
    
    // Function to show errors in the chatbot container
    function showError(message) {
        chatbotContainer.innerHTML = `
            <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
                <strong class="font-bold">שגיאה!</strong>
                <span class="block sm:inline"> ${message}</span>
            </div>
        `;
    }
    
    // Function to initialize the chatbot
    function initializeChatbot(isDummyMode) {
        // Create chatbot UI
        chatbotContainer.innerHTML = `
            <div class="h-full flex flex-col">
                <div class="flex-1 overflow-y-auto p-4" id="chat-messages">
                    <div class="bg-blue-100 p-3 rounded mb-4">
                        <p class="font-semibold">ברוכים הבאים לצ'אט החכם!</p>
                        <p>העלה מסמכים ושאל שאלות לגביהם.</p>
                        ${isDummyMode ? 
                            '<p class="text-yellow-700 mt-2"><b>הערה:</b> המערכת פועלת במצב מוגבל (מודל דמה). לחוויה מלאה, נדרש מפתח API תקף.</p>' : 
                            ''}
                    </div>
                </div>
                <div class="border-t p-4">
                    <div class="flex space-x-2 space-x-reverse">
                        <select id="document-selector" class="border rounded p-2 flex-1">
                            <option value="">כל המסמכים</option>
                        </select>
                    </div>
                    <div class="flex space-x-2 space-x-reverse mt-2">
                        <input type="text" id="chat-input" placeholder="הקלד שאלה כאן..." 
                               class="border rounded p-2 flex-1">
                        <button id="send-button" class="bg-blue-600 text-white px-4 py-2 rounded">
                            שלח
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Get references to elements
        const chatMessages = document.getElementById('chat-messages');
        const chatInput = document.getElementById('chat-input');
        const sendButton = document.getElementById('send-button');
        const documentSelector = document.getElementById('document-selector');
        
        // Load available documents for the selector
        loadDocumentsForSelector();
        
        // Initialize conversation state
        let conversationId = null;
        
        // Add event listeners
        sendButton.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        // Function to send a message
        function sendMessage() {
            const question = chatInput.value.trim();
            if (!question) return;
            
            // Add user message to chat
            addMessageToChat('user', question);
            
            // Clear input
            chatInput.value = '';
            
            // Show thinking indicator
            const thinkingElement = document.createElement('div');
            thinkingElement.className = 'flex items-center p-3 rounded bg-gray-100 my-2 max-w-md ml-auto';
            thinkingElement.innerHTML = '<div class="ml-2">חושב...</div>';
            chatMessages.appendChild(thinkingElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            // Get selected document(s)
            const selectedDoc = documentSelector.value;
            const documentIds = selectedDoc ? [selectedDoc] : [];
            
            // Send to API
            fetch(`${apiBaseUrl}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    question: question,
                    document_ids: documentIds,
                    conversation_id: conversationId,
                    language: 'he'
                })
            })
            .then(response => response.json())
            .then(data => {
                // Remove thinking indicator
                chatMessages.removeChild(thinkingElement);
                
                // Update conversation ID
                if (data.conversation_id) {
                    conversationId = data.conversation_id;
                }
                
                // Add response to chat
                if (data.error) {
                    addMessageToChat('error', data.error);
                } else {
                    addMessageToChat('assistant', data.answer, data.sources);
                }
            })
            .catch(error => {
                // Remove thinking indicator
                chatMessages.removeChild(thinkingElement);
                
                // Show error
                addMessageToChat('error', 'שגיאה בתקשורת עם השרת: ' + error.message);
            });
        }
        
        // Function to add message to chat
        function addMessageToChat(role, content, sources = []) {
            const messageElement = document.createElement('div');
            
            if (role === 'user') {
                messageElement.className = 'flex items-center p-3 rounded bg-blue-100 my-2 max-w-md ml-0 mr-auto';
                messageElement.innerHTML = `
                    <div>
                        <div class="font-semibold">שאלה:</div>
                        <div>${content}</div>
                    </div>
                `;
            } else if (role === 'assistant') {
                messageElement.className = 'flex items-center p-3 rounded bg-gray-100 my-2 max-w-md ml-auto';
                
                let sourcesHtml = '';
                if (sources && sources.length > 0) {
                    sourcesHtml = `
                        <div class="text-xs mt-2 text-gray-600">
                            <span class="font-semibold">מקורות:</span> 
                            ${sources.join(', ')}
                        </div>
                    `;
                }
                
                messageElement.innerHTML = `
                    <div>
                        <div class="font-semibold">תשובה:</div>
                        <div>${content}</div>
                        ${sourcesHtml}
                    </div>
                `;
            } else if (role === 'error') {
                messageElement.className = 'flex items-center p-3 rounded bg-red-100 text-red-800 my-2';
                messageElement.innerHTML = `
                    <div>
                        <div class="font-semibold">שגיאה:</div>
                        <div>${content}</div>
                    </div>
                `;
            }
            
            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        // Function to load documents for the selector
        function loadDocumentsForSelector() {
            fetch(`${apiBaseUrl}/api/documents?language=he`)
                .then(response => response.json())
                .then(data => {
                    if (data.documents) {
                        // Clear existing options except "All Documents"
                        while (documentSelector.options.length > 1) {
                            documentSelector.remove(1);
                        }
                        
                        // Add document options
                        data.documents.forEach(doc => {
                            const option = document.createElement('option');
                            option.value = doc.document_id;
                            
                            const fileName = doc.document_id.split('/').pop();
                            option.textContent = fileName;
                            
                            documentSelector.appendChild(option);
                        });
                    }
                })
                .catch(error => {
                    console.error('Error loading documents for selector:', error);
                });
        }
    }
});