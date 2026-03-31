"""
PDF Text Extraction Module
Handles extracting and processing text from PDF files
"""

import os
import re
from typing import Dict, List, Optional
import logging

# Import PDF processing libraries
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

logger = logging.getLogger(__name__)

class PDFProcessor:
    """
    Handles PDF text extraction and processing
    """
    
    def __init__(self):
       
        self.supported_libraries = []
        
        # Check for PyPDF2
        try:
            import PyPDF2
            self.supported_libraries.append('PyPDF2')
            print("✅ PyPDF2 library available")
        except ImportError:
            print("❌ PyPDF2 library not available")
        
        # Check for pdfplumber
        try:
            import pdfplumber
            self.supported_libraries.append('pdfplumber')
            print("✅ pdfplumber library available")
        except ImportError:
            print("❌ pdfplumber library not available")
        
        # Raise error if no libraries are available
        if not self.supported_libraries:
            raise ImportError(
                "No PDF processing libraries available. Please install PyPDF2 or pdfplumber:\n"
                "pip install PyPDF2 pdfplumber"
            )
    
    
    def extract_text(self, pdf_path: str) -> Dict:
        """
        Extract text from PDF file using available libraries
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted text and metadata
            
        TODO: Implement this method to:
        1. Check if file exists
        2. Try different extraction methods (PyPDF2, pdfplumber)
        3. Choose the best result
        4. Process and structure the text
        5. Return dictionary with raw_text, processed_text, extraction_method, page_count, word_count, character_count
        """
        pass

        # check if file exists
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # check if its a file and not directory
        if not os.path.isfile(pdf_path):
            raise ValueError(f"Path is not a file: {pdf_path}")

        # check file is pdf
        if not pdf_path.lower().endswith('.pdf'):
            raise ValueError(f"File is nto a PDF: {pdf_path}")

        results = {}

        if 'pdfplumber' in self.supported_libraries:
            results['pdfplumber'] = self._extract_with_pdfplumber(pdf_path)
       
        if 'PyPDF2' in self.supported_libraries:
            results['PyPDF2'] = self._extract_with_pypdf2(pdf_path)
            
        best_result = self.choose_best_extraction(results)

        processed_result = self._process_extracted_text(best_result['text'])

        return {
            'success': True,
            'text': process_result['text'],
            'sections': processed_result['sections'],
            'skills': processed_result['skills'],
            'contact_info': processed_result['contact_info'],
            'metadata': best_result['metadata']
        }
        
    
    def _extract_with_pypdf2(self, pdf_path: str) -> Dict:
        
       
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            raise Exception(f"PyPDF2 extraction failed: {e}")

    
    def _extract_with_pdfplumber(self, pdf_path: str) -> Dict:
        
        text = ""

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text
        except Exception as e:
            raise Exception(f"pdfplumber extraction failed: {e}")

    def _choose_best_extraction(self, results: Dict) -> Optional[Dict]:
        """
        Choose the best extraction result based on text quality
        
        Args:
            results: Dictionary of extraction results
            
        Returns:
            Best extraction result or None
            
        TODO: Implement this method to:
        1. Score each extraction result based on:
           - Text length
           - Presence of resume keywords (experience, education, skills, work, job, university, degree)
           - Whitespace ratio (penalty if too much whitespace)
        2. Return the result with the highest score
        """

        pass

        best_result = None
        max_length = 0
        # basic for now
        for library, result in results.items():
            length = len(result.get('text', ''))
            if text_length > max_length:
                max_length = text_length
                best_result = result

        return best_result
    
    def _process_extracted_text(self, text: str) -> Dict:
        """
        Process and structure the extracted text
        
        Args:
            text: Raw extracted text
            
        Returns:
            Dictionary with structured text data
            
        TODO: Implement this method to:
        1. Clean the text using _clean_text()
        2. Extract sections using _extract_sections()
        3. Extract skills using _extract_skills()
        4. Extract contact info using _extract_contact_info()
        5. Generate summary using _generate_summary()
        6. Return dictionary with cleaned_text, sections, skills, contact_info, summary
        """
        pass
    
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize the extracted text
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
            
        TODO: Implement this method to:
        1. Remove excessive whitespace using re.sub(r'\s+', ' ', text)
        2. Remove special characters but keep basic punctuation
        3. Remove extra newlines
        4. Return cleaned text
        """
        pass
    
    def _extract_sections(self, text: str) -> Dict:
        """
        Extract different sections from resume text
        
        Args:
            text: Cleaned text
            
        Returns:
            Dictionary with different sections
            
        TODO: Implement this method to:
        1. Define section patterns for experience, education, skills, summary
        2. Split text into lines
        3. Loop through lines and identify section headers
        4. Group content under appropriate sections
        5. Return dictionary with experience, education, skills, summary, other
        """
        pass
    
    def _extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from resume text
        
        Args:
            text: Cleaned text
            
        Returns:
            List of extracted skills
            
        TODO: Implement this method to:
        1. Define regex patterns for common technical skills:
           - Programming languages: python, java, javascript, react, angular, vue, node.js
           - Databases: sql, mysql, postgresql, mongodb, redis
           - Cloud: aws, azure, gcp, docker, kubernetes
           - Data: machine learning, ai, data analysis, data science, statistics
           - Tools: git, github, excel, power bi, tableau
           - Web: html, css, bootstrap, sass
           - Systems: linux, unix, bash, shell scripting
        2. Search text for these patterns
        3. Return list of unique skills found
        """
        pass
    
    def _extract_contact_info(self, text: str) -> Dict:
        """
        Extract contact information from resume text
        
        Args:
            text: Cleaned text
            
        Returns:
            Dictionary with contact information
            
        TODO: Implement this method to:
        1. Extract email using regex pattern for email addresses
        2. Extract phone number using regex pattern for phone numbers
        3. Extract location using regex patterns for city, state
        4. Return dictionary with email, phone, location
        """
        pass
    
    def _generate_summary(self, text: str) -> str:
        """
        Generate a summary of the resume
        
        Args:
            text: Cleaned text
            
        Returns:
            Summary string
            
        TODO: Implement this method to:
        1. Split text into sentences
        2. Take the first few sentences as summary
        3. Return summary string
        """
        pass

def test_pdf_processor():
    """
    Test function for PDF processor
    """
    processor = PDFProcessor()
    
    # Test with your uploaded resume
    pdf_path = "uploads/20250909_142508_992c0d6a_Desmond_Jung_Resume_1.pdf"
    result = processor.extract_text(pdf_path)
    print(result)

    if os.path.exists(pdf_path):
        try:
            result = processor.extract_text(pdf_path)
            print("PDF Processing Results:")
            print(f"Method used: {result['extraction_method']}")
            print(f"Page count: {result['page_count']}")
            print(f"Word count: {result['word_count']}")
            print(f"Character count: {result['character_count']}")
            print("\nExtracted Skills:")
            for skill in result['processed_text']['skills']:
                print(f"  - {skill}")
            print("\nContact Info:")
            for key, value in result['processed_text']['contact_info'].items():
                print(f"  {key}: {value}")
            print("\nFirst 500 characters of text:")
            print(result['raw_text'][:500] + "...")
        except Exception as e:
            print(f"Error processing PDF: {e}")
    else:
        print(f"PDF file not found: {pdf_path}")

if __name__ == "__main__":
    test_pdf_processor()