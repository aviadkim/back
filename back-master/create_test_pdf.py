from fpdf import FPDF
import random

def create_test_financial_document(filename="test_samples/sample_financial.pdf"):
    """Create a sample PDF with financial data for testing"""
    pdf = FPDF()
    pdf.add_page()
    
    # Add header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Financial Portfolio Summary", ln=True, align="C")
    pdf.ln(10)
    
    # Add content
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "Client: Test Client", ln=True)
    pdf.cell(0, 10, "Account Number: ACC123456", ln=True)
    pdf.cell(0, 10, "Valuation Date: April 1, 2025", ln=True)
    pdf.ln(10)
    
    # Securities table
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Securities:", ln=True)
    pdf.ln(5)
    
    # Table header
    pdf.set_font("Arial", "B", 10)
    pdf.cell(50, 10, "ISIN", border=1)
    pdf.cell(70, 10, "Security Name", border=1)
    pdf.cell(30, 10, "Quantity", border=1)
    pdf.cell(40, 10, "Market Value", border=1, ln=True)
    
    # Sample ISINs
    isins = [
        ("US0378331005", "Apple Inc.", 100, 18500),
        ("US5949181045", "Microsoft Corp", 75, 25000),
        ("US88160R1014", "Tesla Inc", 30, 7500),
        ("CH1908490000", "Credit Suisse AG", 200, 15000),
        ("XS2530201644", "Deutsche Bank AG", 150, 12000),
        ("XS2692298537", "UBS Group AG", 120, 9000),
        ("US0231351067", "Amazon.com Inc", 20, 6000),
        ("US38141G1040", "Goldman Sachs", 40, 11000),
        ("US30303M1027", "Meta Platforms", 60, 14000),
        ("US92826C8394", "Visa Inc", 90, 19000)
    ]
    
    # Table content
    pdf.set_font("Arial", "", 10)
    total_value = 0
    for isin, name, quantity, value in isins:
        pdf.cell(50, 10, isin, border=1)
        pdf.cell(70, 10, name, border=1)
        pdf.cell(30, 10, str(quantity), border=1)
        pdf.cell(40, 10, f"${value:,}", border=1, ln=True)
        total_value += value
    
    # Total
    pdf.set_font("Arial", "B", 10)
    pdf.cell(150, 10, "Total Portfolio Value:", border=1)
    pdf.cell(40, 10, f"${total_value:,}", border=1, ln=True)
    pdf.ln(10)
    
    # Asset allocation
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Asset Allocation:", ln=True)
    pdf.ln(5)
    
    allocations = [
        ("Equities", 65),
        ("Bonds", 25),
        ("Cash", 10)
    ]
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(100, 10, "Asset Class", border=1)
    pdf.cell(40, 10, "Allocation (%)", border=1, ln=True)
    
    pdf.set_font("Arial", "", 10)
    for asset_class, percentage in allocations:
        pdf.cell(100, 10, asset_class, border=1)
        pdf.cell(40, 10, f"{percentage}%", border=1, ln=True)
    
    # Save the PDF
    pdf.output(filename)
    print(f"Created test financial document: {filename}")

if __name__ == "__main__":
    import os
    
    # Create directory if it doesn't exist
    os.makedirs("test_samples", exist_ok=True)
    
    create_test_financial_document()
