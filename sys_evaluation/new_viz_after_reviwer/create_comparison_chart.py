"""
Create Publication-Ready Comparison Charts
"""
import matplotlib.pyplot as plt
import numpy as np
import re
from pathlib import Path

plt.rcParams.update({
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 12
})


def parse_statistical_results(filepath):
    """Parse statistical results file"""
    with open(filepath, 'r') as f:
        content = f.read()

    results = {'methods': {}, 'comparisons': {}}

    # Pattern: "RAG Weighted F1: 0.661 (95% CI: [0.585, 0.728])"
    pattern = r'(\w+(?:-\w+)?(?:\+\w+)?)\s+Weighted F1:\s*([\d.]+)\s*\(95% CI:\s*\[([\d.]+),\s*([\d.]+)\]\)'

    for match in re.finditer(pattern, content):
        method = match.group(1)
        f1 = float(match.group(2))
        ci_lower = float(match.group(3))
        ci_upper = float(match.group(4))

        # Standardize method names
        if method in ['RAG', 'LLM-only', 'LLM+KG', 'LLMKG']:
            method_name = 'LLM+KG' if method in ['LLM+KG', 'LLMKG'] else method

            # Use first occurrence only
            if method_name not in results['methods']:
                results['methods'][method_name] = {
                    'f1': f1,
                    'ci_lower': ci_lower,
                    'ci_upper': ci_upper,
                    'ci_error': f1 - ci_lower
                }

    # Extract p-values
    comp_pattern = r'Comparing\s+(\w+(?:-\w+)?(?:\+\w+)?)\s+vs\s+(\w+(?:-\w+)?(?:\+\w+)?)'
    pval_pattern = r'p-value:\s*([\d.]+)'

    comp_matches = list(re.finditer(comp_pattern, content))
    pval_matches = list(re.finditer(pval_pattern, content))

    for i, comp_match in enumerate(comp_matches):
        if i < len(pval_matches):
            m1 = comp_match.group(1)
            m2 = comp_match.group(2)
            m1 = 'LLM+KG' if m1 in ['LLM+KG', 'LLMKG'] else m1
            m2 = 'LLM+KG' if m2 in ['LLM+KG', 'LLMKG'] else m2
            p_val = float(pval_matches[i].group(1))
            results['comparisons'][f"{m1}_vs_{m2}"] = p_val

    return results


def get_significance_marker(p_value):
    if p_value < 0.001:
        return '***'
    elif p_value < 0.01:
        return '**'
    elif p_value < 0.05:
        return '*'
    else:
        return 'ns'


def add_significance_bracket(ax, x1, x2, y, p_value, height_offset=0.03):
    marker = get_significance_marker(p_value)
    if marker == 'ns':
        return
    bracket_height = y + height_offset
    ax.plot([x1, x1, x2, x2], [y, bracket_height, bracket_height, y], 'k-', linewidth=1.5)
    ax.text((x1 + x2) / 2, bracket_height + 0.01, marker, ha='center', va='bottom', fontsize=14, fontweight='bold')


def create_comparison_chart(results, title, ylabel, filename, output_dir):
    method_order = ['RAG', 'LLM-only', 'LLM+KG']
    methods = [m for m in method_order if m in results['methods']]

    if not methods:
        print(f"❌ ERROR: No methods found!")
        return

    f1_scores = [results['methods'][m]['f1'] for m in methods]
    ci_errors = [results['methods'][m]['ci_error'] for m in methods]

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(methods))
    bars = ax.bar(x, f1_scores, width=0.6, color=['#FF6B6B', '#4ECDC4', '#45B7D1'],
                   edgecolor='black', linewidth=1.5, alpha=0.8)
    ax.errorbar(x, f1_scores, yerr=ci_errors, fmt='none', ecolor='black', capsize=5, capthick=2, linewidth=2)

    for i, (bar, score) in enumerate(zip(bars, f1_scores)):
        ax.text(bar.get_x() + bar.get_width() / 2, score - 0.05, f'{score:.3f}',
                ha='center', va='top', fontsize=12, fontweight='bold', color='white')

    max_y = max(f1_scores) + max(ci_errors)
    if 'RAG_vs_LLM+KG' in results['comparisons']:
        add_significance_bracket(ax, 0, 2, max_y, results['comparisons']['RAG_vs_LLM+KG'], height_offset=0.08)
    if 'LLM-only_vs_LLM+KG' in results['comparisons']:
        add_significance_bracket(ax, 1, 2, max_y, results['comparisons']['LLM-only_vs_LLM+KG'], height_offset=0.04)
    if 'RAG_vs_LLM-only' in results['comparisons']:
        p_val = results['comparisons']['RAG_vs_LLM-only']
        if p_val < 0.05:
            add_significance_bracket(ax, 0, 1, max_y - 0.05, p_val, height_offset=0.02)

    ax.set_ylabel(ylabel, fontweight='bold')
    ax.set_title(title, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(methods, fontweight='bold')
    ax.set_ylim(0, max_y + 0.15)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.set_axisbelow(True)

    legend_text = '* p<0.05   ** p<0.01   *** p<0.001'
    ax.text(0.98, 0.02, legend_text, transform=ax.transAxes, ha='right', va='bottom',
            fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    plt.tight_layout()
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)
    plt.savefig(output_path / f'{filename}.png', dpi=300, bbox_inches='tight')
    plt.savefig(output_path / f'{filename}.pdf', bbox_inches='tight')
    print(f"✅ Saved: {filename}")
    plt.close()


def main():
    bias_path = '../results/bias_classification/bias_statistical_results.txt'
    fact_path = '../results/fact_checking/factcheck_statistical_results.txt'
    output_dir = '../results/comparison_charts'

    print("=" * 60)
    print("CREATING CHARTS")
    print("=" * 60)

    # Delete old images first!
    import os
    for f in ['figure3_bias_comparison.png', 'figure3_bias_comparison.pdf',
              'figure4_factcheck_comparison.png', 'figure4_factcheck_comparison.pdf']:
        try:
            os.remove(f'../results/comparison_charts/{f}')
            print(f"🗑️  Deleted old: {f}")
        except:
            pass

    if not Path(bias_path).exists() or not Path(fact_path).exists():
        print("❌ Files not found!")
        return

    print("\n📊 Parsing bias...")
    bias_results = parse_statistical_results(bias_path)
    print(f"   Found: {list(bias_results['methods'].keys())}")
    for m in bias_results['methods']:
        print(f"   {m}: F1={bias_results['methods'][m]['f1']:.3f}")

    print("\n📊 Parsing fact-checking...")
    fact_results = parse_statistical_results(fact_path)
    print(f"   Found: {list(fact_results['methods'].keys())}")
    for m in fact_results['methods']:
        print(f"   {m}: F1={fact_results['methods'][m]['f1']:.3f}")

    if bias_results['methods']:
        create_comparison_chart(bias_results, 'Bias Detection Performance Comparison',
                               'Weighted F1 Score', 'figure3_bias_comparison', output_dir)
    if fact_results['methods']:
        create_comparison_chart(fact_results, 'Fact-Checking Performance Comparison',
                               'Weighted F1 Score', 'figure4_factcheck_comparison', output_dir)

    print("\n✅ DONE!")


if __name__ == "__main__":
    main()