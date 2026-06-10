import io
import PyPDF2
import docx

async def extract_text_from_file(filename: str, content: bytes) -> str:
    """Parses text from various file formats for the debate context."""
    text = ""
    
    try:
        if filename.endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
                
        elif filename.endswith(".docx"):
            doc = docx.Document(io.BytesIO(content))
            for para in doc.paragraphs:
                text += para.text + "\n"
                
        elif filename.endswith(".txt"):
            text = content.decode("utf-8")
            
        else:
            raise ValueError("Unsupported file format. Please upload PDF, DOCX, or TXT.")
            
        # Clean up whitespace for the LLM
        return " ".join(text.split())[:15000] # Cap at 15k chars to save Groq tokens

    except Exception as e:
        raise ValueError(f"Failed to parse file: {str(e)}")