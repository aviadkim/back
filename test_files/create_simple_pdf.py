from fpdf import FPDF

def create_simple_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add header - avoid Unicode characters
    pdf.cell(200, 10, txt="INVOICE", ln=True, align='C')
    pdf.cell(200, 10, txt="Invoice #: INV-2025-001", ln=True)
    pdf.cell(200, 10, txt="Date: March 30, 2025", ln=True)
    
    # Add vendor details
    pdf.cell(200, 10, txt="ABC Financial Services", ln=True)
    pdf.cell(200, 10, txt="123 Finance Street", ln=True)
    pdf.cell(200, 10, txt="Tel Aviv, 6701101", ln=True)
    
    # Add invoice items - avoid currency symbols
    pdf.ln(10)
    pdf.cell(200, 10, txt="INVOICE ITEMS:", ln=True)
    pdf.cell(100, 10, txt="Financial Analysis Report", ln=False)
    pdf.cell(30, 10, txt="2,500.00 NIS", ln=True, align='R')
    
    pdf.cell(100, 10, txt="Investment Portfolio Review", ln=False)
    pdf.cell(30, 10, txt="1,750.00 NIS", ln=True, align='R')
    
    # Add totals
    pdf.ln(10)
    pdf.cell(130, 10, txt="Total:", ln=False, align='R')
    pdf.cell(30, 10, txt="4,250.00 NIS", ln=True, align='R')
    
    # Save the PDF
    output_path = "test_files/test_invoice.pdf"
    pdf.output(output_path)
    print(f"Created test PDF: {output_path}")

if __name__ == "__main__":
    create_simple_pdf()
