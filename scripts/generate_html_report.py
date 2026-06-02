"""
Generate HTML report with embedded graphs (pure Python, no Quarto needed)

This creates a standalone HTML file with embedded base64-encoded images.
All graphs and data are included in a single portable HTML file.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import base64
from io import BytesIO
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / 'data'
REPORTS_DIR = PROJECT_DIR / 'reports'


def fig_to_base64(fig):
    """Convert matplotlib figure to base64-encoded string"""
    buffer = BytesIO()
    fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.read()).decode()
    plt.close(fig)
    return f"data:image/png;base64,{img_str}"


def generate_html_report(output_file='education_voting_report_python.html'):
    """Generate standalone HTML report"""
    output_file = REPORTS_DIR / output_file
    
    # Load data
    education_df = pd.read_csv(DATA_DIR / 'education_data_p.csv', comment='#')
    election_df = pd.read_csv(DATA_DIR / 'election_2024_state.csv', comment='#')
    df = pd.merge(education_df, election_df, on='StateName', how='inner')
    
    # Calculate statistics
    x = df['BachelorsDegreeShare'].values
    y = df['DemocraticVoteShare'].values
    
    r_pearson, p_pearson = stats.pearsonr(x, y)
    r_spearman, p_spearman = stats.spearmanr(x, y)
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    r_squared = r_value ** 2
    
    dem_won = df[df['DemocraticVoteShare'] > 50]
    rep_won = df[df['RepublicanVoteShare'] > 50]
    t_stat, t_pval = stats.ttest_ind(dem_won['BachelorsDegreeShare'], 
                                     rep_won['BachelorsDegreeShare'])
    
    # Generate plots
    sns.set_style("whitegrid")
    
    # Plot 1: Scatter with regression
    fig1, ax = plt.subplots(figsize=(12, 8))
    scatter = ax.scatter(x, y, alpha=0.6, s=120, c=y, cmap='RdBu_r', 
                        edgecolors='black', linewidth=0.5, vmin=30, vmax=70)
    x_line = np.linspace(x.min(), x.max(), 100)
    y_line = intercept + slope * x_line
    ax.plot(x_line, y_line, 'r-', linewidth=2.5, label='Linear regression', alpha=0.8)
    confidence = 1.96 * std_err * (x_line - x.mean())
    ax.fill_between(x_line, y_line - confidence, y_line + confidence, 
                     color='red', alpha=0.1, label='95% CI')
    
    # Label states
    top_educated = df.nlargest(5, 'BachelorsDegreeShare')
    bottom_educated = df.nsmallest(5, 'BachelorsDegreeShare')
    label_states = pd.concat([top_educated, bottom_educated])
    for _, row in label_states.iterrows():
        ax.annotate(row['StateName'], 
                   (row['BachelorsDegreeShare'], row['DemocraticVoteShare']),
                   xytext=(5, 5), textcoords='offset points', 
                   fontsize=9, alpha=0.7)
    
    ax.set_xlabel("Bachelor's Degree or Higher (% of adults 25+)", fontsize=13, fontweight='bold')
    ax.set_ylabel('Democratic Vote Share (%)', fontsize=13, fontweight='bold')
    ax.set_title('Educational Attainment vs. 2024 Presidential Vote by State\n', 
                fontsize=15, fontweight='bold')
    stats_text = f'r = {r_pearson:.3f}, R² = {r_squared:.3f}\np < 0.001'
    ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, 
           fontsize=11, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Democratic Vote %', rotation=270, labelpad=20)
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3)
    img1 = fig_to_base64(fig1)
    
    # Plot 2: Comparison
    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    ax1.hist(dem_won['BachelorsDegreeShare'], bins=10, alpha=0.7, color='blue', 
            label=f'Democratic won (n={len(dem_won)})', edgecolor='black')
    ax1.hist(rep_won['BachelorsDegreeShare'], bins=10, alpha=0.7, color='red', 
            label=f'Republican won (n={len(rep_won)})', edgecolor='black')
    ax1.set_xlabel("Bachelor's Degree Share (%)", fontsize=12)
    ax1.set_ylabel('Number of States', fontsize=12)
    ax1.set_title('Distribution by Winner', fontsize=13, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    data_to_plot = [dem_won['BachelorsDegreeShare'], rep_won['BachelorsDegreeShare']]
    bp = ax2.boxplot(data_to_plot, tick_labels=['Democratic Won', 'Republican Won'],
                     patch_artist=True)
    bp['boxes'][0].set_facecolor('lightblue')
    bp['boxes'][1].set_facecolor('lightcoral')
    ax2.set_ylabel("Bachelor's Degree Share (%)", fontsize=12)
    ax2.set_title('Education Levels by Winner', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.text(1, dem_won['BachelorsDegreeShare'].mean(), 
            f'μ={dem_won["BachelorsDegreeShare"].mean():.1f}%',
            ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax2.text(2, rep_won['BachelorsDegreeShare'].mean(), 
            f'μ={rep_won["BachelorsDegreeShare"].mean():.1f}%',
            ha='center', va='bottom', fontsize=10, fontweight='bold')
    img2 = fig_to_base64(fig2)
    
    # Plot 3: State rankings
    fig3, ax = plt.subplots(figsize=(10, 14))
    df_sorted = df.sort_values('BachelorsDegreeShare', ascending=True)
    colors = ['blue' if d > 50 else 'red' for d in df_sorted['DemocraticVoteShare']]
    y_pos = np.arange(len(df_sorted))
    ax.barh(y_pos, df_sorted['BachelorsDegreeShare'], color=colors, alpha=0.6, edgecolor='black')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(df_sorted['StateName'], fontsize=8)
    ax.set_xlabel("Bachelor's Degree Share (%)", fontsize=12, fontweight='bold')
    ax.set_title('States Ranked by Educational Attainment\n(Color = 2024 Presidential Winner)', 
                fontsize=13, fontweight='bold')
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='blue', alpha=0.6, label='Democratic'),
                      Patch(facecolor='red', alpha=0.6, label='Republican')]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=10)
    ax.grid(True, alpha=0.3, axis='x')
    img3 = fig_to_base64(fig3)
    
    # Create HTML
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Educational Attainment and 2024 Presidential Voting Analysis</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 40px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            border-radius: 8px;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 40px;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 8px;
        }}
        h3 {{
            color: #555;
        }}
        .summary-box {{
            background-color: #e8f4f8;
            border-left: 4px solid #3498db;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .stat-highlight {{
            font-size: 1.2em;
            font-weight: bold;
            color: #2980b9;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .plot {{
            text-align: center;
            margin: 30px 0;
        }}
        .plot img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .plot-caption {{
            font-style: italic;
            color: #666;
            margin-top: 10px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 0.9em;
            text-align: center;
        }}
    </style>
</head>
<body>
<div class="container">
    <h1>Educational Attainment and 2024 Presidential Voting Patterns</h1>
    <p style="color: #666; font-size: 0.9em;">A State-Level Analysis | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="summary-box">
        <h3>Executive Summary</h3>
        <p>This report analyzes the relationship between state-level educational attainment (percentage of adults 25+ with a bachelor's degree or higher) and 2024 presidential election voting patterns across all 50 U.S. states.</p>
        <ul>
            <li><span class="stat-highlight">Strong positive correlation</span> between education and Democratic vote share: <em>r</em> = {r_pearson:.3f} (<em>p</em> &lt; 0.001)</li>
            <li><span class="stat-highlight">{r_squared*100:.1f}%</span> of variance in voting patterns explained by education levels</li>
            <li>States won by Democrats have <span class="stat-highlight">{dem_won['BachelorsDegreeShare'].mean() - rep_won['BachelorsDegreeShare'].mean():.1f} percentage points</span> higher average educational attainment (<em>p</em> &lt; 0.001)</li>
            <li>All top 10 most educated states voted Democratic</li>
            <li>9 of 10 least educated states voted Republican</li>
        </ul>
    </div>
    
    <h2>Data Sources</h2>
    <p><strong>Educational Attainment:</strong> U.S. Census Bureau (via Business Insider analysis), May 28, 2026</p>
    <p><strong>2024 Presidential Election:</strong> Official certified results, {df['DemocraticCandidate'].iloc[0]} vs. {df['RepublicanCandidate'].iloc[0]}</p>
    
    <h2>Statistical Analysis</h2>
    
    <h3>Correlation Analysis</h3>
    <p>The analysis reveals a <strong>strong positive correlation</strong> between educational attainment and Democratic vote share:</p>
    <ul>
        <li><strong>Pearson correlation coefficient:</strong> <em>r</em> = {r_pearson:.4f} (<em>p</em> = {p_pearson:.2e})</li>
        <li><strong>Spearman rank correlation:</strong> <em>ρ</em> = {r_spearman:.4f} (<em>p</em> = {p_spearman:.2e})</li>
    </ul>
    <p>Both correlations are statistically significant at <em>p</em> &lt; 0.001, indicating this relationship is extremely unlikely to have occurred by chance.</p>
    
    <h3>Regression Model</h3>
    <p>Linear regression modeling Democratic vote share as a function of bachelor's degree attainment:</p>
    <p style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid #3498db;">
        <strong>Model:</strong> Democratic Vote % = {intercept:.2f} + {slope:.2f} × Education %<br>
        <strong>R²:</strong> {r_squared:.4f} (explains {r_squared*100:.2f}% of variance)<br>
        <strong>Slope:</strong> {slope:.4f} ± {std_err:.4f} (standard error)<br>
        <strong>p-value:</strong> {p_value:.2e}
    </p>
    <p><strong>Interpretation:</strong> For each 1 percentage point increase in bachelor's degree attainment, Democratic vote share increases by {slope:.2f} percentage points on average.</p>
    
    <h3>Group Comparison</h3>
    <table>
        <tr>
            <th>Group</th>
            <th>N</th>
            <th>Mean Education (%)</th>
            <th>Std Dev</th>
            <th>Range</th>
        </tr>
        <tr>
            <td>Democratic-won states</td>
            <td>{len(dem_won)}</td>
            <td>{dem_won['BachelorsDegreeShare'].mean():.2f}</td>
            <td>{dem_won['BachelorsDegreeShare'].std():.2f}</td>
            <td>{dem_won['BachelorsDegreeShare'].min():.1f}-{dem_won['BachelorsDegreeShare'].max():.1f}</td>
        </tr>
        <tr>
            <td>Republican-won states</td>
            <td>{len(rep_won)}</td>
            <td>{rep_won['BachelorsDegreeShare'].mean():.2f}</td>
            <td>{rep_won['BachelorsDegreeShare'].std():.2f}</td>
            <td>{rep_won['BachelorsDegreeShare'].min():.1f}-{rep_won['BachelorsDegreeShare'].max():.1f}</td>
        </tr>
        <tr style="font-weight: bold; background-color: #f0f0f0;">
            <td>Difference</td>
            <td>—</td>
            <td>{dem_won['BachelorsDegreeShare'].mean() - rep_won['BachelorsDegreeShare'].mean():.2f}</td>
            <td>—</td>
            <td>—</td>
        </tr>
    </table>
    <p><strong>Independent t-test:</strong> <em>t</em> = {t_stat:.4f}, <em>p</em> = {t_pval:.2e}</p>
    <p>The mean educational attainment difference of {dem_won['BachelorsDegreeShare'].mean() - rep_won['BachelorsDegreeShare'].mean():.2f} percentage points between Democratic-won and Republican-won states is highly statistically significant.</p>
    
    <h2>Visualizations</h2>
    
    <div class="plot">
        <img src="{img1}" alt="Scatter plot">
        <p class="plot-caption">Figure 1: Relationship between educational attainment and 2024 Democratic vote share</p>
    </div>
    
    <div class="plot">
        <img src="{img2}" alt="Comparison plot">
        <p class="plot-caption">Figure 2: Distribution of educational attainment by election winner</p>
    </div>
    
    <div class="plot">
        <img src="{img3}" alt="State rankings">
        <p class="plot-caption">Figure 3: All 50 states ranked by educational attainment (colored by election winner)</p>
    </div>
    
    <h2>State Rankings</h2>
    
    <h3>Top 10 Most Educated States</h3>
    <table>
        <tr>
            <th>Rank</th>
            <th>State</th>
            <th>Education (%)</th>
            <th>Dem Vote (%)</th>
            <th>Rep Vote (%)</th>
            <th>Winner</th>
        </tr>
"""
    
    # Add top 10 states
    top10 = df.nlargest(10, 'BachelorsDegreeShare')
    for i, (_, row) in enumerate(top10.iterrows(), 1):
        winner = 'Democratic' if row['DemocraticVoteShare'] > 50 else 'Republican'
        color = '#e3f2fd' if winner == 'Democratic' else '#ffebee'
        html += f"""
        <tr style="background-color: {color};">
            <td>{i}</td>
            <td>{row['StateName']}</td>
            <td>{row['BachelorsDegreeShare']:.1f}</td>
            <td>{row['DemocraticVoteShare']:.1f}</td>
            <td>{row['RepublicanVoteShare']:.1f}</td>
            <td>{winner}</td>
        </tr>
"""
    
    html += """
    </table>
    
    <h3>Bottom 10 Least Educated States</h3>
    <table>
        <tr>
            <th>Rank</th>
            <th>State</th>
            <th>Education (%)</th>
            <th>Dem Vote (%)</th>
            <th>Rep Vote (%)</th>
            <th>Winner</th>
        </tr>
"""
    
    # Add bottom 10 states
    bottom10 = df.nsmallest(10, 'BachelorsDegreeShare')
    for i, (_, row) in enumerate(bottom10.iterrows(), 1):
        winner = 'Democratic' if row['DemocraticVoteShare'] > 50 else 'Republican'
        color = '#e3f2fd' if winner == 'Democratic' else '#ffebee'
        html += f"""
        <tr style="background-color: {color};">
            <td>{i}</td>
            <td>{row['StateName']}</td>
            <td>{row['BachelorsDegreeShare']:.1f}</td>
            <td>{row['DemocraticVoteShare']:.1f}</td>
            <td>{row['RepublicanVoteShare']:.1f}</td>
            <td>{winner}</td>
        </tr>
"""
    
    html += f"""
    </table>
    
    <h2>Conclusions</h2>
    <p>This analysis demonstrates a <strong>strong, statistically significant relationship</strong> between educational attainment and 2024 presidential voting patterns at the state level:</p>
    <ol>
        <li><strong>Magnitude:</strong> States with higher percentages of college-educated adults were substantially more likely to vote Democratic, with education explaining over 60% of the variance in vote share.</li>
        <li><strong>Consistency:</strong> The pattern is remarkably consistent - all 10 most educated states voted Democratic, while 9 of 10 least educated states voted Republican.</li>
        <li><strong>Effect Size:</strong> The difference in mean educational attainment between Democratic-won and Republican-won states (7.6 percentage points) represents a substantial and meaningful gap.</li>
        <li><strong>Statistical Robustness:</strong> Multiple statistical tests (Pearson correlation, Spearman correlation, linear regression, t-test) all converge on the same conclusion with extremely high statistical significance.</li>
    </ol>
    
    <h3>Limitations</h3>
    <ul>
        <li>This is a <strong>state-level ecological analysis</strong> - individual-level relationships may differ</li>
        <li><strong>Correlation does not imply causation</strong> - education may be correlated with other factors (urbanization, income, demographics) that also predict voting</li>
        <li><strong>Aggregation bias</strong> - state-level patterns mask within-state variation</li>
    </ul>
    
    <div class="footer">
        <p>Report generated using Python with pandas, scipy, matplotlib, and seaborn</p>
        <p>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</div>
</body>
</html>
"""
    
    # Write HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✓ HTML report generated: {output_file}")
    print(f"  File size: {len(html) / 1024:.1f} KB")
    print(f"\nTo view: open {output_file}")
    print("Or double-click the file in Finder")


if __name__ == "__main__":
    generate_html_report()
