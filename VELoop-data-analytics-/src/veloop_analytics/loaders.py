"""Load every sheet as text (dtype=str) so malformed values are never silently coerced."""
import pandas as pd
from .config import RAW, DATASETS, FILE_A, FILE_B

def load_all(raw_dir=RAW) -> dict[str, pd.DataFrame]:
    books = {f: pd.read_excel(raw_dir / f, sheet_name=None, dtype=str) for f in (FILE_A, FILE_B)}
    out = {name: books[f][sheet] for name, (f, sheet, _) in DATASETS.items()}
    out["A:Data_Dictionary"] = books[FILE_A]["Data_Dictionary"]
    out["B:08_Data_Dictionary"] = books[FILE_B]["08_Data_Dictionary"]
    return out
