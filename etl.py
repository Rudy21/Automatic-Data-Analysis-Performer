import pandas as pd
import numpy as np

def load_data(uploaded_file):
    """Loads CSV or Excel data into a Pandas DataFrame."""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(uploaded_file)
        else:
            return None, "Unsupported file format."
        return df, None
    except Exception as e:
        return None, str(e)

def perform_etl(df):
    """
    Performs autonomous ETL:
    - Impute missing values
    - Convert data types (strings to datetime where applicable)
    - Remove duplicates
    """
    # 1. Remove duplicates
    initial_rows = len(df)
    df = df.drop_duplicates()
    duplicates_removed = initial_rows - len(df)
    
    # 2. Convert to datetime if applicable
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                # Attempt to convert to datetime
                df[col] = pd.to_datetime(df[col], errors='ignore')
            except Exception:
                pass
                
    # 3. Impute missing values
    missing_imputed = 0
    for col in df.columns:
        if df[col].isnull().sum() > 0:
            missing_imputed += df[col].isnull().sum()
            if pd.api.types.is_numeric_dtype(df[col]):
                # Impute with median for numerical
                df[col] = df[col].fillna(df[col].median())
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else pd.NaT)
            else:
                # Impute with mode for categorical
                df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'Missing')

    # We could also handle outliers here, but might be better for an advanced step
    # Let's do simple winsorization or capping for numeric columns
    outliers_handled = 0
    for col in df.select_dtypes(include=[np.number]).columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        # Count outliers
        outliers_count = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
        outliers_handled += outliers_count
        
        # Cap outliers
        df[col] = np.where(df[col] < lower_bound, lower_bound, df[col])
        df[col] = np.where(df[col] > upper_bound, upper_bound, df[col])

    etl_stats = {
        "duplicates_removed": duplicates_removed,
        "missing_imputed": missing_imputed,
        "outliers_handled": outliers_handled
    }

    return df, etl_stats
