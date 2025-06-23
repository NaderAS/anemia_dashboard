# clean_xlsx.py

import pandas as pd
from collections import Counter

def generate_clean_csv(input_file='data.xlsx', output_file='clean_anemia_prevalence.csv'):
    # Load original data
    df = pd.read_excel(input_file)
    
    # Filter only Anaemia prevalence (%)
    anemia_df = df[df['indicator_name'].str.startswith('Anaemia prevalence (%)')]
    
    # Clean columns
    anemia_df.columns = anemia_df.columns.str.strip().str.lower()

    anemia_df = anemia_df[[ 
        'setting', 'date', 'indicator_abbr', 'indicator_name',
        'dimension', 'subgroup', 'estimate',
        'population', 'whoreg6', 'wbincome2024'
    ]]

    anemia_df = anemia_df.rename(columns={
        'setting': 'country',
        'date': 'year',
        'subgroup': 'group',
        'estimate': 'prevalence',
        'whoreg6': 'who_region',
        'wbincome2024': 'income_group'
    })

    # Extract gender
    anemia_df['gender'] = anemia_df['indicator_name'].apply(lambda x: 'Female' if 'female' in x.lower() else 'Male')

    # Keep only countries with Male AND Female data
    gender_counts = anemia_df.groupby('country')['gender'].nunique()
    countries_with_both_genders = gender_counts[gender_counts == 2].index.tolist()
    anemia_df = anemia_df[anemia_df['country'].isin(countries_with_both_genders)]
    print(f"✅ Countries with both genders: {len(countries_with_both_genders)}")

    # Pick most common 5 years
    year_counts = Counter(anemia_df['year'])
    top_5_years = [year for year, count in year_counts.most_common(5)]
    anemia_df = anemia_df[anemia_df['year'].isin(top_5_years)]
    print(f"✅ Most common 5 years: {top_5_years}")

    # Keep only (country + dimension) where both genders exist
    dim_gender_counts = anemia_df.groupby(['country', 'dimension'])['gender'].nunique()
    dims_with_both = dim_gender_counts[dim_gender_counts == 2].reset_index()

    # Merge only country + dimension → avoid gender_x / gender_y bug
    anemia_df = anemia_df.merge(dims_with_both[['country', 'dimension']], on=['country', 'dimension'])

    # Drop year column
    anemia_df = anemia_df.drop(columns=['year'])

    # Save to CSV
    anemia_df.to_csv(output_file, index=False)
    print(f"✅ Clean file saved to: {output_file}")

# To run directly
if __name__ == "__main__":
    generate_clean_csv()
