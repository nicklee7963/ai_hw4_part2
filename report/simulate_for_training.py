import pandas as pd
import numpy as np
import random
import os

# 檢查依賴檔案是否存在
if not os.path.exists("exercise_movement.csv"):
    print("❌ 錯誤：找不到 'exercise_movement.csv'，請確保檔案在同目錄下。")
    exit()

# 讀取動作資料庫
df = pd.read_csv("exercise_movement.csv")

# 依照部位拆分 DataFrame，加速後續隨機選取
parts_dfs = {
    "胸部": df[df["訓練部位"] == "胸部"],
    "背部": df[df["訓練部位"] == "背部"],
    "肩部": df[df["訓練部位"] == "肩部"],
    "手臂": df[df["訓練部位"] == "手臂"],
    "腿部": df[df["訓練部位"] == "腿部"],
    "核心": df[df["訓練部位"] == "核心"]
}

# 準備存放資料的容器
data = {
    '姓名': [],
    '性別': [],
    '年紀': [],
    '體重': [],
    
    # 最大能力值 (Feature)
    'chest_max': [],
    'shoulder_max': [],
    'hand_max': [],
    'back_max': [],
    'belly_max': [],
    'leg_max': [],
    
    # 當前體力值 (Feature)
    '胸體力值': [],
    '肩體力值': [],
    '手體力值': [],
    '背體力值': [],
    '腹體力值': [],
    '腿體力值': [],
    
    # 標籤 (Label)
    '菜單': [],
    '菜單評分': [],
    '難度': []
}

# ==========================================
# ⚙️ 設定生成數量
simulate_num = 10000 
# ==========================================

print(f"🚀 開始生成 {simulate_num} 筆訓練資料，請稍候...")

for i in range(simulate_num):
    # --- 1. 生成隨機玩家屬性 ---
    data['姓名'].append(f"User_{i}")
    data['性別'].append(random.choice([0, 1]))
    data['年紀'].append(random.randint(18, 65))
    data['體重'].append(round(random.uniform(50.0, 100.0), 1))
    
    # 生成最大肌力 (200~500)
    vals = [random.randint(200, 500) for _ in range(6)]
    data['chest_max'].append(vals[0])
    data['shoulder_max'].append(vals[1])
    data['back_max'].append(vals[2])
    data['hand_max'].append(vals[3])
    data['belly_max'].append(vals[4])
    data['leg_max'].append(vals[5])
    
    # 假設初始體力 = 最大肌力 (或是你可以改成隨機剩餘體力)
    data['胸體力值'].append(vals[0])
    data['肩體力值'].append(vals[1])
    data['背體力值'].append(vals[2])
    data['手體力值'].append(vals[3])
    data['腹體力值'].append(vals[4])
    data['腿體力值'].append(vals[5])
    
    # 隨機難度偏好 (1~5)
    user_difficulty = random.randint(1, 5)
    data['難度'].append(user_difficulty)

    # --- 2. 生成菜單 (邏輯核心) ---
    menu = {}
    total_score = 0
    
    # 定義部位對應的體力欄位與資料庫
    body_parts = [
        ("chest", "胸部", vals[0]),
        ("back", "背部", vals[2]),
        ("shoulder", "肩部", vals[1]),
        ("hand", "手臂", vals[3]),
        ("leg", "腿部", vals[5]),
        ("belly", "核心", vals[4])
    ]

    for en_name, ch_name, current_coda in body_parts:
        part_menu = []
        part_df = parts_dfs[ch_name]
        part_length = len(part_df)
        
        # 計算該部位的完美分數 (作為分母)
        part_perfect_score = 0
        for _, row in part_df.iterrows():
            if row["部位消耗體力值"] > 0:
                part_perfect_score += row["部位得到肌肉量"] / row["部位消耗體力值"]
        
        if part_perfect_score == 0: part_perfect_score = 1 # 避免除以零

        part_actual_score = 0
        max_attempt = 50
        current_attempt = 0
        
        # 貪婪演算法隨機選動作
        while current_coda > 0 and current_attempt < max_attempt:
            current_attempt += 1
            if part_length == 0: break
            
            dummy = random.randint(0, part_length - 1)
            exercise = part_df.iloc[dummy]
            
            # 判斷條件：沒重複過、體力夠扣、難度符合
            if (exercise["動作名稱"] not in part_menu) and \
               (current_coda - exercise["部位消耗體力值"] >= 0) and \
               (exercise["動作難度"] <= user_difficulty):
                
                current_coda -= exercise["部位消耗體力值"]
                part_menu.append(exercise["動作名稱"])
                
                if exercise["部位消耗體力值"] > 0:
                    part_actual_score += exercise["部位得到肌肉量"] / exercise["部位消耗體力值"]
            
            # 隨機中斷 (模擬真實用戶可能不想做滿)
            if random.choice([0, 1]) == 0:
                break
        
        menu[f"{en_name}_menu"] = part_menu
        # 每個部位滿分 20 分，總分 120 分
        total_score += (part_actual_score / part_perfect_score) * 20

    data['菜單'].append(menu)
    data['菜單評分'].append(total_score)

    # 顯示進度 (每1000筆印一次)
    if (i + 1) % 1000 == 0:
        print(f"已生成 {i + 1} / {simulate_num} 筆...")

# --- 3. 輸出 CSV ---
df_output = pd.DataFrame(data)
output_filename = "training_data.csv"

try:
    df_output.to_csv(output_filename, index=False, encoding='utf-8')
    print(f"\n✅ 成功！已生成 '{output_filename}' (共 {len(df_output)} 筆資料)")
    # 簡單預覽
    print("前 3 筆資料預覽：")
    print(df_output[['姓名', '難度', '菜單評分']].head(3))
except Exception as e:
    print(f"❌ 寫入 CSV 發生錯誤: {e}")
