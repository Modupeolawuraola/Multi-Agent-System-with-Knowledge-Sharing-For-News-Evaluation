import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter

# Set style for publications
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("Set2")


# Function to analyze the fact-check dataset before and after normalization
def analyze_factcheck_dataset(file_path):
    # Load the TSV file
    df = pd.read_csv(file_path, sep='\t')

    # Print initial column information
    print(f"\nColumns in {file_path}: {df.columns.tolist()}")
    print(f"First few rows of the dataset:\n{df.head()}")

    # Create figure for before and after comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Before normalization - show all values including NaN
    print("\nLabel Distribution Before Data Pre-processing:")
    label_counts_before = df['rating'].value_counts(dropna=False)
    print(label_counts_before)

    # Handle NaN values for plotting
    label_counts_before_plot = label_counts_before.fillna(0)
    labels_before = [str(x) if pd.notna(x) else 'Missing' for x in label_counts_before.index]

    colors = plt.cm.Set2(np.linspace(0, 1, len(label_counts_before_plot)))

    # Bar plot before normalization
    bars1 = ax1.bar(labels_before, label_counts_before_plot.values,
                    color=colors, edgecolor='black', alpha=0.8)
    ax1.set_title('Fact-Check Ratings Distribution\n(Before Data Pre-processing)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Rating', fontsize=12)
    ax1.set_ylabel('Count', fontsize=12)
    ax1.set_ylim(0, max(label_counts_before_plot.values) * 1.1)
    ax1.tick_params(axis='x', rotation=45)

    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2., height,
                 f'{int(height)}', ha='center', va='bottom', fontsize=11)

    # After normalization - drop NaN and 'misleading' if present
    df_normalized = df.dropna(subset=['rating']).copy()
    if 'misleading' in df_normalized['rating'].str.lower().unique():
        df_normalized = df_normalized[df_normalized['rating'].str.lower() != 'misleading']

    print("\nLabel Distribution After Data Pre-processing:")
    label_counts_after = df_normalized['rating'].value_counts()
    print(label_counts_after)

    # Bar plot after normalization
    colors_after = plt.cm.Set2(np.linspace(0, 1, len(label_counts_after)))
    bars2 = ax2.bar(label_counts_after.index, label_counts_after.values,
                    color=colors_after, edgecolor='black', alpha=0.8)
    ax2.set_title('Fact-Check Ratings Distribution\n(After Data Pre-processing)', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Rating', fontsize=12)
    ax2.set_ylabel('Count', fontsize=12)
    ax2.set_ylim(0, max(label_counts_after.values) * 1.1)
    ax2.tick_params(axis='x', rotation=45)

    # Add value labels on bars
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2., height,
                 f'{int(height)}', ha='center', va='bottom', fontsize=11)

    plt.tight_layout()
    plt.savefig('fact_check_Pre-processing_comparison.pdf', dpi=300, format='pdf', bbox_inches='tight')
    plt.close()

    # Create summary table
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    # Combine before and after data
    summary_data = []
    labels_set = set(labels_before + list(label_counts_after.index))

    for label in labels_set:
        count_before = label_counts_before_plot.get(label if label != 'Missing' else np.nan, 0)
        count_after = label_counts_after.get(label, 0) if label != 'Missing' else 0

        percentage_before = (count_before / len(df)) * 100 if len(df) > 0 else 0
        percentage_after = (count_after / len(df_normalized)) * 100 if len(df_normalized) > 0 else 0

        summary_data.append([
            label,
            f"{int(count_before)} ({percentage_before:.1f}%)",
            f"{int(count_after)} ({percentage_after:.1f}%)"
        ])

    # Sort summary data by label
    summary_data.sort(key=lambda x: x[0])

    table = ax.table(cellText=summary_data,
                     colLabels=['Rating', 'Before Data Pre-processing', 'After Data Pre-processing'],
                     cellLoc='center',
                     loc='center',
                     colWidths=[0.3, 0.35, 0.35])

    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.5)

    ax.axis('off')
    ax.set_title('Fact-Check Dataset Pre-processing Summary', fontsize=16, fontweight='bold', pad=20)

    plt.savefig('fact_check_Pre-processing_table.pdf', dpi=300, format='pdf', bbox_inches='tight')
    plt.close()

    return df_normalized


