import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Define data directory path
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

# 1. Load data
print("--- Loading Data ---")
customers = pd.read_csv(os.path.join(DATA_DIR, 'customers.csv'))
orders = pd.read_csv(os.path.join(DATA_DIR, 'orders.csv'))
order_items = pd.read_csv(os.path.join(DATA_DIR, 'order_items.csv'))

# Convert order_date to datetime
orders['order_date'] = pd.to_datetime(orders['order_date'])

# Calculate spend per order item
order_items['item_spend'] = (order_items['quantity'] * order_items['unit_price']) - order_items['discount_amount']
order_spend = order_items.groupby('order_id')['item_spend'].sum().reset_index()
orders_full = orders.merge(order_spend, on='order_id', how='left').fillna(0)

# 2. Split data into "Observation Period" and "Prediction Period"
print("--- Splitting Data into Time Windows ---")
cut_off_date = pd.to_datetime('2026-01-01')

orders_2025 = orders_full[orders_full['order_date'] < cut_off_date]
orders_2026 = orders_full[orders_full['order_date'] >= cut_off_date]

# 3. Build Features (from 2025 data)
print("--- Engineering Features (from 2025) ---")
ref_date_2025 = cut_off_date
recency_2025 = orders_2025.groupby('customer_id')['order_date'].max().reset_index()
recency_2025['Recency'] = (ref_date_2025 - recency_2025['order_date']).dt.days
recency_2025 = recency_2025[['customer_id', 'Recency']]

frequency_2025 = orders_2025.groupby('customer_id')['order_id'].nunique().reset_index().rename(columns={'order_id': 'Frequency'})
monetary_2025 = orders_2025.groupby('customer_id')['item_spend'].sum().reset_index().rename(columns={'item_spend': 'Monetary'})

# Combine features
features = customers.merge(recency_2025, on='customer_id', how='left')
features = features.merge(frequency_2025, on='customer_id', how='left')
features = features.merge(monetary_2025, on='customer_id', how='left')

# If customer had no orders in 2025, fill with defaults
features['Recency'] = features['Recency'].fillna(365)
features['Frequency'] = features['Frequency'].fillna(0)
features['Monetary'] = features['Monetary'].fillna(0)

# 4. Build Target (Spend in 2026)
print("--- Creating Target Variable (Spend in 2026) ---")
target_2026 = orders_2026.groupby('customer_id')['item_spend'].sum().reset_index().rename(columns={'item_spend': 'Future_Spend'})

# Merge features and target
dataset = features.merge(target_2026, on='customer_id', how='left').fillna(0)

# 5. Prepare data for Machine Learning
X = dataset[['age', 'region', 'acquisition_channel', 'Recency', 'Frequency', 'Monetary']]
y = dataset['Future_Spend']

# Preprocess categorical features
categorical_features = ['region', 'acquisition_channel']
numeric_features = ['age', 'Recency', 'Frequency', 'Monetary']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', 'passthrough', numeric_features),
        ('cat', OneHotEncoder(drop='first'), categorical_features)
    ])

# 6. Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 7. Train Model
print("--- Training Random Forest Regressor ---")
model = Pipeline(steps=[('preprocessor', preprocessor),
                        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))])

model.fit(X_train, y_train)

# 8. Evaluate Model
y_pred = model.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print(f"\nModel Evaluation Results:")
print(f"Root Mean Squared Error (RMSE): ${rmse:.2f}")
print(f"R-squared Score (R2): {r2:.4f}")

# 9. Apply to all customers & save predictions
print("\n--- Saving Predictions ---")
dataset['Predicted_Future_Spend'] = model.predict(X)
output_file = os.path.join(DATA_DIR, 'clv_predictions.csv')
dataset[['customer_id', 'Future_Spend', 'Predicted_Future_Spend']].to_csv(output_file, index=False)
print(f"Saved CLV predictions to: {output_file}")
