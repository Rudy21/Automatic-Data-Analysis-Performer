import pandas as pd
from scipy.stats import skew, kurtosis

def generate_descriptive_stats(df):
    """Generates descriptive statistics for numerical columns."""
    numerical_cols = df.select_dtypes(include=['number']).columns
    if len(numerical_cols) == 0:
        return None
        
    stats_list = []
    for col in numerical_cols:
        col_data = df[col]
        stats_list.append({
            "Column": col,
            "Mean": col_data.mean(),
            "Median": col_data.median(),
            "Std Dev": col_data.std(),
            "Min": col_data.min(),
            "Max": col_data.max(),
            "Skewness": skew(col_data, nan_policy='omit'),
            "Kurtosis": kurtosis(col_data, nan_policy='omit')
        })
    
    return pd.DataFrame(stats_list)

def calculate_health_score(df_original, df_cleaned, etl_stats):
    """
    Calculates a 'Data Health Score' out of 100 based on the initial data quality.
    High missing values, duplicates, and outliers lower the score.
    """
    total_cells = df_original.shape[0] * df_original.shape[1]
    total_rows = df_original.shape[0]
    
    if total_cells == 0 or total_rows == 0:
        return 0
        
    missing_penalty = (etl_stats['missing_imputed'] / total_cells) * 40 # Max 40 points penalty
    duplicate_penalty = (etl_stats['duplicates_removed'] / total_rows) * 30 # Max 30 points penalty
    
    # Estimate outlier penalty
    numeric_cells = df_original.select_dtypes(include=['number']).shape[0] * df_original.select_dtypes(include=['number']).shape[1]
    outlier_penalty = 0
    if numeric_cells > 0:
        outlier_penalty = (etl_stats['outliers_handled'] / numeric_cells) * 30 # Max 30 points penalty
        
    score = 100 - (missing_penalty + duplicate_penalty + outlier_penalty)
    return max(0, min(100, round(score, 1)))