# Function to analyze the bias dataset before and after normalization
def analyze_bias_dataset(file_path):
    # Load the CSV file
    df = pd.read_csv(file_path)

    # Print initial column information
    print(f"\nColumns in {file_path}: {df.columns.tolist()}")
    print(f"First few rows of the dataset:\n{df.head()}")

    # Create figure for before and after comparison (vertical bar charts only)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Before pre-processing
    print("\nBias Distribution Before  Data Pre-processing:")
    bias_counts_before = df['bias'].value_counts()
    print(bias_counts_before)

    colors_before = sns.color_palette("husl", len(bias_counts_before))

    # Bar plot before normalization
    bars1 = ax1.bar(range(len(bias_counts_before)), bias_counts_before.values,
                    color=colors_before, edgecolor='black', alpha=0.8)
    ax1.set_xticks(range(len(bias_counts_before)))
    ax1.set_xticklabels(bias_counts_before.index, rotation=45, ha='right')
    ax1.set_title('Media Bias Distribution\n(Before Data Pre-processing)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Bias Category', fontsize=12)
    ax1.set_ylabel('Count', fontsize=12)
    ax1.set_ylim(0, max(bias_counts_before.values) * 1.1)

    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2., height,
                 f'{int(height)}', ha='center', va='bottom', fontsize=11)

    # After normalization - merge Lean Left and Left
    df_normalized = df.copy()
    df_normalized['bias'] = df_normalized['bias'].replace('Lean Left', 'Left')

    print("\nBias Distribution After Data Pre-processing:")
    bias_counts_after = df_normalized['bias'].value_counts()
    print(bias_counts_after)

    colors_after = sns.color_palette("husl", len(bias_counts_after))

    # Bar plot after normalization
    bars2 = ax2.bar(range(len(bias_counts_after)), bias_counts_after.values,
                    color=colors_after, edgecolor='black', alpha=0.8)
    ax2.set_xticks(range(len(bias_counts_after)))
    ax2.set_xticklabels(bias_counts_after.index, rotation=45, ha='right')
    ax2.set_title('Media Bias Distribution\n(After Data Pre-processing)', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Bias Category', fontsize=12)
    ax2.set_ylabel('Count', fontsize=12)
    ax2.set_ylim(0, max(bias_counts_after.values) * 1.1)

    # Add value labels on bars
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2., height,
                 f'{int(height)}', ha='center', va='bottom', fontsize=11)

    plt.tight_layout()
    plt.savefig('bias_pre-processing_comparison.pdf', dpi=300, format='pdf', bbox_inches='tight')
    plt.close()

    # Create summary table
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    # Combine before and after data
    summary_data = []
    bias_categories = list(set(bias_counts_before.index) | set(bias_counts_after.index))

    for category in bias_categories:
        count_before = bias_counts_before.get(category, 0)
        count_after = bias_counts_after.get(category, 0)

        percentage_before = (count_before / len(df)) * 100 if len(df) > 0 else 0
        percentage_after = (count_after / len(df_normalized)) * 100 if len(df_normalized) > 0 else 0

        summary_data.append([
            category,
            f"{int(count_before)} ({percentage_before:.1f}%)",
            f"{int(count_after)} ({percentage_after:.1f}%)"
        ])

    # Sort summary data by category
    summary_data.sort(key=lambda x: x[0])

    table = ax.table(cellText=summary_data,
                     colLabels=['Bias Category', 'Before Pre-processing', 'After Pre-processing'],
                     cellLoc='center',
                     loc='center',
                     colWidths=[0.3, 0.35, 0.35])

    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.5)

    ax.axis('off')
    ax.set_title('Media Bias Dataset Pre-processing Summary', fontsize=16, fontweight='bold', pad=20)

    plt.savefig('bias_Pre-processing_table.pdf', dpi=300, format='pdf', bbox_inches='tight')
    plt.close()

    return df_normalized


# Function to create final comparative visualization
def create_final_comparison(fact_check_df, bias_df):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # Fact-check final distribution
    rating_counts = fact_check_df['rating'].value_counts()
    colors_fact = plt.cm.Set2(np.linspace(0, 1, len(rating_counts)))

    bars1 = ax1.bar(rating_counts.index, rating_counts.values,
                    color=colors_fact, edgecolor='black', alpha=0.8)
    ax1.set_title('Fact-Check Dataset (After Pre-processing)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Count', fontsize=12)
    ax1.tick_params(axis='x', rotation=45)

    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2., height,
                 f'{int(height)}', ha='center', va='bottom', fontsize=11)

    # Bias final distribution
    bias_counts = bias_df['bias'].value_counts()
    colors_bias = sns.color_palette("husl", len(bias_counts))

    bars2 = ax2.bar(range(len(bias_counts)), bias_counts.values,
                    color=colors_bias, edgecolor='black', alpha=0.8)
    ax2.set_xticks(range(len(bias_counts)))
    ax2.set_xticklabels(bias_counts.index, rotation=45, ha='right')
    ax2.set_title('Media Bias Dataset (After Pre-processing)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Count', fontsize=12)

    # Add value labels
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2., height,
                 f'{int(height)}', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig('Pre-processing_datasets_final_distribution.pdf', dpi=300, format = 'pdf',  bbox_inches='tight')
    plt.close()


# Main execution
if __name__ == "__main__":
    print("Starting dataset analysis with data Pre-processing...")

    # Analyze fact-check dataset (before and after normalization)
    fact_check_normalized = analyze_factcheck_dataset('fact_check_test.tsv')

    # Analyze bias dataset (before and after normalization)
    bias_normalized = analyze_bias_dataset('bias_cleaned_file.csv')

    # Create final comparison
    if fact_check_normalized is not None and bias_normalized is not None:
        create_final_comparison(fact_check_normalized, bias_normalized)

    print("\nData Pre-processing analysis complete!")
    print("\nGenerated files:")
    print("1. fact_check_Pre-processing_comparison.pdf - Before and after Pre-processing comparison")
    print("2. fact_check_Pre-processing_table.pdf - Summary table of fact-check data Pre-processing")
    print("3. bias_Pre-processing_comparison.pdf - Before and after Pre-processing comparison")
    print("4. bias_Pre-processing_table.pdf - Summary table of bias data Pre-processing")
    print("5. Pre-processing_datasets_final_distribution.pdf - Final Pre-processing_datasets overview")