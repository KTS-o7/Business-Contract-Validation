import pytest
from app.components.text_compare import TextComparer

class TestTextComparer:
    @pytest.fixture
    def identical_texts(self):
        return "This is a test.\nSecond line.", "This is a test.\nSecond line."
    
    @pytest.fixture
    def different_texts(self):
        return "Original text.", "Completely different."
    
    @pytest.fixture
    def modified_texts(self):
        return ("This is line one.\nOriginal line two.\nUnchanged line.",
                "This is modified.\nNew line two.\nUnchanged line.")
    @pytest.fixture
    def insert_texts(self):
        return ("Base text\nUnchanged line",
                "Base text\nNew inserted line\nUnchanged line")

    def test_identical_texts(self, identical_texts):
        text1, text2 = identical_texts
        diff, similarity, side_by_side = TextComparer.compare_texts(text1, text2)
        
        assert similarity == 1.0
        assert all(line.startswith('  ') for line in diff)
        assert all(tag == 'equal' for tag, _ in side_by_side['left'])
        assert all(tag == 'equal' for tag, _ in side_by_side['right'])

    def test_completely_different_texts(self, different_texts):
        text1, text2 = different_texts
        diff, similarity, side_by_side = TextComparer.compare_texts(text1, text2)
        
        assert similarity < 0.5
        assert any(line.startswith('- ') for line in diff)
        assert any(line.startswith('+ ') for line in diff)
        assert any(tag == 'delete' for tag, _ in side_by_side['left'])
        assert any(tag == 'insert' for tag, _ in side_by_side['right'])

    def test_modified_texts(self, modified_texts):
        text1, text2 = modified_texts
        diff, similarity, side_by_side = TextComparer.compare_texts(text1, text2)
        
        assert 0 < similarity < 1
        assert any(line.startswith('  ') for line in diff)  # unchanged lines
        assert any(line.startswith('- ') for line in diff)  # deleted lines
        assert any(line.startswith('+ ') for line in diff)  # added lines

    def test_empty_texts(self):
        diff, similarity, side_by_side = TextComparer.compare_texts("", "")
        
        assert similarity == 1.0
        assert len(diff) == 0
        assert len(side_by_side['left']) == 0
        assert len(side_by_side['right']) == 0

    def test_one_empty_text(self):
        text = "Some content\nMultiple lines"
        diff, similarity, side_by_side = TextComparer.compare_texts(text, "")
        
        assert similarity == 0.0
        assert all(line.startswith('- ') for line in diff)
        assert all(tag == 'delete' for tag, _ in side_by_side['left'])
        assert len(side_by_side['right']) == 0
        
    def test_insert_only(self, insert_texts):
        """Test when only insertions are made to the text"""
        text1, text2 = insert_texts
        diff, similarity, side_by_side = TextComparer.compare_texts(text1, text2)
        
        # Verify insertions
        assert any(line.startswith('+ New inserted line') for line in diff)
        assert any(tag == 'insert' for tag, line in side_by_side['right'] if line == 'New inserted line')
        
        # Verify unchanged parts remain
        assert any(tag == 'equal' for tag, line in side_by_side['left'] if line == 'Base text')
        assert any(tag == 'equal' for tag, line in side_by_side['right'] if line == 'Base text')
        
        # Verify structure
        assert len(side_by_side['left']) < len(side_by_side['right'])  # Right has extra inserted line
        assert 0 < similarity < 1  # Partially similar