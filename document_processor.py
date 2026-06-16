import pdfplumber
import re
from typing import Dict, Any
import pandas as pd

def extract_info(pdf_path: str) -> Dict[str, Any]:
    """
    Process Real Estate doc (PDF): extract key info.
    Supports lease/invoice.
    """
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        tables = []
        for page in pdf.pages:
            text += page.extract_text() or ''
            table = page.extract_tables()
            if table:
                tables.extend(table)
    
    # Regex for Real Estate docs
    patterns = {
        'tenant': re.findall(r'(?:tenant|lessee|client)[:\\s]*([A-Za-z\\s]+?)(?=\\n|$)', text, re.I),
        'landlord': re.findall(r'(?:landlord|lessor|owner)[:\\s]*([A-Za-z\\s]+?)(?=\\n|$)', text, re.I),
        'rent_amount': re.findall(r'rent[:\\s]*[\\$]?([0-9,]+(?:\\.[0-9]{2})?)', text, re.I),
        'start_date': re.findall(r'(?:start|from)[:\\s]*(\\d{1,2}[/-]\\d{1,2}[/-]\\d{2,4})', text),
        'end_date': re.findall(r'(?:end|to)[:\\s]*(\\d{1,2}[/-]\\d{1,2}[/-]\\d{2,4})', text),
        'property_address': re.findall(r'(?:property|address|unit)[:\\s]*([0-9A-Za-z\\s,.-]+?)(?=\\n{2,}|$)', text),
        'total_amount': re.findall(r'(?:total|amount|due)[:\\s]*[\\$]?([0-9,]+(?:\\.[0-9]{2})?)', text)
    }
    
    result = {k: v[0] if v else None for k, v in patterns.items()}
    
    # Tables to DF (invoices)
    if tables:
        df = pd.concat([pd.DataFrame(t) for t in tables if t], ignore_index=True)
        result['tables'] = df.to_dict('records')
    
    result['full_text'] = text[:500] + '...' if len(text) > 500 else text
    
    return result

# Demo with text sim (for no PDF)
def extract_info_from_text(text: str) -> Dict[str, Any]:
    """
    Extract key info from raw text using the same regex patterns.
    """
    patterns = {
        'tenant': re.findall(r'(?:tenant|lessee|client)[:\\s]*([A-Za-z\\s]+?)(?=\\n|$)', text, re.I),
        'landlord': re.findall(r'(?:landlord|lessor|owner)[:\\s]*([A-Za-z\\s]+?)(?=\\n|$)', text, re.I),
        'rent_amount': re.findall(r'rent[:\\s]*[\\$]?([0-9,]+(?:\\.[0-9]{2})?)', text, re.I),
        'start_date': re.findall(r'(?:start|from)[:\\s]*(\\d{1,2}[/-]\\d{1,2}[/-]\\d{2,4})', text),
        'end_date': re.findall(r'(?:end|to)[:\\s]*(\\d{1,2}[/-]\\d{1,2}[/-]\\d{2,4})', text),
        'property_address': re.findall(r'(?:property|address|unit)[:\\s]*([0-9A-Za-z\\s,.-]+?)(?=\\n{2,}|$)', text),
        'total_amount': re.findall(r'(?:total|amount|due)[:\\s]*[\\$]?([0-9,]+(?:\\.[0-9]{2})?)', text)
    }
    
    result = {k: v[0] if v else None for k, v in patterns.items()}
    result['full_text'] = text[:500] + '...' if len(text) > 500 else text
    return result


def extract_from_text(text: str) -> Dict[str, Any]:
    return extract_info_from_text(text)

if __name__ == "__main__":
    sample_text = """
Lease Agreement
Tenant: John Doe
Landlord: ABC Realty
Property: 123 Main St, Apt 4B
Rent: $1,200 monthly
Start: 01/01/2024
End: 12/31/2024
Total due: $1,200
    """
    print(extract_from_text(sample_text))
