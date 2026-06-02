"""
Helper script to fetch and convert 2024 presidential election data

This script provides utilities to:
1. Convert Wikipedia tables to CSV
2. Validate data format
3. Match state names with education data

Data sources (see README.md for full list):
- Wikipedia: https://en.wikipedia.org/wiki/2024_United_States_presidential_election
- MIT Election Lab: https://electionlab.mit.edu/data
- FEC: https://www.fec.gov/
"""

import pandas as pd
import re
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / 'data'


def create_template_csv(output_file='election_2024_state_template.csv'):
    """
    Create a CSV template with all 50 state names matching the education data
    User can fill in the vote percentages manually
    """
    
    output_file = DATA_DIR / output_file

    # Load education data to get exact state names
    education_df = pd.read_csv(DATA_DIR / 'education_data_p.csv', comment='#')
    state_names = sorted(education_df['StateName'].tolist())
    
    # Create template dataframe
    template_df = pd.DataFrame({
        'StateName': state_names,
        'DemocraticVoteShare': [None] * len(state_names),
        'RepublicanVoteShare': [None] * len(state_names),
        'DemocraticCandidate': ['Harris'] * len(state_names),  # Update if different
        'RepublicanCandidate': ['Trump'] * len(state_names),   # Update if different
        'TotalVotes': [None] * len(state_names)
    })
    
    # Add instructions as comments
    with open(output_file, 'w') as f:
        f.write("# 2024 Presidential Election Results Template\n")
        f.write("# Fill in the vote percentages from official sources\n")
        f.write("# See README.md for list of official data sources\n")
        f.write("#\n")
        f.write("# Instructions:\n")
        f.write("# 1. Fill in DemocraticVoteShare and RepublicanVoteShare columns\n")
        f.write("# 2. Values should be percentages (0-100), not decimals\n")
        f.write("# 3. Update candidate names if different from default\n")
        f.write("# 4. TotalVotes is optional but helpful for validation\n")
        f.write("# 5. Save this file as 'election_2024_state.csv' when complete\n")
        f.write("#\n")
        
        template_df.to_csv(f, index=False)
    
    print(f"✓ Created template: {output_file}")
    print(f"  Contains {len(state_names)} states")
    print(f"\nNext steps:")
    print(f"  1. Open {output_file} in Excel or text editor")
    print(f"  2. Fill in vote percentages from official sources")
    print(f"  3. Save as 'election_2024_state.csv'")
    print(f"  4. Run analyze_education_voting.py")


def validate_election_data(filepath='election_2024_state.csv'):
    """
    Validate election data format and check for issues
    """
    filepath = DATA_DIR / filepath
    print(f"\nValidating {filepath}...")
    
    try:
        df = pd.read_csv(filepath, comment='#')
    except FileNotFoundError:
        print(f"✗ File not found: {filepath}")
        return False
    
    issues = []
    
    # Check required columns
    required_cols = ['StateName', 'DemocraticVoteShare', 'RepublicanVoteShare']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        issues.append(f"Missing required columns: {missing_cols}")
    
    # Check for null values
    for col in required_cols:
        if col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                issues.append(f"{col} has {null_count} missing values")
    
    # Check state count
    if len(df) != 50:
        issues.append(f"Expected 50 states, found {len(df)}")
    
    # Check vote percentages are in valid range
    if 'DemocraticVoteShare' in df.columns:
        invalid = df[(df['DemocraticVoteShare'] < 0) | (df['DemocraticVoteShare'] > 100)]
        if len(invalid) > 0:
            issues.append(f"DemocraticVoteShare out of range (0-100) for {len(invalid)} states")
    
    if 'RepublicanVoteShare' in df.columns:
        invalid = df[(df['RepublicanVoteShare'] < 0) | (df['RepublicanVoteShare'] > 100)]
        if len(invalid) > 0:
            issues.append(f"RepublicanVoteShare out of range (0-100) for {len(invalid)} states")
    
    # Check vote shares sum to reasonable values (should be close to 100)
    if 'DemocraticVoteShare' in df.columns and 'RepublicanVoteShare' in df.columns:
        df['TwoPartySum'] = df['DemocraticVoteShare'] + df['RepublicanVoteShare']
        unusual = df[(df['TwoPartySum'] < 85) | (df['TwoPartySum'] > 105)]
        if len(unusual) > 0:
            issues.append(f"Unusual vote sums for states: {unusual['StateName'].tolist()}")
    
    # Check state name matching with education data
    try:
        edu_df = pd.read_csv(DATA_DIR / 'education_data_p.csv', comment='#')
        edu_states = set(edu_df['StateName'])
        elec_states = set(df['StateName'])
        
        unmatched = edu_states.symmetric_difference(elec_states)
        if unmatched:
            issues.append(f"State name mismatches: {unmatched}")
    except:
        print("  ⚠ Could not load education data for state name comparison")
    
    # Report results
    if issues:
        print(f"\n✗ Validation found {len(issues)} issue(s):")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print(f"\n✓ Validation passed!")
        print(f"  - {len(df)} states")
        print(f"  - All required columns present")
        print(f"  - No missing values")
        print(f"  - Vote percentages in valid range")
        print(f"  - State names match education data")
        return True


