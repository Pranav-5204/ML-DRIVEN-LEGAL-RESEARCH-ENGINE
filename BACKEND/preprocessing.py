import os
import pandas as pd
import fitz  # PyMuPDF


pdf_dir = r'D:\archive (2)\pdfs' 


case_ids = []
contents = []

def preprocess_text(text):
    """Preprocess text to include only content after 'JUDGEMENT'."""
    start_index = text.upper().find('HEADNOTE')
    if start_index != -1:
        # Extract content after 'JUDGEMENT'
        content = text[start_index:].strip()
        # Replace excessive newlines and spaces
        content = ' '.join(content.split())
        return content
    return None


for filename in os.listdir(pdf_dir):
    if filename.endswith('.pdf'):
        case_id = os.path.splitext(filename)[0]  
        
        
        pdf_path = os.path.join(pdf_dir, filename)
        
        try:
            # Open the PDF file
            pdf_document = fitz.open(pdf_path)
            
    
            text = ''
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text += page.get_text()
            
     
            preprocessed_text = preprocess_text(text)
            
            if preprocessed_text:

                case_ids.append(case_id)
                contents.append(preprocessed_text)
            

            pdf_document.close()
        
        except fitz.EmptyFileError:
            print(f"Skipping empty file: {pdf_path}")
        except Exception as e:
            print(f"Error processing file {pdf_path}: {e}")

df = pd.DataFrame({
    'Caseid': case_ids,
    'content': contents
})

df.to_csv('supreme_court_cases4.csv', index=False, quoting=1) 
