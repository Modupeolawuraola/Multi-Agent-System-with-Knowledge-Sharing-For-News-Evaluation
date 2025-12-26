"""
Clean the fact-checking test dataset - remove NaN ratings
"""
import pandas as pd

print("="*60)
print("CLEANING FACT-CHECKING TEST DATASET")
print("="*60)

# Read the messy file
df = pd.read_csv('test_dataset/fact_check_test.tsv', sep='\t', encoding='utf-8')

print(f"\nOriginal dataset: {len(df)} rows")
print(f"Columns: {df.columns.tolist()}")

# Check for issues
nan_count = df['rating'].isna().sum()
print(f"\nRows with NaN/empty rating: {nan_count}")

if nan_count > 0:
    print("\nFirst 5 problematic rows:")
    problematic = df[df['rating'].isna()]
    for idx, row in problematic.head(5).iterrows():
        print(f"  Row {idx+2}: {row['claim'][:60]}...")

# Clean the data
print("\nCleaning...")

# Remove rows with NaN ratings
df_clean = df[df['rating'].notna()].copy()

# Normalize ratings (remove extra spaces, capitalize)
df_clean['rating'] = df_clean['rating'].astype(str).str.strip().str.capitalize()

# Keep only valid ratings
valid_ratings = ['False', 'True', 'Misleading']
df_clean = df_clean[df_clean['rating'].isin(valid_ratings)]

print(f"\n✅ Cleaned dataset: {len(df_clean)} rows")
print(f"📊 Removed: {len(df) - len(df_clean)} rows with invalid ratings")

# Show rating distribution
print("\nRating distribution:")
print(df_clean['rating'].value_counts())

# Save cleaned version
output_path = 'test_dataset/fact_check_test_CLEAN.tsv'
df_clean.to_csv(output_path, sep='\t', index=False)

print(f"\n{'='*60}")
print(f"✅ SAVED: {output_path}")
print(f"✅ Ready to process {len(df_clean)} clean claims!")
print(f"{'='*60}")