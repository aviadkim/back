try:
    import PyPDF2
    print(f"PyPDF2 version: {PyPDF2.__version__}")
    
    # Check for PdfReader
    if hasattr(PyPDF2, 'PdfReader'):
        print("PdfReader is available")
    else:
        print("PdfReader not found, likely using PdfFileReader")
        
    # Create a dummy reader to test
    import io
    dummy_pdf = io.BytesIO(b'%PDF-1.7\n%\xe2\xe3\xcf\xd3\n')
    try:
        if hasattr(PyPDF2, 'PdfReader'):
            reader = PyPDF2.PdfReader(dummy_pdf)
            print("Successfully created PdfReader")
        else:
            reader = PyPDF2.PdfFileReader(dummy_pdf)
            print("Successfully created PdfFileReader")
    except Exception as e:
        print(f"Error creating reader: {e}")
        
except ImportError:
    print("PyPDF2 is not installed")
    
except Exception as e:
    print(f"Error: {e}")
