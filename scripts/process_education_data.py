"""
Process education data from text file to CSV
Extracts state education rankings and attainment percentages
"""

import re
import pandas as pd
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / 'data'

# Regex patterns for data extraction (separated from code)
PATTERNS = {
    'state_entry': r'^(\d+)\.\s+(?:\(tie\)\s+)?(.+?)$',
    'bachelors': r"Share of adults 25\+ with a bachelor's degree or higher:\s*(\d+\.?\d*)%",
    'grad_prof': [
        r'(\d+\.?\d*)%\s+of adults.*?graduate or professional degree',
        r'graduate or professional degree.*?(\d+\.?\d*)%',
        r'at (\d+\.?\d*)%.*?graduate',
        r'graduate.*?degree.*?at (\d+\.?\d*)%'
    ]
}

# Validation constants
MAX_REASONABLE_GRAD_SHARE = 40  # Upper bound for sanity check


def extract_comments_from_source(input_file):
    """Extract all lines starting with # from the source file"""
    comments = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith('#'):
                comments.append(line.rstrip())
    return comments


def parse_state_data(lines):
    """Parse state education data from text lines"""
    data = []
    current_state = None
    current_rank = None
    current_bachelors = None
    current_grad_prof = None
    
    for line in lines:
        line = line.strip()
        
        # Check if this line starts a new state entry
        rank_match = re.match(PATTERNS['state_entry'], line)
        
        if rank_match:
            # Save previous state data if complete
            if current_state and current_rank and current_bachelors:
                data.append({
                    'StateName': current_state,
                    'EducationRank': current_rank,
                    'BachelorsDegreeShare': current_bachelors,
                    'GraduateProfessionalDegreeShare': current_grad_prof
                })
            
            # Start new state
            current_rank = int(rank_match.group(1))
            current_state = rank_match.group(2).strip()
            current_bachelors = None
            current_grad_prof = None
            continue
        
        # Look for bachelor's degree percentage
        bachelors_match = re.search(PATTERNS['bachelors'], line)
        if bachelors_match:
            current_bachelors = float(bachelors_match.group(1))
        
        # Look for graduate/professional degree percentage
        if not current_grad_prof:
            for pattern in PATTERNS['grad_prof']:
                grad_match = re.search(pattern, line, re.IGNORECASE)
                if grad_match:
                    potential_value = float(grad_match.group(1))
                    # Sanity check
                    if potential_value < MAX_REASONABLE_GRAD_SHARE:
                        current_grad_prof = potential_value
                        break
    
    # Don't forget the last state
    if current_state and current_rank and current_bachelors:
        data.append({
            'StateName': current_state,
            'EducationRank': current_rank,
            'BachelorsDegreeShare': current_bachelors,
            'GraduateProfessionalDegreeShare': current_grad_prof
        })
    
    return data


def parse_education_data(input_file, output_file):
    """
    Parse education data from text file and save to CSV
    
    Args:
        input_file: Path to the source text file (expects # comment lines at top)
        output_file: Path to save the output CSV
    """
    
    # Extract comments from source file
    source_comments = extract_comments_from_source(input_file)
    
    # Read and parse the data
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    data = parse_state_data(lines)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # IMPORTANT: Recalculate ranks based on bachelor's degree share
    # The original file had markdown auto-numbering issues (many states marked as "1.")
    # So we derive the true rank from the data: highest % = rank 1, lowest % = rank 50
    df = df.sort_values('BachelorsDegreeShare', ascending=False)
    df['EducationRank'] = range(1, len(df) + 1)
    
    # Reorder columns
    df = df[['StateName', 'EducationRank', 'BachelorsDegreeShare', 'GraduateProfessionalDegreeShare']]
    
    # Save to CSV with metadata comments at the top
    with open(output_file, 'w') as f:
        # Write source comments from input file
        for comment in source_comments:
            f.write(f"{comment}\n")
        
        # Add processing metadata
        f.write("#\n")
        f.write(f"# Processed: {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write("# EducationRank: 1 = most educated (highest bachelor's+ %), 50 = least educated\n")
        f.write("# Note: Ranks recalculated from BachelorsDegreeShare due to markdown numbering issues\n")
        f.write("#\n")
        
        # Write the actual CSV data
        df.to_csv(f, index=False)
    
    # Print summary statistics
    print(f"Processed {len(df)} states")
    print(f"\nData saved to: {output_file}")
    print(f"\nTo read this CSV (with comments):")
    print(f"  Python: pd.read_csv('{output_file}', comment='#')")
    print(f"  R: read_csv('{output_file}', comment = '#')")
    print(f"\nSample of data:")
    print(df.head(10))
    print(f"\nMissing graduate/professional degree data for {df['GraduateProfessionalDegreeShare'].isna().sum()} states")
    
    return df


# Main execution
if __name__ == "__main__":
    input_file = DATA_DIR / 'most_and_least_educated_US-states.txt'
    output_file = DATA_DIR / 'education_data_p.csv'
    
    df = parse_education_data(input_file, output_file)
    
    # Data frame is now available for further analysis
    # Next step: merge with 2024 election data for correlation analysis
