import os
import subprocess
import sys

def check_binary(binary_name):
    try:
        result = subprocess.run(['which', binary_name], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout:
            path = result.stdout.strip()
            print(f"✅ {binary_name} found at: {path}")
            return True
        else:
            print(f"❌ {binary_name} not found in PATH")
            return False
    except Exception as e:
        print(f"❌ Error checking {binary_name}: {str(e)}")
        return False

def check_tesseract():
    if check_binary('tesseract'):
        # Check version and available languages
        try:
            version = subprocess.run(['tesseract', '--version'], capture_output=True, text=True)
            print("Tesseract version info:")
            print(version.stdout.split('\n')[0])
            
            langs = subprocess.run(['tesseract', '--list-langs'], capture_output=True, text=True)
            print("\nAvailable languages:")
            for lang in langs.stdout.strip().split('\n')[1:]: # Skip the first line
                print(f"  - {lang}")
            return True
        except Exception as e:
            print(f"❌ Error getting tesseract info: {str(e)}")
            return False
    return False

def check_poppler():
    if check_binary('pdfinfo'):
        # Check version
        try:
            version = subprocess.run(['pdfinfo', '-v'], capture_output=True, text=True)
            print("Poppler version info:")
            print(version.stderr.split('\n')[0])  # Version is in stderr for some reason
            return True
        except Exception as e:
            print(f"❌ Error getting poppler info: {str(e)}")
            return False
    return False

if __name__ == "__main__":
    print("Checking required binaries...\n")
    tesseract_ok = check_tesseract()
    print("\n" + "-" * 50 + "\n")
    poppler_ok = check_poppler()
    
    print("\n" + "=" * 50)
    if tesseract_ok and poppler_ok:
        print("✅ All required binaries found!")
    else:
        print("❌ Some required binaries are missing.")
        
    print("\nChecking Python imports...")
    try:
        import cv2
        print("✅ OpenCV (cv2) imports successfully")
    except ImportError as e:
        print(f"❌ OpenCV import error: {str(e)}")
