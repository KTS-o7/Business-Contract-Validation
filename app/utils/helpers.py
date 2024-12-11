import os

def validate_file_type(file_path: str, allowed_extensions: list[str] = ['.pdf']) -> bool:
    """Validate file type based on extension"""
    _, extension = os.path.splitext(file_path)
    return extension.lower() in allowed_extensions

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    return ' '.join(text.split())

