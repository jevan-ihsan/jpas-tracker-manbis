import pandas as pd

def detect_excel_type(file_path):
    """
    Detect the type of JPAS Excel file uploaded based on its sheet names.
    Returns:
        str: 'worksheet_financial' | 'evaluasi_anper' | 'rekapan_kafalah' | 'unknown'
    """
    try:
        xl = pd.ExcelFile(file_path)
        sheets = xl.sheet_names
        
        # Check sheet name signatures
        if any('Summary PL KONSOL' in s for s in sheets) or any('Summary BS KONSOL' in s for s in sheets):
            return 'worksheet_financial'
        elif any('Input PL' in s for s in sheets) or any('Input BS' in s for s in sheets):
            return 'evaluasi_anper'
        elif any('plafond' in s for s in sheets) or any('pivot 1' in s for s in sheets):
            return 'rekapan_kafalah'
        else:
            # Fallback check on sheet names containing Plafon/Kafalah
            if any('plafon' in s.lower() or 'mitra' in s.lower() for s in sheets):
                return 'worksheet_financial'
            return 'unknown'
    except Exception as e:
        print(f"Error detecting file type: {e}")
        return 'unknown'
