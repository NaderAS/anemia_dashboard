import pandas as pd

# === Load the data ===
file_path = 'data.xlsx'
df = pd.read_excel(file_path)

# === Filter for Anaemia-related indicators (case-insensitive) ===
anemia_df = df[df['indicator_name'].str.contains('anaemia prevalence', case=False, na=False)]

# === Preview the filtered data ===
print("Shape:", anemia_df.shape)
print(anemia_df[['setting', 'date', 'indicator_abbr', 'indicator_name', 'dimension', 'subgroup', 'estimate']].head())
