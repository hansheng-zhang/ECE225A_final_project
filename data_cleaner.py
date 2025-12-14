import re
import pandas as pd

def get_next_version(v_major, v_minor):
    # Defining the max minor version for each major version based on game history
    # 1.6 -> 2.0
    # 2.8 -> 3.0
    # 3.8 -> 4.0
    # 4.8 -> 5.0
    # 5.8 -> 6.0
    # 6.x ... assuming 6.8 -> 7.0 for future proofing or just standard increment
    
    max_minors = {
        1: 6,
        2: 8,
        3: 8,
        4: 8,
        5: 8,
        6: 8 # Assumption
    }
    
    if v_minor >= max_minors.get(v_major, 8):
        return v_major + 1, 0
    else:
        return v_major, v_minor + 1

def build_version_timeline():
    # Map "X.Y" string to Days Since 1.0
    timeline = {}
    curr_major = 1
    curr_minor = 0
    curr_day = 0
    
    # Generate up to 7.0 just to be safe
    while curr_major < 7:
        v_str = f"{curr_major}.{curr_minor}"
        timeline[v_str] = curr_day
        
        # Advance
        next_maj, next_min = get_next_version(curr_major, curr_minor)
        curr_major = next_maj
        curr_minor = next_min
        curr_day += 42 # Each version is 42 days
        
    return timeline

def parse_wish_stats(file_path):
    timeline = build_version_timeline()
    
    data = []
    
    # Regex patterns
    # Section Header: "5.2 A" or "5.2 C"
    version_pattern = re.compile(r"^(\d+\.\d+)\s+([ABC])")
    
    # Wish Count: "109,105" (can have trailing tab)
    count_pattern = re.compile(r"^(\d{1,3}(?:,\d{3})*)\s*$")
    
    # Character: "Chasca Summoned"
    char_pattern = re.compile(r"^(.+)\s+Summoned$")
    
    # Mixed line (Phase C/Chronicled): "13,980 Kaedehara Kazuha Summoned"
    mixed_pattern = re.compile(r"^(\d{1,3}(?:,\d{3})*)\s+(.+)\s+Summoned$")
    
    # 50:50 line (Ignore for now or store?) - "54.23% won 50:50"
    
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f.readlines()]
    
    current_version = None
    current_phase = None
    
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line:
            i += 1
            continue
            
        # Check Version Header
        v_match = version_pattern.match(line)
        if v_match:
            current_version = v_match.group(1)
            current_phase = v_match.group(2)
            i += 1
            continue
        
        if not current_version:
            i += 1
            continue
        
        # Check Mixed Pattern (common in Phase C or compressed lines)
        m_match = mixed_pattern.match(line)
        if m_match:
            count_str = m_match.group(1)
            char_name = m_match.group(2)
            wish_count = int(count_str.replace(',', ''))
            
            # Add entry
            days = timeline.get(current_version, 0)
            if current_phase == 'B':
                days += 21
            # Phase A and C are usually start of patch (Day 0 relative to version)
            
            major_ver = int(current_version.split('.')[0])

            data.append({
                'Version': current_version,
                'Phase': current_phase,
                'Character': char_name,
                'WishCount': wish_count,
                'DaysSinceLaunch': days,
                'MajorVersion': major_ver
            })
            i += 1
            continue
            
        # Check Standard Two-Line Pattern (Count \n Name)
        c_match = count_pattern.match(line)
        if c_match:
            try:
                # Look ahead for character name
                next_line_idx = i + 1
                while next_line_idx < len(lines) and not lines[next_line_idx]:
                    next_line_idx += 1
                
                if next_line_idx < len(lines):
                    next_line = lines[next_line_idx]
                    char_match = char_pattern.match(next_line)
                    if char_match:
                        wish_count = int(c_match.group(1).replace(',', ''))
                        char_name = char_match.group(1)
                        
                        days = timeline.get(current_version, 0)
                        if current_phase == 'B':
                            days += 21
                        
                        major_ver = int(current_version.split('.')[0])
                        
                        data.append({
                            'Version': current_version,
                            'Phase': current_phase,
                            'Character': char_name,
                            'WishCount': wish_count,
                            'DaysSinceLaunch': days,
                            'MajorVersion': major_ver
                        })
                        i = next_line_idx + 1
                        continue
            except IndexError:
                pass
        
        # If nothing matched, move next
        i += 1
        
    return pd.DataFrame(data)

def compute_reruns(df):
    # Sort by time
    df = df.sort_values('DaysSinceLaunch')
    
    # Calculate Rerun Interval and Count
    df['RerunInterval'] = None
    df['RerunCount'] = 0 # 0 means original run, 1 means 1st rerun
    
    # Dictionary to track last appearance of each character: {name: days}
    last_appearance = {}
    # Track count
    appear_counts = {}
    
    # Iterate and fill
    for idx, row in df.iterrows():
        char = row['Character']
        current_days = row['DaysSinceLaunch']
        
        if char in last_appearance:
            prev_days = last_appearance[char]

            # Previous End = Previous Start + 21.
            interval = current_days - (prev_days + 21)
            # If interval is negative? (Overlapping banners? Should not happen)
            if interval < 0:
                interval = 0 # Fallback
                
            df.at[idx, 'RerunInterval'] = interval
            
            appear_counts[char] += 1
            df.at[idx, 'RerunCount'] = appear_counts[char] - 1 # 1st appearance is index 1, so 0 reruns? No, let's call 1st appearance "Release", 2nd "1st Rerun"
            # Actually standard terminology:
            # First banner: Release (RerunCount = 0)
            # Second banner: 1st Rerun (RerunCount = 1)
            
            last_appearance[char] = current_days
            
        else:
            # First time seeing this char in OUR dataset.
            # IMPORTANT: For chars released in 1.0-1.2, their first appearance here (1.3+) is NOT their release.
            # RerunInterval will be NaN.
            last_appearance[char] = current_days
            appear_counts[char] = 1
            df.at[idx, 'RerunCount'] = 0 # Tentative
            
    return df

if __name__ == "__main__":
    input_file = "wish_stats.txt"
    output_file = "cleaned_wish_data.csv"
    
    print(f"Parsing {input_file}...")
    df = parse_wish_stats(input_file)
    print(f"Found {len(df)} records.")
    
    print("Computing rerun stats...")
    df = compute_reruns(df)
    
    print("Example data:")
    print(df.head())
    
    df.to_csv(output_file, index=False)
    print(f"Saved to {output_file}")
