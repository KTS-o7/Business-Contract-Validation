import pytest
from unittest.mock import Mock, patch
from app.components.ner_extractor import NERExtractor

@pytest.fixture
def mock_nlp():
    mock = Mock()
    mock.ents = [
        Mock(label_="PERSON", text="John Doe"),
        Mock(label_="ORG", text="ACME Corp"),
        Mock(label_="MONEY", text="$50,000"),
        Mock(label_="PERSON", text="Jane Smith")
    ]
    return mock

class TestNERExtractor:
    @patch('spacy.load')
    def test_init(self, mock_load):
        extractor = NERExtractor()
        mock_load.assert_called_once_with("en_core_web_sm")
        assert extractor.nlp is not None

    @patch('spacy.load')
    def test_extract_entities(self, mock_load, mock_nlp):
        # Setup
        mock_load.return_value = Mock(return_value=mock_nlp)
        extractor = NERExtractor()
        extractor.nlp = lambda x: mock_nlp

        # Test
        result = extractor.extract_entities("Sample text")
        
        expected = {
            "PERSON": ["John Doe", "Jane Smith"],
            "ORG": ["ACME Corp"],
            "MONEY": ["$50,000"]
        }
        assert result == expected

    @patch('spacy.load')
    def test_empty_text(self, mock_load):
        mock_load.return_value = Mock(return_value=Mock(ents=[]))
        extractor = NERExtractor()
        extractor.nlp = lambda x: Mock(ents=[])
        
        result = extractor.extract_entities("")
        assert result == {}

    @patch('spacy.load')
    def test_no_entities(self, mock_load):
        mock_load.return_value = Mock(return_value=Mock(ents=[]))
        extractor = NERExtractor()
        extractor.nlp = lambda x: Mock(ents=[])
        
        result = extractor.extract_entities("Text with no named entities")
        assert result == {}