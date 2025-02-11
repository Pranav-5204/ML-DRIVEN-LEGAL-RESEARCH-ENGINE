import os
import pandas as pd
import fitz
from transformers import pipeline

pdf_dir = r'D:\archive (2)\pdfs'
csv_file = 'court_cases_with_clusters.csv'
df = pd.read_csv(csv_file)

case_names = []
summaries = []

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def preprocess_text(text):
    start_index = text.upper().find('PETITIONER')
    end_index = text.upper().find('DATE OF JUDGMENT')
    
    if start_index != -1 and end_index != -1:
        case_name = text[start_index:end_index].strip()
        case_name = ' '.join(case_name.split())
        return case_name
    return None

def extract_summary(text):
    try:
        max_chunk_size = 1000
        text_chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
        
        summary_text = ""
        for chunk in text_chunks:
            summary = summarizer(chunk, max_length=150, min_length=50, do_sample=False)
            summary_text += summary[0]['summary_text'] + " "
        
        return summary_text.strip()
    
    except Exception as e:
        print(f"Error during summarization: {e}")
        return None

for index, row in df.iterrows():
    case_id = row['Caseid']
    pdf_path = os.path.join(pdf_dir, f"{case_id}.pdf")
    
    if os.path.exists(pdf_path):
        try:
            pdf_document = fitz.open(pdf_path)
            
            text = ''
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text += page.get_text()
            
            case_name = preprocess_text(text)
            case_names.append(case_name)
            
            summary = extract_summary(text)
            summaries.append(summary)
            
            pdf_document.close()
        
        except fitz.EmptyFileError:
            case_names.append(None)
            summaries.append(None)
        except Exception as e:
            case_names.append(None)
            summaries.append(None)
    else:
        case_names.append(None)
        summaries.append(None)

df['casename'] = case_names
df['summary'] = summaries

output_csv_file = 'finalfile4.csv'
df.to_csv(output_csv_file, index=False, quoting=1)

print("Case names and summaries extraction complete. Updated CSV saved.")
