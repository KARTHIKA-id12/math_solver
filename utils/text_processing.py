import re

# Clean and format text
def clean_text(text):
    """
    Clean and format the text input to prepare it for math solving.
    Preserves important math symbols and operators.
    """
    # Remove extra whitespace
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    
    # Replace common OCR errors in math context
    text = text.replace('x', '×').replace('X', '×')  # Replace 'x' with multiplication symbol if needed
    
    # Fix spaces around operators
    text = re.sub(r'(?<=[0-9])([+\-×÷=])(?=[0-9])', r' \1 ', text)
    
    return text

def format_math_output(text):
    """
    Format math solution output to be more readable
    """
    # Replace plain text equations with LaTeX if needed
    # This is a simple example, actual implementation would be more complex
    text = re.sub(r'(\d+)/(\d+)', r'\\frac{\1}{\2}', text)
    return text