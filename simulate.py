import pandas as pd
import numpy as np
import random

df = pd.read_csv("exercise_movement.csv")


chest_df = df[df["訓練部位"] == "胸部"]
chest_length = len(chest_df)
back_df = df[df["訓練部位"]=="背部"]
back_length = len(back_df)
shoulder_df = df[df["訓練部位"]=="肩部"]
shoulder_length = len(shoulder_df)
hand_df = df[df["訓練部位"]=="手臂"]
hand_length = len(hand_df)
leg_df = df[df["訓練部位"]=="腿部"]
leg_length = len(leg_df)
belly_df = df[df["訓練部位"]=="核心"]
belly_length = len(belly_df)

'''
print(chest_df.info())
print(back_df.info())
print(shoulder_df.info())
print(hand_df.info())
print(leg_df.info())
print(belly_df.info())
'''





data = {
    '姓名': [],
    '性別':[],
    '年紀': [],
    '體重': [],

    # '胸肌肉量': [],
    # '肩肌肉量': [],
    # '手肌肉量': [],
    # '背肌肉量': [],
    # '腹肌肉量': [],
    # '腿肌肉量': [],

    'chest_max': [],
    'shoulder_max': [],
    'hand_max': [],
    'back_max': [],
    'belly_max': [],
    'leg_max': [],
    '胸體力值': [],
    '肩體力值': [],
    '手體力值': [],
    '背體力值': [],
    '腹體力值': [],
    '腿體力值': [],
    '菜單': [],
    '菜單評分': [],
    '難度': []

}


