import pandas as pd
import re

def classify_sheet_by_content(df):
    """
    Classify a sheet based on the occurrences of specific row labels or keywords in cells.
    Returns:
        list: list of strings containing matches from ['BS', 'PL', 'Gearing', 'Mitra', 'CF', 'HUW'] or ['unknown']
    """
    # Convert all string cells in the first few columns to normalized lowercase
    text_content = []
    # Scan up to first 4 columns, since description is usually in the first columns
    max_cols = min(df.shape[1], 4)
    for col_idx in range(max_cols):
        col_vals = df.iloc[:, col_idx].dropna().astype(str).str.lower().str.strip()
        text_content.extend(col_vals.tolist())
    
    # Clean up text content to set of strings
    text_set = {re.sub(r'\s+', ' ', s) for s in text_content}
    
    # Keywords definitions
    bs_keywords = {
        'kas dan bank', 'kas dan giro bank', 'piutang imbal jasa kafalah', 
        'piutang tawidh', "piutang ta'widh", 'aset tetap', 'jumlah aset', 
        'total aset', 'jumlah liabilitas', 'total liabilitas', 'jumlah ekuitas', 
        'total ekuitas', 'cadangan klaim', 'estimasi tawidh retensi sendiri',
        'deposito berjangka mudharabah', 'deposito pada bank', 'reksa dana syariah'
    }
    
    pl_keywords = {
        'imbal jasa kafalah bruto', 'beban penjaminan ulang', 'tawidh bruto', 
        "ta'widh bruto", 'laba setelah pajak', 'laba tahun berjalan', 
        'jumlah pendapatan kafalah', 'pendapatan underwriting', 'beban kafalah', 
        'hasil underwriting neto', 'laba sebelum pajak', 'laba usaha',
        'pendapatan jasa penjaminan (ijk)', 'hasil investasi'
    }
    
    gearing_keywords = {
        'nilai penjaminan ditanggung sendiri', 'modal sendiri bersih', 
        'gearing ratio', 'gearing ratio (nilai baris 1:2)', 'gearing ratio aktual'
    }
    
    cf_keywords = {
        'arus kas dari aktivitas', 'kas bersih', 'arus kas bersih', 'aktivitas operasi',
        'aktivitas investasi', 'aktivitas pendanaan', 'arus kas', 'posisi arus kas', 'posisi arus kas (cashflow)'
    }
    
    huw_keywords = {
        'hasil underwriting', 'mikro pnm', 'kur mikro', 'retail & korporasi', 
        'kur super mikro'
    }
    
    # Check matches count
    bs_matches = len(bs_keywords.intersection(text_set))
    pl_matches = len(pl_keywords.intersection(text_set))
    gearing_matches = any(k in text_set for k in gearing_keywords)
    cf_matches = any(k in s for s in text_set for k in cf_keywords)
    huw_matches = len(huw_keywords.intersection(text_set))
    mitra_matches = any(k in s for s in text_set for k in ['mitra', 'plafon'])
    
    results = []
    if bs_matches >= 3:
        results.append('BS')
    if pl_matches >= 3:
        results.append('PL')
    if gearing_matches:
        results.append('Gearing')
    if cf_matches:
        results.append('CF')
    if huw_matches >= 2:
        results.append('HUW')
    if any(x in text_set for x in ['plafon penjaminan per mitra', 'plafon penjaminan', 'plafon mitra']) or (mitra_matches and any('plafon' in x for x in text_set)):
        results.append('Mitra')
        
    if not results:
        return ['unknown']
    return results

def detect_excel_type(file_path):
    """
    Detect the type of JPAS Excel file uploaded based on its sheet names and cell contents.
    Returns:
        str: 'worksheet_financial' | 'evaluasi_anper' | 'rekapan_kafalah' | 'unknown'
    """
    try:
        xl = pd.ExcelFile(file_path)
        sheets = xl.sheet_names
        
        # 1. Strict Sheet Name Keyword Check
        if any('Summary PL KONSOL' in s for s in sheets) or any('Summary BS KONSOL' in s for s in sheets):
            return 'worksheet_financial'
        elif any('Input PL' in s for s in sheets) or any('Input BS' in s for s in sheets):
            return 'evaluasi_anper'
        elif any('plafond' in s for s in sheets) or any('pivot 1' in s for s in sheets):
            return 'rekapan_kafalah'
            
        # 2. Content-Based Classification Fallback (scan up to first few sheets)
        found_types = set()
        for sheet in sheets[:5]:
            df = xl.parse(sheet, nrows=50)
            stypes = classify_sheet_by_content(df)
            if isinstance(stypes, str):
                stypes = [stypes]
            for stype in stypes:
                if stype != 'unknown':
                    found_types.add(stype)
                
        if 'BS' in found_types and 'PL' in found_types:
            return 'worksheet_financial'
        elif 'BS' in found_types or 'PL' in found_types:
            # If at least BS or PL is found (like in Rasio Likuiditas 2026.xlsx which has BS)
            return 'worksheet_financial'
        elif 'Gearing' in found_types:
            return 'evaluasi_anper'
        elif 'Mitra' in found_types:
            return 'rekapan_kafalah'
            
        # 3. Fallback check on sheet names containing Plafon/Kafalah
        if any('plafon' in s.lower() or 'mitra' in s.lower() for s in sheets):
            return 'worksheet_financial'
            
        return 'unknown'
    except Exception as e:
        print(f"Error detecting file type: {e}")
        return 'unknown'

