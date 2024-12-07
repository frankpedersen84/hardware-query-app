from flask import Flask
from models import db, Workbook, Sheet, Column, Row, Cell

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///excel_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def show_database_contents():
    """Display the contents of the database"""
    with app.app_context():
        # Show workbooks
        workbooks = Workbook.query.all()
        print("\n=== Workbooks ===")
        for wb in workbooks:
            print(f"\nWorkbook: {wb.name}")
            
            # Show sheets in workbook
            for sheet in wb.sheets:
                print(f"\n  Sheet: {sheet.name}")
                print("  Columns:")
                for col in sheet.columns:
                    print(f"    - {col.name} ({col.data_type})")
                
                # Show first 5 rows of data
                print("\n  First 5 rows of data:")
                rows = Row.query.filter_by(sheet_id=sheet.id).limit(5).all()
                for row in rows:
                    row_data = []
                    for cell in row.cells:
                        col_name = cell.column.name
                        value = cell.value
                        row_data.append(f"{col_name}: {value}")
                    print(f"    Row {row.row_index}: {', '.join(row_data)}")

if __name__ == "__main__":
    show_database_contents()
