import os
import pandas as pd
import fitz  # PyMuPDF

# Directory where PDF files are stored
pdf_dir = r'D:\archive (2)\pdfs'  # Use raw string to avoid escape sequence issue

# Load the existing CSV file
csv_file = 'court_cases_with_clusters.csv'  # Update with your CSV file path
df = pd.read_csv(csv_file)

# Lists to hold case names and summaries
case_names = []
summaries = []

def preprocess_text(text):
    """Extract content between 'PETITIONER' and 'DATE OF JUDGMENT'."""
    start_index = text.upper().find('PETITIONER')
    end_index = text.upper().find('DATE OF JUDGMENT')
    
    if start_index != -1 and end_index != -1:
        # Extract content between the two keywords
        case_name = text[start_index:end_index].strip()
        # Replace excessive newlines and spaces
        case_name = ' '.join(case_name.split())
        return case_name
    return None

def extract_summary(text):
    """Extract at least 50 words from the end of the text, starting at a new sentence."""
    # Split text into sentences
    sentences = text.split('. ')
    
    # Filter out empty sentences
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    
    # If there are no sentences, return None
    if not sentences:
        return None
    
    # Start from the end and collect sentences until we reach at least 50 words
    summary = []
    word_count = 0
    
    # Iterate backwards through the sentences
    for sentence in reversed(sentences):
        summary.append(sentence)
        word_count += len(sentence.split())
        
        # Break if we have at least 50 words
        if word_count >= 50:
            break
    
    # Reverse the summary to maintain the original order and join into a single string
    return '. '.join(reversed(summary)).strip() + ('.' if summary else '')

# Iterate through each row in the DataFrame
for index, row in df.iterrows():
    case_id = row['Caseid']  # Get the case ID from the DataFrame
    pdf_path = os.path.join(pdf_dir, f"{case_id}.pdf")  # Construct the PDF file path
    
    if os.path.exists(pdf_path):  # Check if the PDF file exists
        try:
            # Open the PDF file
            pdf_document = fitz.open(pdf_path)
            
            # Extract text from each page of the PDF
            text = ''
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text += page.get_text()
            
            # Preprocess text to extract case name
            case_name = preprocess_text(text)
            case_names.append(case_name)  # Append the case name to the list
            
            # Extract summary
            summary = extract_summary(text)
            summaries.append(summary)  # Append the summary to the list
            
            # Close the PDF document
            pdf_document.close()
        
        except fitz.EmptyFileError:
            print(f"Skipping empty file: {pdf_path}")
            case_names.append(None)  # Append None for empty files
            summaries.append(None)  # Append None for empty files
        except Exception as e:
            print(f"Error processing file {pdf_path}: {e}")
            case_names.append(None)  # Append None for errors
            summaries.append(None)  # Append None for errors
    else:
        print(f"PDF file not found for case ID: {case_id}")
        case_names.append(None)  # Append None if PDF doesn't exist
        summaries.append(None)  # Append None if PDF doesn't exist

# Add the case names and summaries to the DataFrame
df['casename'] = case_names
df['summary'] = summaries

# Save the updated DataFrame to a new CSV file
output_csv_file = 'finalfile4.csv'  # Update with your desired output path
df.to_csv(output_csv_file, index=False, quoting=1)  # quoting=1 to ensure text with commas is properly quoted

print("Case names and summaries extraction complete. Updated CSV saved.")
