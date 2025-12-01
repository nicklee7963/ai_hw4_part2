# preprocess.py
import pandas as pd
import ast

# 1. 讀取模擬出來的原始資料
print("正在讀取 training_data.csv ...")
try:
    df = pd.read_csv("training_data.csv")
except FileNotFoundError:
    print("❌ 找不到 training_data.csv，請先執行 simulate_gen.py")
    exit()

# 2. 找出所有出現過的動作名稱 (建立 One-Hot Columns)
all_actions = set()

# 先把字串轉回 Dictionary，並收集所有動作
parsed_menus = []
for menu_str in df['菜單']:
    # 使用 ast.literal_eval 安全地將字串轉為 Dict
    menu_dict = ast.literal_eval(menu_str)
    parsed_menus.append(menu_dict)
    
    # 遍歷所有部位的動作列表
    for part_list in menu_dict.values():
        for action in part_list:
            all_actions.add(action)

sorted_actions = sorted(list(all_actions))
print(f"✅ 偵測到 {len(sorted_actions)} 種不同的健身動作。")

# 3. 建立動作的 One-Hot Encoding (有做該動作=1, 沒做=0)
# 建立一個空的 DataFrame 來裝動作標籤
action_df_data = []

for menu_dict in parsed_menus:
    # 每一列先全部填 0
    row_data = {f"act_{action}": 0 for action in sorted_actions}
    
    # 將有做到的動作填 1
    for part_list in menu_dict.values():
        for action in part_list:
            row_data[f"act_{action}"] = 1
    
    action_df_data.append(row_data)

action_df = pd.DataFrame(action_df_data)

# 4. 合併原始資料與動作標籤
# 只保留數值型特徵，去掉原本的文字型 '菜單' 欄位
cols_to_keep = [
    '性別', '年紀', '體重', '難度',
    'chest_max', 'shoulder_max', 'hand_max', 'back_max', 'belly_max', 'leg_max',
    '胸體力值', '肩體力值', '手體力值', '背體力值', '腹體力值', '腿體力值',
    '菜單評分'
]

final_df = pd.concat([df[cols_to_keep], action_df], axis=1)

# 5. 輸出結果
output_filename = "processed_dataset.csv"
final_df.to_csv(output_filename, index=False)
print(f"🎉 處理完成！已儲存為 '{output_filename}'，可以用來訓練了。")
