import pandas as pd

def filter_excel_data(data_dir, in_file, out_file):
    # Construct full path to the input file
    in_path = f"{data_dir}/{in_file}"
    
    # Read the Excel file
    df = pd.read_excel(in_path)
    
    # Filter the DataFrame
    df = df[df['Item Name'].str.startswith('Sample')]

    # Construct full path to the output file
    out_path = f"{data_dir}/{out_file}"

    # Write the DataFrame back to Excel
    df.to_excel(out_path, index=False)

# Use the function
data_dir = r"C:\Users\marci\OneDrive\silkresource\data06"
in_file = "orders-2023-06-08-13-07-17.xlsx"
out_file = "sample-orders-2023-06-08-13-07-17.xlsx"

filter_excel_data(data_dir, in_file, out_file)
