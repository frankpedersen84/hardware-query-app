import pandas as pd

def check_excel():
    try:
        df = pd.read_excel('hardware_data.xlsx')
        print("\nFirst few rows:")
        print(df.head())
        print("\nColumns:", list(df.columns))
        print("\nTotal rows:", len(df))
    except Exception as e:
        print(f"Error reading Excel file: {str(e)}")

if __name__ == "__main__":
    check_excel()
