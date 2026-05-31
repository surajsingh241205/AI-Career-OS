from PyPDF2 import PdfReader
from docx import Document 

def extract_text(file_path):
    text = ""
    
    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        
        for page in reader.pages:
            page_text = page.extract_text() 
            
            if page_text:
                text += page_text + "\n"
    
    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text
            