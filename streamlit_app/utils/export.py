import streamlit as st
import pandas as pd
import io
from datetime import datetime

def export_to_excel(df, filename=None):
    if filename is None:
        filename = f"campaign_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Recommendations', index=False)
        
        try:
            worksheet = writer.sheets['Recommendations']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        except:
            pass
    
    output.seek(0)
    return output, filename

def export_recommendations_to_csv(df, filename=None):
    if filename is None:
        filename = f"campaign_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    csv_data = df.to_csv(index=False)
    return csv_data, filename