import pdfplumber

class PDFParser:
    def __init__(self):
        self.text = ""
        
    def extract_text(self, pdf_file):
        """Extract text from PDF file"""
        try:
            with pdfplumber.open(pdf_file) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                self.text = text.strip()
                return self.text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")