def convert_wikipedia_table(html_or_text):
    """
    Helper function to convert Wikipedia table data to CSV format
    
    User should:
    1. Go to Wikipedia 2024 election page
    2. Find state results table
    3. Copy table as text or HTML
    4. Paste into a file
    5. Call this function with the file path
    """
    print("This function is a placeholder for converting Wikipedia tables.")
    print("Recommended approach:")
    print("  1. Visit: https://en.wikipedia.org/wiki/2024_United_States_presidential_election")
    print("  2. Find the state-by-state results table")
    print("  3. Copy the table")
    print("  4. Paste into Excel/Google Sheets")
    print("  5. Save as CSV with columns matching the template")
    print("  6. Or use pandas.read_html() if table is well-formatted")


def manual_entry_guide():
    """
    Print a guide for manual data entry
    """
    print("\n" + "=" * 70)
    print("MANUAL DATA ENTRY GUIDE")
    print("=" * 70)
    
    print("\n1. Create template:")
    print("   python3 fetch_election_data.py --template")
    
    print("\n2. Get official data from one of these sources:")
    print("   - Wikipedia: https://en.wikipedia.org/wiki/2024_United_States_presidential_election")
    print("   - 270towin: https://www.270towin.com/2024-presidential-election-results/")
    print("   - FEC: https://www.fec.gov/")
    
    print("\n3. Fill in the template:")
    print("   - Open election_2024_state_template.csv")
    print("   - For each state, enter Democratic and Republican vote percentages")
    print("   - Use actual percentages (e.g., 52.3, not 0.523)")
    print("   - Save as 'election_2024_state.csv'")
    
    print("\n4. Validate the data:")
    print("   python3 fetch_election_data.py --validate")
    
    print("\n5. Run analysis:")
    print("   python3 analyze_education_voting.py")
    
    print("\n" + "=" * 70)


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == '--template':
            create_template_csv()
        elif command == '--validate':
            validate_election_data()
        elif command == '--guide':
            manual_entry_guide()
        else:
            print(f"Unknown command: {command}")
            print("\nAvailable commands:")
            print("  --template   Create a blank template CSV")
            print("  --validate   Validate an existing election data file")
            print("  --guide      Show manual data entry guide")
    else:
        print("2024 Presidential Election Data Helper")
        print("\nUsage:")
        print("  python3 fetch_election_data.py --template   # Create template")
        print("  python3 fetch_election_data.py --validate   # Validate data")
        print("  python3 fetch_election_data.py --guide      # Show guide")
        print("\nFor detailed instructions, see README.md")


if __name__ == "__main__":
    main()
