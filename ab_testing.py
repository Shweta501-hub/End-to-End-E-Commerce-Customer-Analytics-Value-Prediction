import pandas as pd
import numpy as np
import os
from scipy import stats

# Path to the data folder
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def generate_ab_test_data(num_users=2000):
    np.random.seed(42)
    
    # 1. Assign users to Control (Old Checkout Page) or Treatment (New Checkout Page)
    groups = np.random.choice(['Control', 'Treatment'], size=num_users, p=[0.5, 0.5])
    
    # 2. Simulate Conversion Rates (purchases)
    # Control has a 10% conversion rate, Treatment has an 18% conversion rate
    conversion_rates = {'Control': 0.10, 'Treatment': 0.18}
    converted = []
    
    # 3. Simulate Purchase Amount (AOV) for converted users
    # Control AOV = $50 average, Treatment AOV = $68 average
    purchase_amounts = []
    
    for group in groups:
        # Check if user converts
        is_converted = np.random.binomial(1, conversion_rates[group])
        converted.append(is_converted)
        
        if is_converted == 1:
            if group == 'Control':
                amount = np.random.normal(50, 12)
            else:
                amount = np.random.normal(68, 12)
            purchase_amounts.append(round(max(5.0, amount), 2)) # Min purchase $5
        else:
            purchase_amounts.append(0.0)
            
    df = pd.DataFrame({
        'user_id': range(1, num_users + 1),
        'group': groups,
        'converted': converted,
        'purchase_amount': purchase_amounts
    })
    
    # Save test logs to CSV
    output_path = os.path.join(DATA_DIR, 'ab_test_data.csv')
    df.to_csv(output_path, index=False)
    print(f"Generated A/B test data for {num_users} users at: {output_path}")
    return df

def analyze_ab_test(df):
    print("\n--- A/B Test Descriptive Statistics ---")
    summary = df.groupby('group').agg(
        total_users=('user_id', 'count'),
        converted_users=('converted', 'sum'),
        conversion_rate=('converted', 'mean'),
        average_order_value=('purchase_amount', lambda x: x[x > 0].mean())
    ).reset_index()
    
    # Calculate conversion rate as percentage
    summary['conversion_rate'] = (summary['conversion_rate'] * 100).round(2)
    summary['average_order_value'] = summary['average_order_value'].round(2)
    print(summary.to_string(index=False))
    
    print("\n--- 1. Conversion Rate Analysis (Chi-Square Test) ---")
    # Build contingency table
    contingency_table = pd.crosstab(df['group'], df['converted'])
    chi2, p_val_conv, dof, expected = stats.chi2_contingency(contingency_table)
    
    print(f"Chi-Square Statistic: {chi2:.4f}")
    print(f"P-value: {p_val_conv:.6f}")
    
    if p_val_conv < 0.05:
        print("RESULT: Statistically Significant! We reject the Null Hypothesis. The new checkout design significantly improved conversion rates.")
    else:
        print("RESULT: Not Statistically Significant. We fail to reject the Null Hypothesis. The conversion rate difference could be due to random chance.")
        
    print("\n--- 2. Average Order Value (AOV) Analysis (Two-Sample T-Test) ---")
    # Filter purchase amounts for converted users only
    control_purchases = df[(df['group'] == 'Control') & (df['converted'] == 1)]['purchase_amount']
    treatment_purchases = df[(df['group'] == 'Treatment') & (df['converted'] == 1)]['purchase_amount']
    
    t_stat, p_val_aov = stats.ttest_ind(control_purchases, treatment_purchases, equal_var=False)
    
    print(f"T-Statistic: {t_stat:.4f}")
    print(f"P-value: {p_val_aov:.6f}")
    
    if p_val_aov < 0.05:
        print("RESULT: Statistically Significant! We reject the Null Hypothesis. The new checkout design significantly increased the average order value.")
    else:
        print("RESULT: Not Statistically Significant. We fail to reject the Null Hypothesis. The difference in purchase amount is not statistically meaningful.")

def main():
    print("--- Starting A/B Testing Simulator & Analyzer ---")
    df = generate_ab_test_data()
    analyze_ab_test(df)

if __name__ == "__main__":
    main()
