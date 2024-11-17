import pytest
from unittest.mock import Mock, patch, mock_open
from io import BytesIO
from app.components.pdf_parser import PDFParser

@pytest.fixture
def sample_pdf_content():
    return "This is a sample PDF content\nWith multiple lines"

@pytest.fixture
def mock_pdf():
    mock = Mock()
    mock.pages = [
        Mock(extract_text=lambda: "Page 1 content"),
        Mock(extract_text=lambda: "Page 2 content")
    ]
    return mock

class TestPDFParser:
    def test_init(self):
        parser = PDFParser()
        assert parser.text == ""

    @patch('pdfplumber.open')
    def test_extract_text_success(self, mock_open, mock_pdf):
        # Setup
        mock_open.return_value.__enter__.return_value = mock_pdf
        parser = PDFParser()
        
        # Test
        result = parser.extract_text("dummy.pdf")
        expected = "Page 1 content\nPage 2 content"
        
        assert result.strip() == expected.strip()
        assert parser.text.strip() == expected.strip()
        mock_open.assert_called_once()

    @patch('pdfplumber.open')
    def test_extract_text_empty_pdf(self, mock_open):
        mock_pdf = Mock()
        mock_pdf.pages = []
        mock_open.return_value.__enter__.return_value = mock_pdf
        
        parser = PDFParser()
        result = parser.extract_text("empty.pdf")
        
        assert result == ""
        assert parser.text == ""

    @patch('pdfplumber.open')
    def test_extract_text_error(self, mock_open):
        # Setup error case
        mock_open.side_effect = Exception("PDF Error")
        parser = PDFParser()
        
        # Test error handling
        with pytest.raises(Exception) as exc_info:
            parser.extract_text("invalid.pdf")
        
        assert "Error extracting text from PDF: PDF Error" in str(exc_info.value)

    def test_file_not_found(self):
        parser = PDFParser()
        with pytest.raises(Exception):
            parser.extract_text("nonexistent.pdf")