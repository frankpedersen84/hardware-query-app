from flask import Flask
from models import db, Workbook, Sheet, Column, Row, Cell
import pandas as pd
from pathlib import Path

# Create Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///excel_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

def load_excel_to_db(file_path):
    """
    Load an Excel file into the database
    
    Args:
        file_path (str): Path to the Excel file
    """
    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()
        
        try:
            # Load Excel file
            excel_file = pd.ExcelFile(file_path)
            workbook_name = Path(file_path).name
            
            print(f"Loading workbook: {workbook_name}")
            
            # Create workbook record
            workbook = Workbook(name=workbook_name)
            db.session.add(workbook)
            db.session.flush()
            
            # Process each sheet
            for sheet_name in excel_file.sheet_names:
                print(f"Processing sheet: {sheet_name}")
                df = pd.read_excel(excel_file, sheet_name)
                
                # Create sheet record
                sheet = Sheet(name=sheet_name, workbook_id=workbook.id)
                db.session.add(sheet)
                db.session.flush()
                
                # Create columns
                column_objects = {}
                for col_name in df.columns:
                    data_type = str(df[col_name].dtype)
                    column = Column(name=col_name, data_type=data_type, sheet_id=sheet.id)
                    db.session.add(column)
                    db.session.flush()
                    column_objects[col_name] = column
                
                # Create rows and cells (using batch processing)
                batch_size = 1000
                total_rows = len(df)
                
                for start_idx in range(0, total_rows, batch_size):
                    end_idx = min(start_idx + batch_size, total_rows)
                    print(f"Processing rows {start_idx} to {end_idx} of {total_rows}")
                    
                    batch_df = df.iloc[start_idx:end_idx]
                    
                    for idx, row_data in batch_df.iterrows():
                        row = Row(row_index=idx, sheet_id=sheet.id)
                        db.session.add(row)
                        db.session.flush()
                        
                        # Add cells for this row
                        for col_name, value in row_data.items():
                            cell = Cell(
                                value=str(value) if pd.notna(value) else None,
                                row_id=row.id,
                                column_id=column_objects[col_name].id
                            )
                            db.session.add(cell)
                    
                    # Commit each batch
                    db.session.commit()
            
            print("Excel file successfully loaded into database!")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error loading workbook: {str(e)}")
            return False

if __name__ == "__main__":
    # Replace this with your Excel file path
    excel_file_path = input("Enter the path to your Excel file: ")
    load_excel_to_db(excel_file_path)
