# train_multi_models.py
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# 引入五種模型
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor

# --- 設定 ---
CSV_FILENAME = "processed_dataset.csv"
RANDOM_SEED = 42
MODEL_DIR = "models" # 模型存放資料夾

# 建立存放模型的資料夾
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

# --- 1. 準備資料 ---
if not os.path.exists(CSV_FILENAME):
    print(f"❌ 找不到 {CSV_FILENAME}，請先執行 preprocess.py")
    exit()

print("讀取資料中...")
df = pd.read_csv(CSV_FILENAME)

# 定義 Feature (X) 和 Label (y)
# 排除 '菜單評分' 以外的所有欄位都是 Feature
target_col = '菜單評分'
feature_cols = [c for c in df.columns if c != target_col]

X = df[feature_cols]
y = df[target_col]

# 切分訓練集跟測試集
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_SEED
)

print(f"資料筆數: {len(df)} | 特徵數量: {len(feature_cols)}")
print("-" * 50)

# --- 2. 定義模型清單 ---
models = {
    "RandomForest": RandomForestRegressor(n_estimators=100, max_depth=10, random_state=RANDOM_SEED),
    "DecisionTree": DecisionTreeRegressor(max_depth=10, random_state=RANDOM_SEED),
    "XGBoost": XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=RANDOM_SEED),
    "LinearRegression": LinearRegression(),
    "GradientBoosting": GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=RANDOM_SEED)
}

# --- 3. 迴圈訓練並儲存 ---
results = []

for name, model in models.items():
    print(f"🔥 正在訓練 {name} ...")
    
    # 訓練
    model.fit(X_train, y_train)
    
    # 預測
    y_pred = model.predict(X_test)
    
    # 評估
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"   MSE: {mse:.4f} | R2 Score: {r2:.4f}")
    
    # 儲存模型 (包含特徵欄位名稱，方便之後預測時對照)
    save_path = os.path.join(MODEL_DIR, f"{name}.pkl")
    model_data = {
        'model': model,
        'features': feature_cols,
        'action_columns': [c for c in feature_cols if c.startswith('act_')]
    }
    joblib.dump(model_data, save_path)
    print(f"   ✅ 模型已儲存至: {save_path}")
    print("-" * 50)
    
    results.append({'Model': name, 'MSE': mse, 'R2': r2})

# --- 4. 總結比較 ---
print("\n=== 🏆 模型效能排行榜 ===")
results_df = pd.DataFrame(results).sort_values(by='R2', ascending=False)
print(results_df)