simulate_num = 10
for i in range(simulate_num):
    data['姓名'].append(i)
    data['性別'].append(random.choice([0, 1]))
    data['年紀'].append(random.randint(18, 65))
    data['體重'].append(round(random.uniform(50.0, 100.0), 1))  # generate fload
    x0 = random.randint(200, 500)
    data['chest_max'].append(x0)
    x1 = random.randint(200, 500)
    data['shoulder_max'].append(x1)
    x2 = random.randint(200, 500)
    data['back_max'].append(x2)
    x3 = random.randint(200, 500)
    data['hand_max'].append(x3)
    x4 = random.randint(200, 500)
    data['belly_max'].append(x4)
    x5 = random.randint(200, 500)
    data['leg_max'].append(x5)

    data['胸體力值'].append(x0)
    data['肩體力值'].append(x1)
    data['背體力值'].append(x2)
    data['手體力值'].append(x3)
    data['腹體力值'].append(x4)
    data['腿體力值'].append(x5)


    data['難度'].append(random.randint(1, 5))





    # ====== 胸部 ======

    menu = {}
    score = 0

    # 胸部
    chest_menu = []
    chest_coda = data["胸體力值"][i]

    chest_actual_score = 0
    chest_perfect_score = 0
    for j in range(chest_length):
        chest_perfect_score += chest_df.iloc[j]["部位得到肌肉量"] / chest_df.iloc[j]["部位消耗體力值"]

    max_attempt = 50
    current_attempt = 0
    while chest_coda > 0 and current_attempt < max_attempt:
        current_attempt += 1
        dummy = random.randint(0, chest_length - 1)
        exercise = chest_df.iloc[dummy]
        if (exercise["動作名稱"] not in chest_menu) and (chest_coda - exercise["部位消耗體力值"] >= 0) and exercise["動作難度"] <= data["難度"][i]:
            chest_coda -= exercise["部位消耗體力值"]
            chest_menu.append(exercise["動作名稱"])
            chest_actual_score += exercise["部位得到肌肉量"] / exercise["部位消耗體力值"]
        if random.choice([0, 1]) == 0:
            break
    menu["chest_menu"] = chest_menu
    score += chest_actual_score / chest_perfect_score * 20




    # ====== 背部 ======

    back_menu = []
    back_coda = data["背體力值"][i]

    back_actual_score = 0
    back_perfect_score = 0
    for j in range(back_length):
        back_perfect_score += back_df.iloc[j]["部位得到肌肉量"] / back_df.iloc[j]["部位消耗體力值"]

    max_attempt = 50
    current_attempt = 0
    while back_coda > 0 and current_attempt < max_attempt:
        current_attempt += 1
        dummy = random.randint(0, back_length - 1)
        exercise = back_df.iloc[dummy]
        if (exercise["動作名稱"] not in back_menu) and (back_coda - exercise["部位消耗體力值"] >= 0) and exercise["動作難度"] <= data["難度"][i]:
            back_coda -= exercise["部位消耗體力值"]
            back_menu.append(exercise["動作名稱"])
            back_actual_score += exercise["部位得到肌肉量"] / exercise["部位消耗體力值"]
        if random.choice([0, 1]) == 0:
            break
    menu["back_menu"] = back_menu
    score += back_actual_score / back_perfect_score * 20




    # ====== 肩部 ======

    shoulder_menu = []
    shoulder_coda = data["肩體力值"][i]

    shoulder_actual_score = 0
    shoulder_perfect_score = 0
    for j in range(shoulder_length):
        shoulder_perfect_score += shoulder_df.iloc[j]["部位得到肌肉量"] / shoulder_df.iloc[j]["部位消耗體力值"]

    max_attempt = 50
    current_attempt = 0
    while shoulder_coda > 0 and current_attempt < max_attempt:
        current_attempt += 1
        dummy = random.randint(0, shoulder_length - 1)
        exercise = shoulder_df.iloc[dummy]
        if (exercise["動作名稱"] not in shoulder_menu) and (shoulder_coda - exercise["部位消耗體力值"] >= 0) and exercise["動作難度"] <= data["難度"][i]:
            shoulder_coda -= exercise["部位消耗體力值"]
            shoulder_menu.append(exercise["動作名稱"])
            shoulder_actual_score += exercise["部位得到肌肉量"] / exercise["部位消耗體力值"]
        if random.choice([0, 1]) == 0:
            break
    menu["shoulder_menu"] = shoulder_menu
    score += shoulder_actual_score / shoulder_perfect_score * 20




    # ====== 手臂 ======

    hand_menu = []
    hand_coda = data["手體力值"][i]

    hand_actual_score = 0
    hand_perfect_score = 0
    for j in range(hand_length):
        hand_perfect_score += hand_df.iloc[j]["部位得到肌肉量"] / hand_df.iloc[j]["部位消耗體力值"]

    max_attempt = 50
    current_attempt = 0
    while hand_coda > 0 and current_attempt < max_attempt:
        current_attempt += 1
        dummy = random.randint(0, hand_length - 1)
        exercise = hand_df.iloc[dummy]
        if (exercise["動作名稱"] not in hand_menu) and (hand_coda - exercise["部位消耗體力值"] >= 0) and exercise["動作難度"] <= data["難度"][i]:
            hand_coda -= exercise["部位消耗體力值"]
            hand_menu.append(exercise["動作名稱"])
            hand_actual_score += exercise["部位得到肌肉量"] / exercise["部位消耗體力值"]
        if random.choice([0, 1]) == 0:
            break
    menu["hand_menu"] = hand_menu
    score += hand_actual_score / hand_perfect_score * 20




    # ====== 腿部 ======

    leg_menu = []
    leg_coda = data["腿體力值"][i]

    leg_actual_score = 0
    leg_perfect_score = 0
    for j in range(leg_length):
        leg_perfect_score += leg_df.iloc[j]["部位得到肌肉量"] / leg_df.iloc[j]["部位消耗體力值"]

    max_attempt = 50
    current_attempt = 0
    while leg_coda > 0 and current_attempt < max_attempt:
        current_attempt += 1
        dummy = random.randint(0, leg_length - 1)
        exercise = leg_df.iloc[dummy]
        if (exercise["動作名稱"] not in leg_menu) and (leg_coda - exercise["部位消耗體力值"] >= 0) and exercise["動作難度"] <= data["難度"][i]:
            leg_coda -= exercise["部位消耗體力值"]
            leg_menu.append(exercise["動作名稱"])
            leg_actual_score += exercise["部位得到肌肉量"] / exercise["部位消耗體力值"]
        if random.choice([0, 1]) == 0:
            break
    menu["leg_menu"] = leg_menu
    score += leg_actual_score / leg_perfect_score * 20




    # ====== 核心（腹部） ======

    belly_menu = []
    belly_coda = data["腹體力值"][i]

    belly_actual_score = 0
    belly_perfect_score = 0
    for j in range(belly_length):
        belly_perfect_score += belly_df.iloc[j]["部位得到肌肉量"] / belly_df.iloc[j]["部位消耗體力值"]

    max_attempt = 50
    current_attempt = 0
    while belly_coda > 0 and current_attempt < max_attempt:
        current_attempt += 1
        dummy = random.randint(0, belly_length - 1)
        exercise = belly_df.iloc[dummy]
        if (exercise["動作名稱"] not in belly_menu) and (belly_coda - exercise["部位消耗體力值"] >= 0) and exercise["動作難度"] <= data["難度"][i]:
            belly_coda -= exercise["部位消耗體力值"]
            belly_menu.append(exercise["動作名稱"])
            belly_actual_score += exercise["部位得到肌肉量"] / exercise["部位消耗體力值"]
        if random.choice([0, 1]) == 0:
            break
    menu["belly_menu"] = belly_menu
    score += belly_actual_score / belly_perfect_score * 20




    # ====== 加入總結 ======

    data["菜單"].append(menu)
    data["菜單評分"].append(score)


    
 


