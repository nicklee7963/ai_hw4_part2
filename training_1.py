import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import random
import joblib
import os
from typing import Dict, List, Any

# --- 設定 ---
MODEL_FILENAME = "fitness_ai_model.pkl"
CSV_FILENAME = "processed_dataset.csv"
RANDOM_SEED = 42

np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

# 全域變數
rf_model = None
ACTION_COLUMNS = []
FEATURES = []
ACTION_NAMES = []

# --- 1. 模型初始化 (載入或訓練) ---
def initialize_model():
    global rf_model, ACTION_COLUMNS, FEATURES, ACTION_NAMES
    
    # A. 嘗試讀取已儲存的模型
    if os.path.exists(MODEL_FILENAME):
        print(f"[AI] 載入模型: {MODEL_FILENAME}...")
        try:
            saved_data = joblib.load(MODEL_FILENAME)
            rf_model = saved_data['model']
            ACTION_COLUMNS = saved_data['action_columns']
            FEATURES = saved_data['features']
            ACTION_NAMES = [col.split('_')[1] for col in ACTION_COLUMNS]
            print("[AI] 模型載入成功！")
            return
        except Exception as e:
            print(f"[AI] 讀取失敗: {e}，準備重新訓練...")

    # B. 重新訓練模型
    print("[AI] 開始訓練新模型...")
    if not os.path.exists(CSV_FILENAME):
        print(f"[錯誤] 找不到 {CSV_FILENAME}，AI 無法運作。")
        return

    df = pd.read_csv(CSV_FILENAME)
    
    # 定義欄位
    PLAYER_ATTRIBUTES = [
        '性別', '年紀', '體重',
        'chest_max', 'shoulder_max', 'hand_max', 'back_max', 'belly_max', 'leg_max',
        '胸體力值', '肩體力值', '手體力值', '背體力值', '腹體力值', '腿體力值', '難度'
    ]
    ACTION_COLUMNS = [col for col in df.columns if col.startswith('act_')]
    TARGET_COLUMN = '菜單評分'
    FEATURES = PLAYER_ATTRIBUTES + ACTION_COLUMNS
    ACTION_NAMES = [col.split('_')[1] for col in ACTION_COLUMNS]

    # 訓練
    X = df[FEATURES]
    y = df[TARGET_COLUMN]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_SEED)

    rf_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=RANDOM_SEED)
    rf_model.fit(X_train, y_train)
    print("[AI] 訓練完成。")

    # 儲存
    joblib.dump({
        'model': rf_model,
        'action_columns': ACTION_COLUMNS,
        'features': FEATURES
    }, MODEL_FILENAME)
    print(f"[AI] 模型已儲存。")

# 初始化時直接執行
initialize_model()


# --- 2. 核心預測邏輯 (內部使用) ---
def _predict_raw_menu(player_profile: Dict[str, Any], num_candidates=1000):
    if rf_model is None: return [], 0

    best_score = -np.inf
    best_menu = []
    base_data = pd.Series(player_profile)

    for _ in range(num_candidates):
        num_actions = random.randint(3, 7)
        selected_actions = random.sample(ACTION_NAMES, k=num_actions)
        
        action_features = {col: 0 for col in ACTION_COLUMNS}
        current_menu_list = []
        for action_name in selected_actions:
            col_name = f'act_{action_name}'
            if col_name in action_features:
                action_features[col_name] = 1
                current_menu_list.append(action_name)

        menu_features = pd.Series(action_features).combine_first(base_data)
        X_predict = pd.DataFrame([menu_features[FEATURES].values], columns=FEATURES)
        predicted_score = rf_model.predict(X_predict)[0]

        if predicted_score > best_score:
            best_score = predicted_score
            best_menu = current_menu_list
            
    return best_menu, best_score


# --- 3. 外部接口 (給 Game 呼叫) ---
def get_recommendation_list(player_obj):
    """
    接收 Player 物件，回傳 (動作列表 List, 分數 float)
    """
    # 1. 自動提取 Player 屬性轉成字典
    profile = {
        '性別': getattr(player_obj, 'gender', 1),
        '年紀': getattr(player_obj, 'age', 20),
        '體重': getattr(player_obj, 'weight', 70.0),
        '難度': getattr(player_obj, 'difficulty', 3),
        
        'chest_max': getattr(player_obj, 'chest_max', 300),
        'shoulder_max': getattr(player_obj, 'shoulder_max', 300),
        'hand_max': getattr(player_obj, 'hand_max', 300),
        'back_max': getattr(player_obj, 'back_max', 300),
        'belly_max': getattr(player_obj, 'belly_max', 300),
        'leg_max': getattr(player_obj, 'leg_max', 300),
        
        '胸體力值': getattr(player_obj, 'energy_chest', 300),
        '肩體力值': getattr(player_obj, 'energy_shoulder', 300),
        '手體力值': getattr(player_obj, 'energy_hand', 300),
        '背體力值': getattr(player_obj, 'energy_back', 300),
        '腹體力值': getattr(player_obj, 'energy_belly', 300),
        '腿體力值': getattr(player_obj, 'energy_leg', 300),
    }

    # 2. 呼叫預測
    return _predict_raw_menu(profile)
