# tests/test_llm_analyzer.py
import pytest
from unittest.mock import Mock, patch
from app.components.llm_analyzer import LLMAnalyzer

@pytest.fixture
def mock_groq_response():
    return Mock(choices=[Mock(message=Mock(content="Test analysis response"))])

@pytest.fixture
def sample_differences():
    return [
        "- Original: Salary of $50,000",
        "+ Modified: Salary of $60,000"
    ]

@pytest.fixture
def large_differences():
    return [f"Difference {i}" for i in range(2000)]  # Create large dataset

@pytest.fixture
def sample_entities():
    return {
        "MONEY": ["$50,000", "$60,000"],
        "ORG": ["ACME Corp"],
        "PERSON": ["John Doe"]
    }

class TestLLMAnalyzer:
    def test_init(self):
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
            analyzer = LLMAnalyzer()
            assert analyzer.client is not None

    def test_init_no_api_key(self):
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                LLMAnalyzer()
            assert "GROQ_API_KEY environment variable is required" in str(exc_info.value)

    def test_create_prompt(self, sample_differences, sample_entities):
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
            analyzer = LLMAnalyzer()
            prompt = analyzer._create_prompt(sample_differences, sample_entities)
            assert "Changes:" in prompt
            assert sample_differences[0] in prompt
            assert str(sample_entities) in prompt

    def test_chunk_differences(self):
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
            analyzer = LLMAnalyzer()
            differences = list(range(25))
            chunks = analyzer._chunk_differences(differences, chunk_size=10)
            assert len(chunks) == 3
            assert len(chunks[0]) == 10
            assert len(chunks[1]) == 10
            assert len(chunks[2]) == 5

    def test_analyze_chunk(self, mock_groq_response, sample_differences, sample_entities):
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
            with patch('app.components.llm_analyzer.Groq') as mock_groq:
                mock_groq.return_value.chat.completions.create.return_value = mock_groq_response
                analyzer = LLMAnalyzer()
                result = analyzer._analyze_chunk(sample_differences, sample_entities)
                assert result == "Test analysis response"
                mock_groq.return_value.chat.completions.create.assert_called_once()

    def test_synthesize_analyses(self, mock_groq_response):
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
            with patch('app.components.llm_analyzer.Groq') as mock_groq:
                mock_groq.return_value.chat.completions.create.return_value = mock_groq_response
                analyzer = LLMAnalyzer()
                analyses = ["Analysis 1", "Analysis 2"]
                result = analyzer._synthesize_analyses(analyses)
                assert result == "Test analysis response"
                mock_groq.return_value.chat.completions.create.assert_called_once()

    def test_analyze_differences_small_input(self, mock_groq_response, sample_differences, sample_entities):
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
            with patch('app.components.llm_analyzer.Groq') as mock_groq:
                mock_groq.return_value.chat.completions.create.return_value = mock_groq_response
                analyzer = LLMAnalyzer()
                result = analyzer.analyze_differences(sample_differences, sample_entities)
                assert result == "Test analysis response"
                mock_groq.return_value.chat.completions.create.assert_called_once()

    def test_analyze_differences_large_input(self, mock_groq_response, large_differences, sample_entities):
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
            with patch('app.components.llm_analyzer.Groq') as mock_groq:
                mock_groq.return_value.chat.completions.create.return_value = mock_groq_response
                analyzer = LLMAnalyzer()
                result = analyzer.analyze_differences(large_differences, sample_entities)
                assert result == "Test analysis response"
                # Should be called multiple times - once for each chunk plus synthesis
                assert mock_groq.return_value.chat.completions.create.call_count > 1

    def test_analyze_differences_error(self, sample_differences, sample_entities):
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
            with patch('app.components.llm_analyzer.Groq') as mock_groq:
                mock_groq.return_value.chat.completions.create.side_effect = Exception("Analysis Error")
                analyzer = LLMAnalyzer()
                with pytest.raises(RuntimeError) as exc_info:
                    analyzer.analyze_differences(sample_differences, sample_entities)
                assert "Error analyzing differences: Analysis Error" in str(exc_info.value)
                mock_groq.return_value.chat.completions.create.assert_called_once()

    def test_analyze_empty_differences(self, mock_groq_response, sample_entities):
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
            with patch('app.components.llm_analyzer.Groq') as mock_groq:
                mock_groq.return_value.chat.completions.create.return_value = mock_groq_response
                analyzer = LLMAnalyzer()
                result = analyzer.analyze_differences([], sample_entities)
                assert result == "Test analysis response"
                mock_groq.return_value.chat.completions.create.assert_called_once()

    @pytest.mark.parametrize("invalid_input", [
        None,
        123,
        "string",
        {"key": "value"}
    ])
    def test_analyze_invalid_differences(self, invalid_input, sample_entities):
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
            analyzer = LLMAnalyzer()
            with pytest.raises(Exception):
                analyzer.analyze_differences(invalid_input, sample_entities)