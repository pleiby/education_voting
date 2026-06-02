"""
Analyze the relationship between educational attainment and 2024 presidential voting patterns by state

Data sources:
- Education: education_data_p.csv (processed from Census Bureau data)
- Election: 2024 presidential results by state (to be acquired)

Recommended election data sources:
- MIT Election Data and Science Lab: https://electionlab.mit.edu/data
- Federal Election Commission: https://www.fec.gov/introduction-campaign-finance/election-results-and-voting-information/
- 270towin.com: https://www.270towin.com/2024-presidential-election-results/
- Wikipedia: https://en.wikipedia.org/wiki/2024_United_States_presidential_election
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from datetime import datetime
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / 'data'
OUTPUT_DIR = PROJECT_DIR / 'outputs' / 'analysis_output'
EDUCATION_FILE = DATA_DIR / 'education_data_p.csv'
ELECTION_FILE = DATA_DIR / 'election_2024_state.csv'

# Statistical significance level
ALPHA = 0.05


def load_education_data(filepath):
    """Load education data from CSV with comments"""
    df = pd.read_csv(filepath, comment='#')
    print(f"✓ Loaded education data: {len(df)} states")
    print(f"  Columns: {list(df.columns)}")
    return df


def load_election_data(filepath):
    """
    Load 2024 presidential election results by state
    
    Expected columns:
    - StateName: State name (must match education data)
    - DemocraticVoteShare: Democratic candidate vote percentage (0-100)
    - RepublicanVoteShare: Republican candidate vote percentage (0-100)
    - DemocraticCandidate: Candidate name (e.g., "Harris")
    - RepublicanCandidate: Candidate name (e.g., "Trump")
    - TotalVotes: Total votes cast (optional, for weighting)
    """
    try:
        df = pd.read_csv(filepath, comment='#')
        print(f"✓ Loaded election data: {len(df)} states")
        
        # Validate required columns
        required = ['StateName', 'DemocraticVoteShare', 'RepublicanVoteShare']
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        return df
    except FileNotFoundError:
        print(f"\n⚠ Election data file not found: {filepath}")
        print("\nTo proceed, create a CSV file with 2024 presidential election results.")
        print("Required format:")
        print("  StateName,DemocraticVoteShare,RepublicanVoteShare,DemocraticCandidate,RepublicanCandidate")
        print("  Alabama,35.2,64.8,Harris,Trump")
        print("  Alaska,42.5,57.5,Harris,Trump")
        print("  ...")
        print("\nSee script header for data source recommendations.")
        return None


def merge_datasets(education_df, election_df):
    """Merge education and election data on state name"""
    merged = pd.merge(
        education_df,
        election_df,
        on='StateName',
        how='inner'
    )
    
    print(f"\n✓ Merged data: {len(merged)} states")
    
    # Check for states that didn't match
    edu_states = set(education_df['StateName'])
    elec_states = set(election_df['StateName'])
    unmatched = edu_states.symmetric_difference(elec_states)
    if unmatched:
        print(f"  ⚠ Unmatched states: {unmatched}")
    
    return merged


def calculate_statistics(df):
    """Calculate correlation and regression statistics"""
    
    # Democratic vote share vs. Bachelor's degree share
    x = df['BachelorsDegreeShare'].values
    y = df['DemocraticVoteShare'].values
    
    # Pearson correlation
    r_pearson, p_pearson = stats.pearsonr(x, y)
    
    # Spearman correlation (rank-based, robust to outliers)
    r_spearman, p_spearman = stats.spearmanr(x, y)
    
    # Linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    # Calculate R²
    r_squared = r_value ** 2
    
    results = {
        'pearson_r': r_pearson,
        'pearson_p': p_pearson,
        'spearman_r': r_spearman,
        'spearman_p': p_spearman,
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_squared,
        'regression_p': p_value,
        'std_err': std_err,
        'n_states': len(df)
    }
    
    return results


def print_statistical_summary(stats_results):
    """Print formatted statistical summary"""
    print("\n" + "=" * 70)
    print("STATISTICAL ANALYSIS: Education vs. 2024 Presidential Voting")
    print("=" * 70)
    
    print(f"\nSample size: {stats_results['n_states']} states")
    
    print("\n--- CORRELATION ANALYSIS ---")
    print(f"Pearson correlation (r):  {stats_results['pearson_r']:7.4f}  (p = {stats_results['pearson_p']:.4f})")
    print(f"Spearman correlation (ρ): {stats_results['spearman_r']:7.4f}  (p = {stats_results['spearman_p']:.4f})")
    
    sig_pearson = "***" if stats_results['pearson_p'] < 0.001 else "**" if stats_results['pearson_p'] < 0.01 else "*" if stats_results['pearson_p'] < 0.05 else "ns"
    print(f"Significance: {sig_pearson} ({'p < 0.001' if stats_results['pearson_p'] < 0.001 else f'p = {stats_results['pearson_p']:.4f}'})")
    
    # Interpretation
    r = abs(stats_results['pearson_r'])
    if r > 0.7:
        strength = "strong"
    elif r > 0.4:
        strength = "moderate"
    elif r > 0.2:
        strength = "weak"
    else:
        strength = "very weak"
    
    direction = "positive" if stats_results['pearson_r'] > 0 else "negative"
    print(f"\nInterpretation: {strength.capitalize()} {direction} correlation")
    print(f"Higher bachelor's degree attainment is associated with {'higher' if stats_results['pearson_r'] > 0 else 'lower'} Democratic vote share.")
    
    print("\n--- LINEAR REGRESSION ---")
    print(f"Model: DemocraticVoteShare = {stats_results['intercept']:.2f} + {stats_results['slope']:.2f} × BachelorsDegreeShare")
    print(f"R² = {stats_results['r_squared']:.4f} ({stats_results['r_squared']*100:.2f}% of variance explained)")
    print(f"p-value: {stats_results['regression_p']:.4e}")
    print(f"Standard error of slope: {stats_results['std_err']:.4f}")
    
    print(f"\nInterpretation: For each 1 percentage point increase in bachelor's degree attainment,")
    print(f"Democratic vote share changes by {stats_results['slope']:.2f} percentage points (on average).")
    
    print("\n" + "=" * 70)


def create_visualizations(df, stats_results, output_dir):
    """Create publication-quality visualizations"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 11
    
    # 1. Main scatter plot with regression line
    fig, ax = plt.subplots(figsize=(12, 8))
    
    x = df['BachelorsDegreeShare']
    y = df['DemocraticVoteShare']
    
    # Scatter plot
    scatter = ax.scatter(x, y, alpha=0.6, s=100, c=y, cmap='RdBu_r', 
                        edgecolors='black', linewidth=0.5, vmin=30, vmax=70)
    
    # Regression line
    x_line = np.linspace(x.min(), x.max(), 100)
    y_line = stats_results['intercept'] + stats_results['slope'] * x_line
    ax.plot(x_line, y_line, 'r-', linewidth=2, label='Linear regression', alpha=0.8)
    
    # 95% confidence interval (approximate)
    confidence = 1.96 * stats_results['std_err'] * (x_line - x.mean())
    ax.fill_between(x_line, y_line - confidence, y_line + confidence, 
                     color='red', alpha=0.1, label='95% CI')
    
    # Labels for interesting states
    # Top 5 most and least educated
    top_educated = df.nlargest(5, 'BachelorsDegreeShare')
    bottom_educated = df.nsmallest(5, 'BachelorsDegreeShare')
    label_states = pd.concat([top_educated, bottom_educated])
    
    for _, row in label_states.iterrows():
        ax.annotate(row['StateName'], 
                   (row['BachelorsDegreeShare'], row['DemocraticVoteShare']),
                   xytext=(5, 5), textcoords='offset points', 
                   fontsize=9, alpha=0.7)
    
    # Formatting
    ax.set_xlabel('Bachelor\'s Degree or Higher (% of adults 25+)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Democratic Vote Share (% of votes)', fontsize=13, fontweight='bold')
    ax.set_title('Educational Attainment vs. 2024 Presidential Vote by State\n', 
                fontsize=15, fontweight='bold')
    
    # Add statistics to plot
    stats_text = f'r = {stats_results["pearson_r"]:.3f}, R² = {stats_results["r_squared"]:.3f}\n'
    stats_text += f'p < 0.001' if stats_results['pearson_p'] < 0.001 else f'p = {stats_results["pearson_p"]:.4f}'
    ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, 
           fontsize=11, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Democratic Vote %', rotation=270, labelpad=20)
    
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    scatter_path = output_dir / 'education_voting_scatter.png'
    plt.savefig(scatter_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved: {scatter_path}")
    
    # 2. Histogram comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Split by winner
    dem_won = df[df['DemocraticVoteShare'] > 50]
    rep_won = df[df['RepublicanVoteShare'] > 50]
    
    ax1.hist(dem_won['BachelorsDegreeShare'], bins=10, alpha=0.7, color='blue', 
            label=f'Dem won ({len(dem_won)} states)', edgecolor='black')
    ax1.hist(rep_won['BachelorsDegreeShare'], bins=10, alpha=0.7, color='red', 
            label=f'Rep won ({len(rep_won)} states)', edgecolor='black')
    ax1.set_xlabel('Bachelor\'s Degree Share (%)')
    ax1.set_ylabel('Number of States')
    ax1.set_title('Distribution of Education by Election Winner')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Box plot comparison
    data_to_plot = [dem_won['BachelorsDegreeShare'], rep_won['BachelorsDegreeShare']]
    bp = ax2.boxplot(data_to_plot, labels=['Democratic Won', 'Republican Won'],
                     patch_artist=True)
    bp['boxes'][0].set_facecolor('lightblue')
    bp['boxes'][1].set_facecolor('lightcoral')
    ax2.set_ylabel('Bachelor\'s Degree Share (%)')
    ax2.set_title('Education Levels by Election Winner')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add mean values
    ax2.text(1, dem_won['BachelorsDegreeShare'].mean(), 
            f'μ={dem_won["BachelorsDegreeShare"].mean():.1f}%',
            ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax2.text(2, rep_won['BachelorsDegreeShare'].mean(), 
            f'μ={rep_won["BachelorsDegreeShare"].mean():.1f}%',
            ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    comparison_path = output_dir / 'education_voting_comparison.png'
    plt.savefig(comparison_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {comparison_path}")
    
    # 3. State ranking plot
    fig, ax = plt.subplots(figsize=(10, 14))
    
    df_sorted = df.sort_values('BachelorsDegreeShare', ascending=True)
    colors = ['blue' if d > 50 else 'red' for d in df_sorted['DemocraticVoteShare']]
    
    y_pos = np.arange(len(df_sorted))
    ax.barh(y_pos, df_sorted['BachelorsDegreeShare'], color=colors, alpha=0.6, edgecolor='black')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(df_sorted['StateName'], fontsize=8)
    ax.set_xlabel('Bachelor\'s Degree Share (%)', fontsize=12, fontweight='bold')
    ax.set_title('States Ranked by Educational Attainment\n(Color = 2024 Presidential Winner)', 
                fontsize=13, fontweight='bold')
    
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='blue', alpha=0.6, label='Democratic'),
                      Patch(facecolor='red', alpha=0.6, label='Republican')]
    ax.legend(handles=legend_elements, loc='lower right')
    
    ax.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()
    ranking_path = output_dir / 'states_ranked_by_education.png'
    plt.savefig(ranking_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {ranking_path}")
    
    plt.close('all')


def generate_summary_report(df, stats_results, output_dir):
    """Generate a text summary report"""
    report_file = output_dir / 'analysis_summary.txt'
    
    with open(report_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("ANALYSIS REPORT: Educational Attainment vs. 2024 Presidential Voting\n")
        f.write("=" * 80 + "\n")
        f.write(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"\nDatasets:\n")
        f.write(f"  Education: {EDUCATION_FILE}\n")
        f.write(f"  Election: {ELECTION_FILE}\n")
        f.write(f"  Sample size: {stats_results['n_states']} states\n")
        
        f.write("\n" + "-" * 80 + "\n")
        f.write("STATISTICAL RESULTS\n")
        f.write("-" * 80 + "\n")
        
        f.write(f"\nCorrelation Analysis:\n")
        f.write(f"  Pearson r = {stats_results['pearson_r']:.4f} (p = {stats_results['pearson_p']:.4e})\n")
        f.write(f"  Spearman ρ = {stats_results['spearman_r']:.4f} (p = {stats_results['spearman_p']:.4e})\n")
        
        f.write(f"\nLinear Regression:\n")
        f.write(f"  Model: DemVote% = {stats_results['intercept']:.2f} + {stats_results['slope']:.2f} × Education%\n")
        f.write(f"  R² = {stats_results['r_squared']:.4f}\n")
        f.write(f"  p-value = {stats_results['regression_p']:.4e}\n")
        f.write(f"  Standard error = {stats_results['std_err']:.4f}\n")
        
        # Comparative statistics
        dem_won = df[df['DemocraticVoteShare'] > 50]
        rep_won = df[df['RepublicanVoteShare'] > 50]
        
        f.write("\n" + "-" * 80 + "\n")
        f.write("DESCRIPTIVE STATISTICS\n")
        f.write("-" * 80 + "\n")
        
        f.write(f"\nDemocratic-won states (n={len(dem_won)}):\n")
        f.write(f"  Mean education: {dem_won['BachelorsDegreeShare'].mean():.2f}%\n")
        f.write(f"  Median education: {dem_won['BachelorsDegreeShare'].median():.2f}%\n")
        f.write(f"  Std dev: {dem_won['BachelorsDegreeShare'].std():.2f}%\n")
        
        f.write(f"\nRepublican-won states (n={len(rep_won)}):\n")
        f.write(f"  Mean education: {rep_won['BachelorsDegreeShare'].mean():.2f}%\n")
        f.write(f"  Median education: {rep_won['BachelorsDegreeShare'].median():.2f}%\n")
        f.write(f"  Std dev: {rep_won['BachelorsDegreeShare'].std():.2f}%\n")
        
        # T-test for difference
        t_stat, t_pval = stats.ttest_ind(dem_won['BachelorsDegreeShare'], 
                                         rep_won['BachelorsDegreeShare'])
        f.write(f"\nIndependent t-test (education difference between winners):\n")
        f.write(f"  t-statistic = {t_stat:.4f}\n")
        f.write(f"  p-value = {t_pval:.4e}\n")
        f.write(f"  Mean difference = {dem_won['BachelorsDegreeShare'].mean() - rep_won['BachelorsDegreeShare'].mean():.2f} percentage points\n")
        
        f.write("\n" + "-" * 80 + "\n")
        f.write("TOP 10 STATES BY EDUCATION\n")
        f.write("-" * 80 + "\n")
        top10 = df.nlargest(10, 'BachelorsDegreeShare')[['StateName', 'BachelorsDegreeShare', 'DemocraticVoteShare']]
        for i, row in top10.iterrows():
            winner = "D" if row['DemocraticVoteShare'] > 50 else "R"
            f.write(f"  {row['StateName']:20s} {row['BachelorsDegreeShare']:5.1f}%  Dem: {row['DemocraticVoteShare']:5.1f}%  [{winner}]\n")
        
        f.write("\n" + "-" * 80 + "\n")
        f.write("BOTTOM 10 STATES BY EDUCATION\n")
        f.write("-" * 80 + "\n")
        bottom10 = df.nsmallest(10, 'BachelorsDegreeShare')[['StateName', 'BachelorsDegreeShare', 'DemocraticVoteShare']]
        for i, row in bottom10.iterrows():
            winner = "D" if row['DemocraticVoteShare'] > 50 else "R"
            f.write(f"  {row['StateName']:20s} {row['BachelorsDegreeShare']:5.1f}%  Dem: {row['DemocraticVoteShare']:5.1f}%  [{winner}]\n")
        
        f.write("\n" + "=" * 80 + "\n")
    
    print(f"✓ Saved: {report_file}")


def main():
    """Main analysis pipeline"""
    print("\n" + "=" * 70)
    print("EDUCATION vs VOTING ANALYSIS: 2024 Presidential Election")
    print("=" * 70 + "\n")
    
    # Load data
    education_df = load_education_data(EDUCATION_FILE)
    election_df = load_election_data(ELECTION_FILE)
    
    if election_df is None:
        print("\n⚠ Analysis cannot proceed without election data.")
        print("Please create the election data file and run again.")
        return
    
    # Merge datasets
    merged_df = merge_datasets(education_df, election_df)
    
    if len(merged_df) < 30:
        print(f"\n⚠ Warning: Only {len(merged_df)} states matched. Check state name consistency.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Calculate statistics
    print("\nCalculating statistics...")
    stats_results = calculate_statistics(merged_df)
    
    # Print summary
    print_statistical_summary(stats_results)
    
    # Create visualizations
    print("\nGenerating visualizations...")
    create_visualizations(merged_df, stats_results, OUTPUT_DIR)
    
    # Generate report
    print("\nGenerating summary report...")
    generate_summary_report(merged_df, stats_results, OUTPUT_DIR)
    
    # Save merged dataset
    merged_output = OUTPUT_DIR / 'education_voting_merged.csv'
    merged_df.to_csv(merged_output, index=False)
    print(f"✓ Saved merged data: {merged_output}")
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"\nOutputs saved to: {OUTPUT_DIR}/")
    print("  - education_voting_scatter.png")
    print("  - education_voting_comparison.png")
    print("  - states_ranked_by_education.png")
    print("  - analysis_summary.txt")
    print("  - education_voting_merged.csv")
    print("\n")


if __name__ == "__main__":
    main()
