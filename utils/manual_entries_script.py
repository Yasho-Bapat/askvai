import pandas as pd

# List of IDs to be removed
ids_to_remove = [
    "297e0382901c727b01901cfec17f015b",
    "297e0382901c727b01901cfec1c70163",
    "297e0382901c727b0190201a18860230",
    "297e0382901c727b0190201a188a0231",
    "297e0382901c727b0190227d6e6202a2",
    "297e0382901c727b0190227d6e6b02a3",
    "297e0383901730ca01901a6aee9200af",
    "297e0383901730ca01901a6aeea900b2",
    "297e0383901730ca01901a6fc79000ea",
    "297e0383901730ca01901a6fc7be00f0",
    "297e0383901730ca01901a6fc7c500f1",
    "297e0383901730ca01901a6fc7cc00f2",
    "297e0383901730ca01901a6fc7d200f3",
    "297e0383901730ca01901a71b845010b",
    "297e0383901730ca01901a71b860010f",
    "297e0383901730ca01901a7884c0013d",
    "297e0383901730ca01901a7884ce013f",
    "297e0383901730ca01901a854e4401d3",
    "297e0383901730ca01901a854e5c01d4",
    "297e0383901730ca01901a868ed701dd",
    "297e0383901730ca01901a895ea601ff",
    "297e0383901730ca01901a895ed10200",
    "297e0383901730ca01901aa264e502f3",
    "297e0383901730ca01901aa264e902f4",
    "297e0383901730ca01901ac16907044a",
    "297e0383901730ca01901b4523e4092c",
    "297e0383901730ca01901b4523e9092d",
    "297e0383901730ca01901b4523f0092e",
    "297e0383901730ca01901b4d5ee8096e",
    "297e0383901730ca01901b4d5efe0970",
    "297e0383901730ca01901b52207d0998",
    "297e0383901730ca01901b5220820999",
    "297e0383901730ca01901b6cf6c10a81",
    "297e0383901730ca01901b6cf6c50a82",
    "297e0383901730ca01901b7503730ad2",
    "297e0383901730ca01901b98aae00bc7",
    "297e0383901730ca01901b98aae30bc8",
    "297e0383901730ca01901bcd7a0c0d46",
    "297e0383901730ca01901bcd7a110d47",
    "297e0383901730ca01901bcd7a220d49"
]

# Load the Excel file
file_path = 'askVAI_experiment.xlsx'  # Replace with the path to your file
xls = pd.ExcelFile(file_path)

# Define the sheet names you want to process
sheet_names = ['with_manufacturer_info', 'without_manufacturer_info']  # Replace with the sheet names you want to process

# Create a dictionary to hold the filtered DataFrames
filtered_sheets = {}

# Process each specified sheet
for sheet_name in sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet_name)

    # Filter out the rows with matching IDs
    filtered_df = df[~df['material_id'].isin(ids_to_remove)]

    # Add the filtered DataFrame to the dictionary
    filtered_sheets[sheet_name] = filtered_df

# Save the filtered DataFrames back to a new Excel file
with pd.ExcelWriter('filtered_file.xlsx') as writer:
    for sheet_name, filtered_df in filtered_sheets.items():
        filtered_df.to_excel(writer, sheet_name=sheet_name, index=False)

print("Rows with specified IDs have been removed and the new file has been saved as 'filtered_file.xlsx'.")
