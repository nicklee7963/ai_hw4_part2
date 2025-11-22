import pandas as pd
import openai
import os
import time
from training_1 import get_recommendation_list

# ==========================================
# 🔑 OpenAI API 設定 (動態輸入版)
# ==========================================
client = None # 一開始設為空值

def setup_openai(user_key):
    """
    由主程式呼叫此函式來設定 API Key
    """
    global client
    if user_key and user_key.strip():
        try:
            client = openai.OpenAI(api_key=user_key.strip())
            print("✅ OpenAI API Key 設定完成！")
        except Exception as e:
            print(f"⚠️ Key 格式似乎有誤: {e}")
            client = None
    else:
        print("⚠️ 未輸入 Key，AI 功能將無法使用。")
        client = None
# ==========================================

# --- 1. 載入動作資料庫 ---
EXERCISE_DB = {}
try:
    df = pd.read_csv("exercise_movement.csv")
    for _, row in df.iterrows():
        key = row["動作名稱"]
        EXERCISE_DB[key] = {
            "部位": row["訓練部位"],
            "消耗": row["部位消耗體力值"],
            "難度": row["動作難度"]
        }
except FileNotFoundError:
    print("[錯誤] 找不到 exercise_movement.csv")

# --- 2. OpenAI 功能 ---
def explain_action_with_openai(action_name, part):
    if not client:
        print(f"\n(因未設定 API Key，跳過 AI 講解: {action_name})")
        return

    print(f"\n🤖 AI 教練正在分析【{action_name}】的動作細節...")
    prompt = (
        f"請簡短介紹健身動作「{action_name}」(訓練部位：{part})。"
        f"請包含兩點：1. 這個動作的主要訓練主旨。"
        f"2. 操作時的一個關鍵注意事項。"
        f"字數控制在 100 字以內，語氣要像個專業且熱血的教練。"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        explanation = response.choices[0].message.content.strip()
        print("-" * 40)
        print(f"📢 教練指導：\n{explanation}")
        print("-" * 40)
        time.sleep(1) 
    except Exception as e:
        print(f"(AI 解說連線失敗: {e})")

def generate_quiz_with_openai(action_name):
    if not client:
        return f"做 {action_name} 會消耗體力嗎？", True

    prompt = (
        f"請針對健身動作 '{action_name}' 出一題簡單的『是非題』，"
        f"格式必須為：題目|T 或 題目|F (T代表True, F代表False)。"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=100
        )
        content = response.choices[0].message.content.strip()
        if "|" in content:
            q, a = content.split("|")
            return q, ("T" in a.upper())
        else:
            return f"{action_name} 是一個好動作嗎？", True
    except:
        return f"做 {action_name} 會消耗體力嗎？", True

# --- 3. 主訓練流程 ---
def start_training_session(player):
    trained_log = [] 

    p_name = getattr(player, 'name', 'Player')
    print(f"\n{'='*10} 🏋️ {p_name} 的訓練時間 🏋️ {'='*10}")

    print("正在連線 AI 推薦系統 (Random Forest)...")
    action_list, score = get_recommendation_list(player)

    print(f"\n=== 📋 AI 智能菜單 (評分: {score:.1f}) ===")
    if not action_list:
        print("(教練建議：今天休息，無需訓練)")
        return [] 

    menu_options = [] 
    temp_display = {} 
    
    idx_counter = 1
    for action in action_list:
        if action in EXERCISE_DB:
            info = EXERCISE_DB[action]
            part = info["部位"]
            cost = info["消耗"]
            display_str = f"({idx_counter}) {action} [耗能:{cost}]"
            if part not in temp_display: temp_display[part] = []
            temp_display[part].append(display_str)
            menu_options.append(action)
            idx_counter += 1
        else:
            if "未知" not in temp_display: temp_display["未知"] = []
            temp_display["未知"].append(f"({idx_counter}) {action} (?)")
            menu_options.append(action)
            idx_counter += 1

    for part, items in temp_display.items():
        print(f"【{part}】: {', '.join(items)}")
    
    print("-" * 40)
    print(f"(輸入 1 ~ {len(menu_options)} 選擇動作，輸入 0 結束訓練)")

    while True:
        try:
            user_input = input(f"請輸入編號 (0-{len(menu_options)}): ").strip()
            
            if user_input == '0':
                print("結束訓練。")
                break
            
            if not user_input.isdigit():
                print("❌ 請輸入數字！")
                continue
                
            choice_idx = int(user_input) - 1 
            
            if 0 <= choice_idx < len(menu_options):
                target_action = menu_options[choice_idx]
                
                if target_action not in EXERCISE_DB:
                    print("❌ 資料庫錯誤")
                    continue
                
                info = EXERCISE_DB[target_action]
                cost = info["消耗"]
                part_name = info["部位"]
                
                part_map = {
                    "胸部": "energy_chest", "背部": "energy_back", 
                    "肩部": "energy_shoulder", "手臂": "energy_hand", 
                    "腿部": "energy_leg", "核心": "energy_belly"
                }
                attr_name = part_map.get(part_name)
                current_energy = getattr(player, attr_name, 0)
                
                if current_energy < cost:
                    print(f"⚠️ {part_name} 體力不足！(剩餘: {current_energy}, 需要: {cost})")
                    continue

                # AI 講解
                explain_action_with_openai(target_action, part_name)
                
                # 知識考核
                print(f"🧠 進入【{target_action}】知識考核...")
                while True:
                    question, correct_ans = generate_quiz_with_openai(target_action)
                    print(f"題目: {question}")
                    user_ans_str = input("請回答 (T/F): ").strip().upper()
                    user_bool = (user_ans_str == 'T')
                    
                    if user_bool == correct_ans:
                        print("✅ 答對了！")
                        break
                    else:
                        print(f"❌ 答錯了... 再試一次！\n")
                        time.sleep(0.5)

                # 扣體力 & 記錄
                reps = 10 
                new_energy = current_energy - cost
                setattr(player, attr_name, new_energy)
                
                trained_log.append(part_name)
                
                print(f"💪 完成訓練！ {target_action} x {reps} 下")
                print(f"   {part_name}體力: {current_energy} -> {new_energy}")
                print("-" * 20)
                
            else:
                print(f"❌ 無效的編號")
                
        except Exception as e:
            print(f"錯誤: {e}")

    return trained_log
