import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def analyze_and_plot(input_file):
    df = pd.read_csv(input_file)
    
    # Filter out records with no RerunInterval (First appearances) for interval analysis
    reruns = df.dropna(subset=['RerunInterval']).copy()
    reruns['RerunInterval'] = reruns['RerunInterval'].astype(float)
    
    # --- Feature Engineering: Relative Popularity ---
    # Group by Major Version and calculate Z-score of WishCount
    # Note: We should normalize WishCount against the *Avg WishCount of that Major Version*
    # because player base size changes.
    
    df['RelativeWishCount'] = df.groupby('MajorVersion')['WishCount'].transform(
        lambda x: (x - x.mean()) / x.std()
    )
    
    # We need to map this back to the reruns df
    # Rerun logic: The wish count of the *previous* banner might influence the *next* rerun interval.
    # OR: Does the character's *general* popularity (e.g. average wishes) influence rerun frequency?
    # The prompt says: "whether characters with higher wish counts tend to rerun sooner".
    # This usually means "If I sold well, do I come back sooner?"
    # So we should look at the Wish Count of the *Banner N* vs the Interval to *Banner N+1*.
    # In our data:
    # Row X is Banner N. Interval X is time *since* N-1.
    # So Interval X is the gap leading up to Banner N.
    # So we should correlate Interval X with Wish Count of Banner N-1.
    # BUT, we don't have explicit "Previous Banner Wish Count" column easily without shift.
    
    # Let's adjust.
    # We want to see if "High Popularity -> Short Wait".
    # Ideally: WishCount(Appearance K) vs Interval(Appearance K+1).
    # Currently: RerunInterval is "Time since previous".
    # So for Row i: RerunInterval is time between i-1 and i.
    # We should match this with WishCount of i-1.
    
    # Let's create a lag feature.
    # Sort by character and Time.
    df.sort_values(['Character', 'DaysSinceLaunch'], inplace=True)
    df['PrevWishCount'] = df.groupby('Character')['WishCount'].shift(1)
    df['PrevMajorVersion'] = df.groupby('Character')['MajorVersion'].shift(1)
    
    # Re-calculate Relative Wish Count based on the *Previous* Major Version?
    # Or just use the Wish Count of the previous banner and normalize it by *its* era.
    
    # Let's calculate globally normalized wish counts (by major version stats)
    # First, compute stats per major version
    mv_stats = df.groupby('MajorVersion')['WishCount'].agg(['mean', 'std']).reset_index()
    
    # Merge stats to original df
    df = df.merge(mv_stats, on='MajorVersion', suffixes=('', '_mv'))
    df['ZScore'] = (df['WishCount'] - df['mean']) / df['std']
    
    # Now shift ZScore to get PrevZScore
    df.sort_values(['Character', 'DaysSinceLaunch'], inplace=True)
    df['PrevZScore'] = df.groupby('Character')['ZScore'].shift(1)
    
    # Filter for reruns (rows where RerunInterval is present)
    rerun_analysis = df.dropna(subset=['RerunInterval']).copy()
    rerun_analysis['RerunInterval'] = rerun_analysis['RerunInterval'].astype(float)
    
    # --- Visualization 1: Rerun Interval Trend ---
    plt.figure(figsize=(10, 6))
    plt.scatter(rerun_analysis['DaysSinceLaunch'], rerun_analysis['RerunInterval'], 
                c=rerun_analysis['MajorVersion'], cmap='viridis', alpha=0.7)
    plt.colorbar(label='Major Version')
    plt.title('Character Rerun Intervals Over Time')
    plt.xlabel('Days Since Launch (approx)')
    plt.ylabel('Rerun Interval (Days)')
    plt.grid(True, alpha=0.3)
    plt.savefig('rerun_trend.png')
    plt.close()
    
    # --- Visualization 2: Interval vs Popularity (Previous Banner) ---
    plt.figure(figsize=(10, 6))
    valid_corr = rerun_analysis.dropna(subset=['PrevZScore'])
    
    scatter = plt.scatter(valid_corr['PrevZScore'], valid_corr['RerunInterval'], 
                c=valid_corr['MajorVersion'], cmap='viridis', alpha=0.7)
    plt.colorbar(scatter, label='Major Version')
    
    # Trend line
    z = np.polyfit(valid_corr['PrevZScore'], valid_corr['RerunInterval'], 1)
    p = np.poly1d(z)
    plt.plot(valid_corr['PrevZScore'], p(valid_corr['PrevZScore']), "r--", alpha=0.8)
    
    plt.title(f'Impact of Previous Banner Popularity on Rerun Wait\nCorrelation: {valid_corr["PrevZScore"].corr(valid_corr["RerunInterval"]):.3f}')
    plt.xlabel('Previous Banner Wish Count (Z-Score within Major Version)')
    plt.ylabel('Time Until Next Rerun (Days)')
    plt.grid(True, alpha=0.3)
    plt.savefig('wish_correlation.png')
    plt.close()
    
    # --- Visualization 3: Boxplot by Major Version ---
    plt.figure(figsize=(10, 6))
    rerun_analysis.boxplot(column='RerunInterval', by='MajorVersion', grid=False, rot=45)
    plt.title('Distribution of Rerun Intervals by Major Version')
    plt.suptitle('') # Suppress auto title
    plt.ylabel('Rerun Interval (Days)')
    plt.xlabel('Major Version')
    plt.tight_layout()
    plt.savefig('interval_dist.png')
    plt.close()

    # --- Statistics ---
    print("Correlation (Prev Popularity vs Interval):")
    print(valid_corr[['PrevZScore', 'RerunInterval']].corr())
    
    print("\nAverage Rerun Interval by Major Version:")
    print(rerun_analysis.groupby('MajorVersion')['RerunInterval'].mean())
    
    return rerun_analysis

if __name__ == "__main__":
    analyze_and_plot("cleaned_wish_data.csv")
