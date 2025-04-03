#!/bin/bash

echo "===== Running Document Q&A Test with Real PDF ====="

# Default values
QUESTIONS=10
PDF_PATH=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --pdf)
      PDF_PATH="$2"
      shift
      shift
      ;;
    --questions)
      QUESTIONS="$2"
      shift
      shift
      ;;
    *)
      shift
      ;;
  esac
done

# Create necessary directories
mkdir -p /workspaces/back/uploads
mkdir -p /workspaces/back/extractions
mkdir -p /workspaces/back/qa_test_results
chmod 755 /workspaces/back/uploads
chmod 755 /workspaces/back/extractions
chmod 755 /workspaces/back/qa_test_results

# Make sure the test script is executable
chmod +x /workspaces/back/quick_qa_test.py

# Check if the application is running
echo "Checking if application is running..."
curl -s http://localhost:5003/health > /dev/null
if [ $? -ne 0 ]; then
    echo "Application is not running at http://localhost:5003"
    echo "Starting application..."
    
    cd /workspaces/back/project_organized
    python app.py > /dev/null 2>&1 &
    APP_PID=$!
    
    # Wait for the application to start
    echo "Waiting for application to start..."
    for i in {1..15}; do
        echo -n "."
        sleep 1
        curl -s http://localhost:5003/health > /dev/null
        if [ $? -eq 0 ]; then
            echo " Application started!"
            break
        fi
        
        if [ $i -eq 15 ]; then
            echo " Failed to start application."
            echo "Check app.py for errors"
            exit 1
        fi
    done
else
    echo "Application is already running at http://localhost:5003"
fi

# Check if we already have PDFs in the uploads directory
if [ -z "$PDF_PATH" ]; then
    echo "Looking for existing PDF files..."
    if [ -d "/workspaces/back/uploads" ] && [ "$(ls -A /workspaces/back/uploads | grep -c '\.pdf$')" -gt 0 ]; then
        echo "Found existing PDF files in uploads directory"
    else
        # Create a sample PDF file for testing if no PDFs exist and none specified
        echo "Creating a sample PDF file for testing..."
        pip install reportlab > /dev/null 2>&1
        python - << EOF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

os.makedirs('/workspaces/back/uploads', exist_ok=True)
pdf_path = '/workspaces/back/uploads/test_financial_report.pdf'
c = canvas.Canvas(pdf_path, pagesize=letter)
c.setFont("Helvetica", 12)

# Add some financial content
c.drawString(100, 750, "XYZ Investment Holdings - Portfolio Statement")
c.drawString(100, 730, "Client: John Smith")
c.drawString(100, 710, "Account Number: 12345678")
c.drawString(100, 690, "Date: April 15, 2025")
c.drawString(100, 670, "Valuation Date: April 14, 2025")

c.drawString(100, 640, "Portfolio Summary:")
c.drawString(120, 620, "Total Value: $2,345,678.90")
c.drawString(120, 600, "Stocks: 70% ($1,642,975.23)")
c.drawString(120, 580, "Bonds: 20% ($469,135.78)")
c.drawString(120, 560, "Cash: 10% ($234,567.89)")

c.drawString(100, 530, "Holdings:")
c.drawString(120, 510, "1. Apple Inc. (AAPL) - ISIN US0378331005")
c.drawString(140, 490, "Shares: 1000")
c.drawString(140, 470, "Price: $178.25")
c.drawString(140, 450, "Value: $178,250.00")

c.drawString(120, 430, "2. Microsoft Corp (MSFT) - ISIN US5949181045")
c.drawString(140, 410, "Shares: 500")
c.drawString(140, 390, "Price: $402.75")
c.drawString(140, 370, "Value: $201,375.00")

c.drawString(120, 350, "3. Amazon.com Inc (AMZN) - ISIN US0231351067")
c.drawString(140, 330, "Shares: 300")
c.drawString(140, 310, "Price: $185.35")
c.drawString(140, 290, "Value: $55,605.00")

c.save()
print(f"Created sample PDF at {pdf_path}")
PDF_PATH=pdf_path
EOF
        PDF_PATH="/workspaces/back/uploads/test_financial_report.pdf"
    fi
fi

# Run the test
echo -e "\nRunning Q&A test with real PDF and $QUESTIONS questions..."
if [ -n "$PDF_PATH" ]; then
    python /workspaces/back/quick_qa_test.py --questions $QUESTIONS --pdf "$PDF_PATH"
else
    python /workspaces/back/quick_qa_test.py --questions $QUESTIONS
fi

# Show results
echo -e "\nLatest test results:"
LATEST_RESULT=$(ls -t /workspaces/back/qa_test_results/quick_qa_test_*.txt | head -n 1)
if [ -f "$LATEST_RESULT" ]; then
    cat "$LATEST_RESULT"
else
    echo "No test results found"
fi

echo -e "\nTest complete! The results are saved in the qa_test_results directory."
