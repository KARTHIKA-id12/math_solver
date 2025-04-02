from config import GEMINI_API_KEY
import google.generativeai as genai
import re

# Configure the Gemini API
genai.configure(api_key=GEMINI_API_KEY)

def clean_solution_text(text):
    """Clean up the solution text by removing unwanted asterisks and formatting properly."""
    # Remove standalone asterisks that aren't part of math expressions
    text = re.sub(r'(?<!\$)\*\*(?!\$)', '', text)  # Remove ** that aren't within math expressions
    text = re.sub(r'(?<!\$)\*(?!\$)', '', text)     # Remove * that aren't within math expressions
    
    # Clean up extra whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Ensure proper LaTeX delimiters
    # Replace incorrect $ usage with proper LaTeX delimiters
    text = re.sub(r'\$(.*?)\$', r'\\(\1\\)', text)
    text = re.sub(r'\$\$(.*?)\$\$', r'\\[\1\\]', text)
    
    return text

def solve_problem(question_text):
    try:
        # Configure the model
        generation_config = {
            "temperature": 0.1,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": 2048,
        }
        
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        
        # Initialize Gemini model
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Create prompt with specific formatting instructions
        prompt = f"""
        You are an expert math tutor. Please solve the following math problem step by step:
        
        {question_text}
        
        Format your solution exactly like a textbook with these requirements:
        1. Start with a "Problem Statement" section.
        2. Number each step clearly (e.g., "Step 1: [Step Name]").
        3. Format all mathematical expressions using LaTeX notation with $ for inline math and $$ for display equations.
        4. Break down the solution into clear, logical steps.
        5. For each step:
           - Briefly explain what we're doing
           - Show the mathematical work
           - Explain what the result means
        6. End with a "Final Answer" section that states the answer clearly.
        7. IMPORTANT: DO NOT use asterisks (*) for emphasis or bullets, use proper HTML formatting instead.
        8. Use the cleanest possible formatting without any markdown artifacts.
        9. Make sure all equation formatting is correct and renders properly in MathJax.
        
        Your solution MUST use proper LaTeX formatting and should be clear and professional.
        """
        
        # Get response from Gemini
        response = model.generate_content(prompt)
        
        # Extract and clean the solution text
        solution = response.text
        solution = clean_solution_text(solution)
        
        # Convert newlines to HTML line breaks to preserve formatting
        solution = solution.replace('\n', '<br>')
        
        # Enhance formatting for steps
        solution = re.sub(r'(Step \d+:)', r'<div class="step">\1</div>', solution)
        
        # Format the final answer
        solution = solution.replace('Final Answer', '<div class="final-answer">Final Answer</div>')
        solution = solution.replace('final answer', '<div class="final-answer">Final Answer</div>')
        
        # Clean up redundant breaks
        solution = solution.replace('<br><br>', '<br>')
        solution = solution.replace('<div class="step"><br>', '<div class="step">')
        
        return question_text, solution
        
    except Exception as e:
        return question_text, f"Error solving the problem: {str(e)}"