import requests
import os
import sys
import time
import json

class AppTester:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def check_health(self):
        """Check if the application is running and healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ Application is healthy!")
                return True
            else:
                print(f"❌ Health check failed with status code: {response.status_code}")
                print(response.text)
                return False
        except Exception as e:
            print(f"❌ Health check failed with error: {str(e)}")
            return False
    
    def upload_document(self, pdf_path, language="heb+eng"):
        """Upload a PDF document for processing."""
        if not os.path.exists(pdf_path):
            print(f"❌ File not found: {pdf_path}")
            return None
        
        print(f"Uploading {pdf_path}...")
        try:
            with open(pdf_path, 'rb') as file:
                files = {'file': file}
                data = {'language': language}
                response = self.session.post(
                    f"{self.base_url}/api/documents/upload", 
                    files=files, 
                    data=data
                )
            
            if response.status_code == 200:
                print("✅ Document uploaded successfully!")
                result = response.json()
                return result
            else:
                print(f"❌ Upload failed with status code: {response.status_code}")
                print(response.text)
                return None
        except Exception as e:
            print(f"❌ Upload failed with error: {str(e)}")
            return None
    
    def get_document_status(self, document_id):
        """Check the processing status of a document."""
        try:
            response = self.session.get(f"{self.base_url}/api/documents/{document_id}")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Status check failed: {response.status_code}")
                print(response.text)
                return None
        except Exception as e:
            print(f"❌ Status check failed: {str(e)}")
            return None
    
    def wait_for_processing(self, document_id, max_tries=20, interval=2):
        """Wait for document processing to complete."""
        print(f"Waiting for document {document_id} to be processed...")
        
        for i in range(max_tries):
            status = self.get_document_status(document_id)
            if not status:
                print("Failed to get document status")
                return None
            
            if status.get('status') == 'completed':
                print("✅ Document processing completed!")
                return status
            elif status.get('status') == 'failed':
                print("❌ Document processing failed!")
                return status
            
            print(f"Status: {status.get('status')} ({i+1}/{max_tries})")
            time.sleep(interval)
        
        print("⚠️ Timed out waiting for document processing")
        return None

def main():
    if len(sys.argv) < 3:
        print("Usage: python test_app_functionality.py <base_url> <pdf_path>")
        print("Example: python test_app_functionality.py http://localhost:5001 test_documents/sample.pdf")
        sys.exit(1)
    
    base_url = sys.argv[1]
    pdf_path = sys.argv[2]
    
    tester = AppTester(base_url)
    
    # Step 1: Check if the app is healthy
    if not tester.check_health():
        print("Exiting due to health check failure")
        sys.exit(1)
    
    # Step 2: Upload a document
    upload_result = tester.upload_document(pdf_path)
    if not upload_result:
        print("Exiting due to upload failure")
        sys.exit(1)
    
    document_id = upload_result.get('document_id')
    if not document_id:
        print("Failed to get document ID from upload response")
        print("Response:", json.dumps(upload_result, indent=2))
        sys.exit(1)
    
    # Step 3: Wait for processing to complete
    final_status = tester.wait_for_processing(document_id)
    if final_status:
        print("\nFinal document status:")
        print(json.dumps(final_status, indent=2))
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()