df_output = pd.DataFrame(data)

output_filename = "simulate.csv"

# 3. 使用 .to_csv() 方法將 DataFrame 寫入 CSV 檔案
# index=False 告訴 Pandas 不要將 DataFrame 左邊的索引（0, 1, 2...）寫入檔案
try:
    df_output.to_csv(output_filename, index=False, encoding='utf-8')
    print(f"✅ 檔案 '{output_filename}' 成功創建。")
    print("檔案內容如下:")
    # 讀取檔案內容並印出，以便您在終端機中確認
    with open(output_filename, 'r', encoding='utf-8') as f:
        print(f.read())
        
except Exception as e:
    print(f"❌ 寫入 CSV 檔案時發生錯誤: {e}")

# 執行完畢後，在您的程式碼所在目錄下會多出一個名為 hello_world_output.csv 的檔案。

import random

class Player:
    def __init__(self, name, difficulty=None):
        # 1. 強制重設隨機體質，避免被 AI 模型的 seed(42) 影響
        random.seed() 
        
        self.name = name
        
        # --- 基本屬性 ---
        self.gender = random.choice([0, 1])
        self.age = random.randint(18, 65)
        self.weight = round(random.uniform(50.0, 100.0), 1)
        self.height = round(random.uniform(150, 190), 1)
        
        if difficulty:
            self.difficulty = difficulty
        else:
            self.difficulty = random.randint(1, 5)

        # --- 訓練累積次數 (初始化為 0) ---
        self.training_chest = 0
        self.training_back = 0
        self.training_leg = 0
        self.training_hand = 0
        self.training_shoulder = 0
        self.training_belly = 0

        # --- 最大肌力值 (200-500) ---
        self.chest_max = random.randint(200, 500)
        self.shoulder_max = random.randint(200, 500)
        self.hand_max = random.randint(200, 500)
        self.back_max = random.randint(200, 500)
        self.belly_max = random.randint(200, 500)
        self.leg_max = random.randint(200, 500)

        # --- 當前體力值 (初始等於最大值) ---
        self.energy_chest = self.chest_max
        self.energy_shoulder = self.shoulder_max
        self.energy_hand = self.hand_max
        self.energy_back = self.back_max
        self.energy_belly = self.belly_max
        self.energy_leg = self.leg_max

    def get_status(self):
        """顯示玩家狀態"""
        sex_str = "男" if self.gender == 1 else "女"
        print(f"=== 玩家: {self.name} ===")
        print(f"基本: {sex_str} | {self.age}歲 | {self.height}cm | {self.weight}kg")
        print(f"難度: Lv.{self.difficulty}")
        print(f"體質: 胸肌{self.chest_max} / 腿肌{self.leg_max} / 背肌{self.back_max}")
        print(f"  肩部: {self.shoulder_max:<4} | 手臂: {self.hand_max:<4} | 核心: {self.belly_max:<4}")
        print("-" * 25)

    def to_model_input(self):
        """
        【關鍵方法】
        將玩家的屬性轉換成 Random Forest 模型看得懂的字典格式 (Dict)。
        這裡的 Key 必須跟當初訓練 CSV 的欄位名稱一模一樣！
        """
        return {
            # --- 基本屬性 ---
            '性別': self.gender,
            '年紀': self.age,
            '體重': self.weight,
            '難度': self.difficulty,

            # --- 最大能力值 (直接對應 feature name) ---
            'chest_max': self.chest_max,
            'shoulder_max': self.shoulder_max,
            'hand_max': self.hand_max,
            'back_max': self.back_max,
            'belly_max': self.belly_max,
            'leg_max': self.leg_max,

            # --- 當前體力值 (對應中文 feature name) ---
            '胸體力值': self.energy_chest,
            '肩體力值': self.energy_shoulder,
            '手體力值': self.energy_hand,
            '背體力值': self.energy_back,
            '腹體力值': self.energy_belly,
            '腿體力值': self.energy_leg
        }
# --- 測試區塊 ---
if __name__ == "__main__":
    # 創建一個玩家
    p1 = Player("AI_Test_User", difficulty=3)
    p1.get_status()
    
    # 測試輸出給模型的資料
    print("\n給模型的資料格式:")
    print(p1.to_model_input())
