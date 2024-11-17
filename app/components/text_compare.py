import difflib

class TextComparer:
    @staticmethod
    def compare_texts(text1: str, text2: str) -> tuple[list[str], float, dict[str, list[str]]]:
        """Compare two texts and return differences, similarity ratio and side-by-side view"""
        # Original diff
        d = difflib.Differ()
        diff = list(d.compare(text1.splitlines(), text2.splitlines()))
        
        # Calculate similarity ratio
        similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
        
        # Generate side by side view
        d = difflib.HtmlDiff()
        side_by_side = {
            'left': [],
            'right': []
        }
        
        left_lines = text1.splitlines()
        right_lines = text2.splitlines()
        matcher = difflib.SequenceMatcher(None, left_lines, right_lines)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                for i in range(i1, i2):
                    side_by_side['left'].append(('equal', left_lines[i]))
                    side_by_side['right'].append(('equal', right_lines[j1 + (i - i1)]))
            elif tag == 'replace':
                for i, j in zip(range(i1, i2), range(j1, j2)):
                    if i < len(left_lines):
                        side_by_side['left'].append(('delete', left_lines[i]))
                    if j < len(right_lines):
                        side_by_side['right'].append(('insert', right_lines[j]))
            elif tag == 'delete':
                for i in range(i1, i2):
                    side_by_side['left'].append(('delete', left_lines[i]))
            elif tag == 'insert':
                for j in range(j1, j2):
                    side_by_side['right'].append(('insert', right_lines[j]))
        
        return diff, similarity, side_by_side