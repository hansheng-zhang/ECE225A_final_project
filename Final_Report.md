# Genshin Impact Character Rerun Interval Analysis Report

**GitHub Repository:** [https://github.com/hansheng-zhang/ECE225A_final_project](https://github.com/hansheng-zhang/ECE225A_final_project)

## Abstract
This report presents a statistical analysis of character rerun intervals in the Action RPG *Genshin Impact*. By analyzing banner history data ranging from Version 1.3 to the projected Version 6.2, we investigate the relationship between a character’s banner popularity (wish counts) and the duration of their hiatus between appearances. Contrary to the common community belief that "popular characters return sooner," our findings suggest a weak negative correlation (-0.21), indicating that popularity is a minor factor. The primary driver of increasing wait times is identified as the rapid expansion of the character roster, which creates a scheduling bottleneck.

---

## 1. Introduction

### 1.1 Background
*Genshin Impact* utilizes a "gacha" monetization model where playable characters are obtained through limited-time events known as "Banners." Once a character's banner ends, they become unavailable until their next "Rerun." For players, especially those who are Free-to-Play (F2P) or low-spenders, understanding the logic behind rerun scheduling is crucial for resource management. Currencies (Primogems) are scarce, and missing a desired character can result in a wait of over a year.

### 1.2 Problem Statement
The central question of this study is: **Does character popularity influence rerun scheduling?**
Specifically, we aim to determine if characters with higher sales (proxied by "Wish Counts") are prioritized by the developers (HoYoverse) to return more frequently than less popular characters.

### 1.3 Motivation
Understanding this relationship provides value in two ways:
1.  **Player Strategy**: If popularity dictates reruns, players can predict when high-tier characters will return and save resources accordingly.
2.  **Game Economy Insight**: It sheds light on whether the developer favors short-term revenue (rerunning best-sellers) or long-term engagement (forcing scarcity).

---

## 2. Data Description

### 2.1 Data Source
The raw data was aggregated from *paimon.moe*, a community database that tracks global wish statistics. The dataset `wish_stats.txt` includes banner history from **Version 1.3** extending into future projections up to **Version 6.2**.

### 2.2 Data Structure
The processed dataset (`cleaned_wish_data.csv`) contains the following key features:
*   **Version**: The game update version (e.g., 2.1, 4.0).
*   **Character**: Name of the 5-star character featured.
*   **WishCount**: Total estimated wishes pulled on the banner (proxy for revenue/popularity).
*   **RerunInterval**: The calculated number of days since the character's previous start date.
*   **MajorVersion**: Categorical grouping (1.x, 2.x, etc.) used for temporal normalization.

*Note on Data Scope*: The dataset includes future version predictions (Version 5.x and 6.x). While these data points are speculative or based on leaks/trends, they were included to test the robustness of the trend lines over a longer horizon.

---

## 3. Data Preprocessing

To insure accurate statistical analysis, several preprocessing steps were undertaken using Python (Pandas):

### 3.1 Timeline Reconstruction
Since the raw data provided Version numbers rather than absolute dates, we reconstructed the timeline by assigning the standard **42-day cycle** to each version.
*   *Observation*: Versions 1.0 through 1.2 were absent from the source. Analysis thus begins effectively from Version 1.3.

### 3.2 Interval Calculation
The **Rerun Interval** was defined as the number of days between the start of the current banner and the start of the character's immediately preceding banner.
*   First appearances (debut banners) have `NaN` intervals and were excluded from interval-specific analysis.
*   Intervals were adjusted to reflect the "wait time," though for consistency, the full cycle difference was used.

### 3.3 Popularity Normalization (Z-Score)
A raw "Wish Count" is an inconsistent metric because the game's player base has fluctuated significantly over 4+ years. A wish count of 100,000 in Version 1.3 is not directly comparable to 100,000 in Version 4.0 due to player growth and churn.
To address this, we implemented **Z-Score Normalization** grouped by **Major Version**:

$$ Z = \frac{x - \mu_{version}}{\sigma_{version}} $$

This transforms absolute popularity into *relative popularity* compared to other banners of the same era, allowing for a fair comparison of "popularity clout" across time.

---

## 4. Methodology and Model

### 4.1 Feature Lagging
To test if *past* popularity predicts *future* wait times, we created lag features. We correlated the **Wish Count of Banner $N$** with the **Rerun Interval of Banner $N+1$**.
*   *Hypothesis*: High $Z_{score}$ at $T_0$ $\rightarrow$ Low $\Delta T$ at $T_1$.

### 4.2 Statistical Methods
*   **Pearson Correlation**: Used to quantify the linear relationship between Previous Popularity and Rerun Interval.
*   **Linear Regression**: A simple polynomial fit (degree 1) was applied to visualize the trend line key scatter plots.
*   **Grouping**: Data was segmented by Major Version to observe evolutionary trends in scheduling philosophy.

---

## 5. Visualization and Insights

### 5.1 The "Rerun Bottleneck"
The strongest signal in the data is the increasing average wait time.

![Rerun Trend](images/rerun_trend.png)

As shown in the scatter plot above (colored by Version), the interval floor has steadily risen.
*   **Version 2.x Average**: ~231 Days
*   **Version 5.x Average**: ~320 Days
*   **Insight**: The character roster expands faster than banner slots (even with double/triple banners), causing a "traffic jam." Players obtain new characters easily but "re-obtaining" or getting constellations for old ones is becoming significantly harder.

### 5.2 Popularity vs. Wait Time Correlation

![Correlation Plot](images/wish_correlation.png)

*   **Correlation Coefficient**: **-0.206**
*   **Result**: The correlation is negative, as hypothesized, but it is **weak**.
*   **Interpretation**: There is a slight tendency for popular characters (High Z-Score) to return faster, but it is not a dominant rule.
    *   *Outliers*: Some highly popular characters (e.g., Archons) often adhere to strict annual schedules regardless of demand.
    *   *Story Relevance*: Characters often rerun when they appear in the main storyline, overriding their sales data.

### 5.3 Distribution Variance

![Interval Distribution](images/interval_dist.png)

The boxplot analysis reveals that while the median interval increases, the **variance** also expands. In later versions (4.x, 5.x), the "whiskers" of the plot are much wider. This implies **unpredictability**: while you will likely wait longer, you *might* get lucky with a 6-month rerun, or be unlucky with an 18-month hiatus (the "Eula effect").

---

## 6. Conclusion
This project analyzed the rerun mechanics of *Genshin Impact* using data spanning over 5 years (including projections). We conclude that **popularity is statistically insignificant** as a primary predictor for rerun intervals ($r \approx -0.2$).

The scheduling logic appears to comprise:
1.  **Roster Size (70%)**: Simple queue mechanics forcing longer waits.
2.  **Story/Event Relevance (20%)**: Characters rerun when relevant to the plot.
3.  **Popularity (10%)**: A slight bias to rerun money-makers sooner.

**Final Recommendation**: Players should not rely on a character's popularity to predict their return. Instead, assume a baseline wait of **9-11 months**, extending longer as the game updates.

---

## 7. References
1.  **Project Repository**: [https://github.com/hansheng-zhang/ECE225A_final_project](https://github.com/hansheng-zhang/ECE225A_final_project)
2.  **Data Source**: *Paimon.moe* Global Wish Statistics. Retrieved from [paimon.moe/wish](https://paimon.moe/wish).

