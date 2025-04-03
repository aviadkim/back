import requests
import os
import sys
import time

def test_document_upload(base_url, pdf_path, language="heb+eng"):
    """Test uploading a document to the system"""
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: PDF file not found at {pdf_path}")
        return False
    
    try:
        # Prepare the file and form data
        files = {'file': open(pdf_path, 'rb')}
        data = {'language': language}
        
        print(f"Uploading {pdf_path} to {base_url}/api/documents/upload...")
        response = requests.post(f"{base_url}/api/documents/upload", files=files, data=data)
        
        print(f"Upload status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Document uploaded successfully")
            result = response.json()
            print(f"Response: {result}")
            
            # If there's a document_id, try to get its status
            if 'document_id' in result:
                doc_id = result['document_id']
                print(f"\nChecking status of document {doc_id}...")
                
                # Poll for status a few times
                max_attempts = 5
                for i in range(max_attempts):
                    status_response = requests.get(f"{base_url}/api/documents/{doc_id}")
                    if status_response.status_code == 200:
                        status = status_response.json()
                        print(f"Document status (attempt {i+1}/{max_attempts}): {status.get('status', 'unknown')}")
                        if status.get('status') in ['completed', 'failed']:
                            print(f"Final status: {status}")
                            break
                    else:
                        print(f"❌ Failed to get document status: {status_response.status_code}")
                        break
                    
                    # Wait a bit before checking again
                    time.sleep(2)
            
            return True
        else:
            print(f"❌ Upload failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error during upload: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Make sure to close the file
        if 'files' in locals() and 'file' in files:
            files['file'].close()

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_document_upload.py <pdf_path> [base_url] [language]")
        print("Example: python test_document_upload.py test_documents/sample.pdf http://localhost:5001 heb+eng")
        return
    
    pdf_path = sys.argv[1]
    base_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:5001"
    language = sys.argv[3] if len(sys.argv) > 3 else "heb+eng"
    
    test_document_upload(base_url, pdf_path, language)

if __name__ == "__main__":
    main()
