# 2024 Presidential Election Voting and Educational Attainment Analysis

Analysis of the relationship between state-level educational attainment and 2024 presidential election voting patterns.

## Project Overview

This project examines how educational attainment (bachelor's degree share) correlates with 2024 presidential election outcomes across the 50 U.S. states. It includes:

- Data processing scripts (Python and R, for flexibility depending on user preference)
- Statistical analysis (correlation, regression, t-tests)
- Visualizations (scatter plots, histograms, state rankings)
- Comprehensive summary reports

## Data Sources

### Educational Attainment Data

**Source:** U.S. Census Bureau (via Business Insider analysis)
- **Article:** [The most and least educated US states](https://www.businessinsider.com/most-least-educated-states-bachelors-degrees-or-higher#50-west-virginia-1)
- **Date:** May 28, 2026
- **Metric:** Percentage of adults 25+ with bachelor's degree or higher
- **Coverage:** All 50 states

**Processed files:**
- `data/most_and_least_educated_US-states.txt` - Original source data
- `data/education_data_p.csv` - Processed by Python script
- `data/education_data_r.csv` - Processed by R script

### 2024 Presidential Election Data

**Official and Recommended Sources:**

#### 1. **MIT Election Data and Science Lab** (Most Recommended for Research)
- **URL:** https://electionlab.mit.edu/data
- **Description:** Comprehensive, standardized election data from 1976-present
- **Format:** CSV, well-documented
- **Timeline:** Published ~6 months after election certification
- **Best for:** Academic research, historical comparisons, clean datasets

#### 2. **Federal Election Commission (FEC)** (Official Federal Source)
- **URL:** https://www.fec.gov/introduction-campaign-finance/election-results-and-voting-information/
- **Description:** Official federal election results
- **Format:** Various (PDF, Excel)
- **Timeline:** Published after state certifications complete
- **Best for:** Official, legally certified results

#### 3. **Associated Press (AP) Election Results**
- **URL:** https://www.ap.org/elections/
- **Description:** Comprehensive unofficial results, called races
- **Format:** API available, web interface
- **Timeline:** Real-time during election, finalized shortly after
- **Best for:** Timely, reliable unofficial results

#### 4. **Wikipedia - 2024 United States Presidential Election**
- **URL:** https://en.wikipedia.org/wiki/2024_United_States_presidential_election
- **Description:** Aggregated results with state-by-state tables
- **Format:** HTML tables (can be copied to spreadsheet)
- **Timeline:** Updated continuously, finalized after certification
- **Best for:** Quick reference, easy data extraction

#### 5. **270towin**
- **URL:** https://www.270towin.com/2024-presidential-election-results/
- **Description:** Interactive electoral map with detailed state results
- **Format:** Web interface with data tables
- **Timeline:** Updated in real-time during election
- **Best for:** Visual reference, state-level percentages

#### 6. **Dave Leip's U.S. Election Atlas**
- **URL:** https://uselectionatlas.org/
- **Description:** Comprehensive historical and recent election data
- **Format:** Subscription required for full data downloads
- **Timeline:** Updated regularly
- **Best for:** County-level data, detailed historical analysis

#### 7. **State Election Officials**
- Individual state Secretary of State websites
- Most authoritative source for each state
- Format varies by state
- Best for: Official state-certified results, precinct-level data

**Required data format for this analysis:**
```csv
StateName,DemocraticVoteShare,RepublicanVoteShare,DemocraticCandidate,RepublicanCandidate,TotalVotes
Alabama,34.6,65.4,Harris,Trump,2234000
Alaska,42.8,57.2,Harris,Trump,359000
...
```

**Project file:** `data/election_2024_state.csv`

This file was manually assembled from sources documented in its header comments. Treat the header metadata as the authoritative provenance record for the election data used in this project.

## Project Structure

```
education_voting/
├── README.md
├── data/
│   ├── most_and_least_educated_US-states.txt
│   ├── education_data_p.csv
│   ├── education_data_r.csv
│   ├── election_2024_state.csv
│   ├── election_2024_state_actual.csv
│   ├── election_2024_state_template.csv
│   └── extended_analysis_data.csv
├── scripts/
│   ├── process_education_data.py
│   ├── process_education_data.R
│   ├── fetch_election_data.py
│   ├── analyze_education_voting.py
│   ├── extended_analysis_multivariate.py
│   └── generate_html_report.py
├── reports/
│   ├── education_voting_report.qmd        # Main Quarto source
│   ├── education_voting_report.html       # Main rendered report
│   ├── education_voting_report_python.html
│   └── multivariate_comparison.png
└── outputs/
    └── analysis_output/
        ├── education_voting_scatter.png
        ├── education_voting_comparison.png
        ├── states_ranked_by_education.png
        ├── analysis_summary.txt
        └── education_voting_merged.csv
```

**Main output:** `reports/education_voting_report.html` - Comprehensive analysis including:
- Statistical analysis (correlation, regression, t-tests)
- Model comparison (linear vs. fractional logit)
- All visualizations (properly sized for browser viewing)
- State rankings and tables
- Conclusions and methodology

## Requirements

### Python
```bash
pip install pandas numpy matplotlib seaborn scipy
```

### R
```r
install.packages(c("stringr", "dplyr", "readr"))
```

## Usage

### Step 1: Process Education Data

**Python:**
```bash
python3 scripts/process_education_data.py
```

**R:**
```bash
Rscript scripts/process_education_data.R
```

Both scripts:
- Read `most_and_least_educated_US-states.txt`
- Extract state names, education ranks, bachelor's degree shares
- Recalculate ranks based on actual percentages (corrects markdown numbering issues)
- Output CSV with metadata comments
- Generate `education_data_p.csv` or `education_data_r.csv`

All generated files are written to `data/`.

### Step 2: Acquire 2024 Election Data

**Option A: Use helper script**
```bash
python3 scripts/fetch_election_data.py --guide
```

**Option B: Manual data entry**
1. Visit one of the official sources listed above
2. Copy state-by-state results
3. Format as CSV matching the template in `data/election_2024_state_template.csv`
4. Save with proper column names

**Required columns:**
- `StateName` - Must match education data exactly
- `DemocraticVoteShare` - Percentage (0-100)
- `RepublicanVoteShare` - Percentage (0-100)
- `DemocraticCandidate` - Candidate name
- `RepublicanCandidate` - Candidate name
- `TotalVotes` - Optional, for reference

### Step 3: Run Analysis

**⭐ Recommended: Generate comprehensive Quarto HTML report**

```bash
quarto render reports/education_voting_report.qmd
open reports/education_voting_report.html
```

This comprehensive report includes:
- Executive summary with key findings
- Statistical analysis (correlation, regression, t-tests)
- **Model comparison: Linear vs. Fractional Logit** (bounded regression)
- All visualizations embedded (properly sized, no horizontal scrolling)
- State rankings and tables
- Conclusions and limitations
- Professional formatting with TOC

Requirements: Quarto (install from https://quarto.org/docs/get-started/)

**Alternative A: Generate PNG charts for presentations**

```bash
python3 scripts/analyze_education_voting.py
```

Generates individual PNG files in `outputs/analysis_output/` for use in slides or other documents.

**Alternative B: Generate HTML report (Pure Python, no Quarto)**

```bash
python3 scripts/generate_html_report.py
```

Produces a standalone HTML file at `reports/education_voting_report_python.html` without requiring Quarto installation.

## Reading CSV Files with Comments

Both Python and R support reading CSV files with `#` comment lines:

**Python:**
```python
import pandas as pd
df = pd.read_csv('data/education_data_p.csv', comment='#')
```

**R:**
```r
library(readr)
df <- read_csv('data/education_data_r.csv', comment = '#')
```

## Key Findings

- **Strong positive correlation** (r = 0.78, p < 0.001)
- **61% of variance explained** by education level (R² = 0.612)
- **Regression model:** Democratic Vote % = -1.45 + 1.38 × Education %
- **Mean education difference:** Democratic-won states (40.1%) vs Republican-won states (32.4%) = 7.6 percentage points (p < 0.001)

## Methodology

### Model Selection: Linear vs. Bounded Regression

**Important methodological note:** Vote share is a **bounded continuous variable** (0-100%), making it a limited dependent variable. The comprehensive Quarto report includes detailed comparison between:

1. **Linear regression (OLS)** - Traditional approach, assumes unbounded outcomes
2. **Fractional logit (GLM)** - Theoretically appropriate for bounded proportions

**Key findings:**
- For our data (vote share range: 26-64%), both models give nearly identical results
- Predictions differ by < 0.1 percentage points on average
- **Fractional logit is theoretically preferable** (respects natural bounds)
- Linear regression is defensible for this dataset (well within bounds)

**Recommendation:** Use fractional logit for methodological rigor, though linear approximates well here.

**See the Quarto report** (`reports/education_voting_report.qmd` / `reports/education_voting_report.html`) for full model comparison with visualizations and detailed discussion.

### Statistical Tests
- **Pearson correlation:** Measures linear relationship strength
- **Spearman correlation:** Measures monotonic relationship (rank-based)
- **Linear regression:** Models Democratic vote share as function of education
- **Independent t-test:** Tests mean education difference between Democratic-won and Republican-won states

### Visualizations
1. **Scatter plot** - Shows correlation with regression line and confidence interval
2. **Comparison plots** - Histograms and box plots by election winner
3. **State rankings** - All 50 states ranked by education, colored by winner

## Future Extensions

- County-level analysis (requires county-level education data)
- Include graduate/professional degree share as additional predictor
- Time series analysis (compare to previous elections)
- Multivariate analysis with sourced urbanization, demographic, and economic covariates
- Geographic clustering analysis

## Notes

- State names must match exactly between education and election datasets
- The markdown numbering issue in the original education file has been corrected by recalculating ranks from actual percentages
- All CSV files include metadata as `#` comments for self-documentation
- `data/extended_analysis_data.csv` documents which columns come from project source files and which exploratory covariates were entered directly in code
- Processing date is automatically generated when scripts run

## License

Data sources are from public domain (Census Bureau, election results). Analysis code is provided for educational and research purposes.

## Contact

For questions about methodology or to report issues, please see the project repository.

---

**Last Updated:** 2026-06-02
