import pandas as pd
from datetime import datetime
import numpy as np
import os

# Data
CLONE_PATH = '/opt/airflow/repo'  # Use the path from the airflow workflow
ticket_details_path = os.path.join(CLONE_PATH,"Ticket Details.xlsx")
device_list_path = os.path.join(CLONE_PATH,"Device List.xlsx")
ticket_details_df = pd.read_excel(ticket_details_path, sheet_name='Sheet1', engine='openpyxl')
device_list_df = pd.read_excel(device_list_path, sheet_name='Sheet1', engine='openpyxl')

# Define the cutoff date for filtering (past 5 years)
cutoff_date = datetime(2019, 1, 1)
current_date = datetime.today()

# Ticket Details Dataset

ticket_details_df['CreatedDate'] = pd.to_datetime(ticket_details_df['CreatedDate'], errors='coerce')
ticket_details_df['SolvedAtDate'] = pd.to_datetime(ticket_details_df['SolvedAtDate'], errors='coerce')

ticket_details_df = ticket_details_df[ticket_details_df['CreatedDate'] >= cutoff_date]

ticket_details_df['SolvedAtDate'].fillna(pd.NaT, inplace=True)

ticket_details_df['Days To Resolve'] = (ticket_details_df['SolvedAtDate'] - ticket_details_df['CreatedDate']).dt.days

ticket_details_df['Days To Resolve Bucket'] = ticket_details_df['Days To Resolve'].apply(
    lambda x: "Unresolved" if pd.isna(x) else "+15 days" if x > 15 else f"{x} days"
)

ticket_details_df.dropna(subset=['TransactionNumber', 'CreatedDate', 'CategoryLevel1'], how='all', inplace=True)

for col in ['FixFlag', 'RecordType', 'OOBOrNot', 'OOBStatus']:
    ticket_details_df[col] = ticket_details_df[col].astype(str).str.strip().str.upper()

ticket_details_df.sort_values(by=['TransactionNumber', 'CreatedDate'], ascending=[True, False], inplace=True)
ticket_details_df.drop_duplicates(subset=['TransactionNumber'], keep='first', inplace=True)

ticket_details_df[['CategoryLevel1', 'CategoryLevel2Alias', 'CategoryLevel3', 'CategoryLevel4']] = \
    ticket_details_df[['CategoryLevel1', 'CategoryLevel2Alias', 'CategoryLevel3', 'CategoryLevel4']].apply(lambda x: x.str.strip().str.upper())

ticket_details_df['ProductKey'] = ticket_details_df['ProductKey'].astype(str).str.strip().str.upper()
ticket_details_df['DeviceAlias'] = ticket_details_df['DeviceAlias'].astype(str).str.strip().str.upper()

# Device List Dataset

device_list_df['Estimated Installation Date'] = pd.to_datetime(device_list_df['Estimated Installation Date'], errors='coerce')

device_list_df = device_list_df[
    (device_list_df['Estimated Installation Date'] <= current_date) &
    (device_list_df['Estimated Installation Date'] > datetime(1900, 1, 1))
]

device_list_df.sort_values(by=['ProductKey', 'DeviceAlias', 'Estimated Installation Date'], ascending=[True, True, True], inplace=True)
device_list_df.drop_duplicates(subset=['ProductKey', 'DeviceAlias'], keep='first', inplace=True)

device_list_df['ProductKey'] = device_list_df['ProductKey'].astype(str).str.strip().str.upper()
device_list_df['DeviceAlias'] = device_list_df['DeviceAlias'].astype(str).str.strip().str.upper()

device_list_df['Device Age'] = (datetime(2024, 2, 1) - device_list_df['Estimated Installation Date']).dt.days // 365

merged_df = pd.merge(ticket_details_df, device_list_df, on=['ProductKey', 'DeviceAlias'], how='left')

column_mapping = {
    "TransactionNumber": "transaction_number",
    "ProductKey": "product_key",
    "DeviceAlias": "device_alias",
    "FixFlag": "fix_flag",
    "RecordType": "record_type",
    "OOBOrNot": "oob_or_not",
    "OOBStatus": "oob_status",
    "CreatedDate": "created_date",
    "SolvedAtDate": "solved_at_date",
    "Days To Resolve": "days_to_resolve",
    "Days To Resolve Bucket": "days_to_resolve_bucket",
    "CategoryLevel1": "category_level1",
    "CategoryLevel2Alias": "category_level2",
    "CategoryLevel3": "category_level3",
    "CategoryLevel4": "category_level4",
    "Estimated Installation Date": "estimated_installation_date",
    "Device Age": "device_age"
}

merged_df.rename(columns=column_mapping, inplace=True)

merged_df = merged_df[list(column_mapping.values())]

merged_df = merged_df.dropna(subset=["days_to_resolve", "device_age"])

def sanitize_integer(value, min_val=0, max_val=365):  
    if pd.isna(value) or value in [np.nan, np.inf, -np.inf, "NaN", "INF"]:  
        return None
    try:
        num = int(float(value))
        return min(max(num, min_val), max_val)
    except:
        return None  

integer_columns = ["device_age", "days_to_resolve"]
for col in integer_columns:
    if col in merged_df.columns:
        merged_df[col] = merged_df[col].apply(sanitize_integer)

merged_data_path = "Cleaned_Merged_Data.csv"
merged_df.to_csv(merged_data_path, index=False)

print("Data cleaning and merging complete. File saved as Cleaned_Merged_Data.csv")
