import os
import time
import random
import pickle
import sys

# 匯入你的支線模組
from simulate import Player
from mini_typing_game import quick_reaction_game_strict
from mini_training_game import start_training_session, setup_openai

# 嘗試匯入 OpenAI client，用於生成結局
try:
    from mini_training_game import client
except ImportError:
    client = None
    print("⚠️ 警告：無法匯入 OpenAI client，結局生成功能將受限。")

# --- 設定與常數 ---
SAVE_DIR = "saves"  # 存檔資料夾
MAX_SAVES = 4       # 最大存檔數

# 遊戲難度設定
DIFFICULTY_SETTINGS = {
    1: {"name": "簡單", "time": 1.0},
    2: {"name": "普通", "time": 0.75},
    3: {"name": "難",   "time": 0.50},
    4: {"name": "困難", "time": 0.25},
    5: {"name": "屌炸天", "time": 0.10}
}

# 定義五大魔王
DEMON_KINGS_DATA = [
    {"id": 0, "name": "史萊姆王·波波", "title": "【貪婪的】", "deed": "偷走了村莊所有的蛋白粉，讓村民肌肉萎縮。", "hp": 1, "word_len": 3, "difficulty": 1},
    {"id": 1, "name": "哥布林健身教練", "title": "【暴虐的】", "deed": "強迫路人做姿勢錯誤的深蹲，導致大家膝蓋受傷。", "hp": 2, "word_len": 4, "difficulty": 2},
    {"id": 2, "name": "半獸人·加爾魯什", "title": "【破壞者】", "deed": "因為練背練不好，憤怒地摧毀了這座城市的圖書館。", "hp": 3, "word_len": 5, "difficulty": 3},
    {"id": 3, "name": "吸血鬼伯爵·德古拉", "title": "【永夜的】", "deed": "吸食人們的意志力，讓人們再也不想去健身房。", "hp": 4, "word_len": 6, "difficulty": 4},
    {"id": 4, "name": "深淵魔龍·巴哈姆特", "title": "【終焉的】", "deed": "它的存在就是為了讓世界陷入肥胖與懶惰的深淵。", "hp": 5, "word_len": 8, "difficulty": 5}
]

class GameState:
    def __init__(self, player, slot_id, difficulty_lv=2):
        self.player = player
        self.slot_id = slot_id 
        self.difficulty_lv = difficulty_lv 
        self.bosses = DEMON_KINGS_DATA.copy()
        self.defeated_bosses = []

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def slow_print(text, speed=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()

# --- 存檔系統 (Save/Load) ---

def ensure_save_dir():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

def get_save_filename(slot_id):
    return os.path.join(SAVE_DIR, f"save_{slot_id}.pkl")

def get_slot_info(slot_id):
    filename = get_save_filename(slot_id)
    if os.path.exists(filename):
        try:
            with open(filename, 'rb') as f:
                state = pickle.load(f)
                p_name = state.player.name
                kill_count = len(state.defeated_bosses)
                diff_lv = getattr(state, 'difficulty_lv', 2) 
                diff_name = DIFFICULTY_SETTINGS.get(diff_lv, {}).get("name", "未知")
                return f"{p_name} (討伐: {kill_count}/5) [{diff_name}]"
        except:
            return "檔案損毀"
    return "---- 空白存檔 ----"

def list_save_slots():
    print("\n💾 --- 存檔管理 ---")
    for i in range(1, MAX_SAVES + 1):
        info = get_slot_info(i)
        print(f"[{i}] {info}")
    print("-" * 20)

def save_game(game_state):
    ensure_save_dir()
    filename = get_save_filename(game_state.slot_id)
    with open(filename, 'wb') as f:
        pickle.dump(game_state, f)
    print(f"\n✅ 進度已儲存至欄位 {game_state.slot_id}！")
    time.sleep(1)

def load_game_menu():
    ensure_save_dir()
    list_save_slots()
    while True:
        choice = input("請選擇讀取的欄位 (輸入 0 返回): ").strip()
        if choice == '0': return None
        
        if choice.isdigit() and 1 <= int(choice) <= MAX_SAVES:
            filename = get_save_filename(choice)
            if os.path.exists(filename):
                with open(filename, 'rb') as f:
                    return pickle.load(f)
            else:
                print("❌ 該欄位沒有存檔！")
        else:
            print("無效的輸入。")

# --- NLP 生成功能 ---

def generate_ending_story(game_state):
    from mini_training_game import client
    
    if not client:
        print("\n(系統提示：因無法連線 OpenAI，跳過 AI 結局生成)")
        return

    p = game_state.player
    boss_names = [b['name'] for b in game_state.bosses if b['id'] in game_state.defeated_bosses]
    diff_name = DIFFICULTY_SETTINGS[game_state.difficulty_lv]["name"]

    print("\n✨ 正在撰寫你的傳奇史詩 (AI 生成中)...✨")
    
    prompt = (
        f"請寫一段壯闊的奇幻小說結局，描述勇者 {p.name} 在「{diff_name}」的殘酷難度下，"
        f"擊敗了所有魔王，拯救了異世界。\n"
        f"勇者屬性：體重 {p.weight}kg，擅長部位包含胸、背、腿。\n"
        f"總訓練累積次數：胸{p.training_chest}次, 腿{p.training_leg}次, 背{p.training_back}次。\n"
        f"擊敗的魔王名單：{', '.join(boss_names)}。\n"
        f"請描述他如何運用強壯的肉體和堅強的意志帶來和平，並提到他最後回到原本的世界或是留在異世界成為傳說。"
        f"字數約 200-300 字。"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
        )
        story = response.choices[0].message.content.strip()
        
        clear_screen()
        print("="*40)
        print(f"📖 勇者 {p.name} 的傳說 📖")
        print("="*40)
        slow_print(story, speed=0.05)
        print("\n" + "="*40)
        input("按 Enter 結束旅程...")
        
    except Exception as e:
        print(f"AI 生成失敗: {e}")
        input("按 Enter 結束...")

# [新功能] 故事總攬 (生成 .txt)
def do_story_review(game_state):
    from mini_training_game import client
    
    if not client:
        print("\n⚠️ 請先設定 API Key 才能生成故事日誌！")
        time.sleep(1.5)
        return

    p = game_state.player
    alive_count = 5 - len(game_state.defeated_bosses)
    defeated_list = [b['name'] for b in game_state.bosses if b['id'] in game_state.defeated_bosses]
    boss_text = ", ".join(defeated_list) if defeated_list else "尚未擊敗任何魔王"
    diff_name = DIFFICULTY_SETTINGS[game_state.difficulty_lv]["name"]

    print("\n📜 正在整理冒險日誌 (AI 撰寫中)...")

    prompt = (
        f"請為異世界勇者 {p.name} 撰寫一份「冒險日誌總結」。\n"
        f"目前狀態：\n"
        f"- 挑戰難度：{diff_name}\n"
        f"- 身體素質：{p.weight}kg, 訓練累積(胸{p.training_chest}, 腿{p.training_leg}, 背{p.training_back})\n"
        f"- 戰績：已擊敗 {boss_text}，剩餘 {alive_count} 隻魔王。\n"
        f"請用「吟遊詩人」的語氣，總結他目前的旅程進度與訓練成果，並給予他繼續前進的鼓勵。\n"
        f"字數約 150 字。"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        story_text = response.choices[0].message.content.strip()
        
        # 顯示在螢幕
        print("-" * 40)
        print(f"【{p.name} 的冒險日誌】")
        slow_print(story_text, speed=0.02)
        print("-" * 40)

        # 寫入檔案
        filename = f"story_review_{p.name}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"=== {p.name} 的冒險日誌 ===\n")
            f.write(f"時間：{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"難度：{diff_name}\n")
            f.write("-" * 30 + "\n")
            f.write(story_text)
            f.write("\n" + "-" * 30 + "\n")
        
        print(f"\n✅ 日誌已生成並存檔為: {filename}")
        input("按 Enter 返回...")

    except Exception as e:
        print(f"AI 生成失敗: {e}")
        input("按 Enter 返回...")

# --- 遊戲內容 ---

def intro_story(player):
    clear_screen()
    print("="*40)
    slow_print("⚡ 一道閃電劈下，你感覺意識逐漸模糊... ⚡")
    time.sleep(1)
    print("="*40)
    slow_print(f"當你再次睜開眼，發現自己身處在一個陌生的異世界。")
    slow_print(f"你的名字是 {player.name}，看起來是一位剛轉生的勇者。")
    print("\n【系統分析你的身體素質】")
    player.get_status()
    print("\n")
    slow_print("這是一個被「懶惰魔王」支配的世界。")
    slow_print("女神告訴你：『勇者啊！你的任務就是鍛鍊肉體，並擊敗這五位魔王！』")
    print("-" * 30)
    input("按 Enter 接受使命...")

def do_rest(game_state):
    p = game_state.player
    print("\n💤 你找了一間旅館休息...")
    time.sleep(1)
    p.energy_chest = p.chest_max
    p.energy_shoulder = p.shoulder_max
    p.energy_hand = p.hand_max
    p.energy_back = p.back_max
    p.energy_belly = p.belly_max
    p.energy_leg = p.leg_max
    print("✨ 體力已完全恢復！狀態絕佳！")
    save_game(game_state)
    input("按 Enter 返回...")

def do_fight(game_state):
    alive_bosses = [b for b in game_state.bosses if b['id'] not in game_state.defeated_bosses]
    if not alive_bosses:
        print("\n🎉 所有的魔王都已被你擊敗！")
        return

    boss = random.choice(alive_bosses)
    lv = game_state.difficulty_lv
    diff_setting = DIFFICULTY_SETTINGS[lv]
    time_per_char = diff_setting["time"]
    diff_name = diff_setting["name"]

    clear_screen()
    print(f"\n⚔️  遭遇強敵！ {boss['title']} {boss['name']}")
    print(f"惡行：{boss['deed']}")
    print(f"----------------------------------------")
    print(f"【關卡難度: {diff_name}】 (每字 {time_per_char} 秒)")
    print(f"通關條件：反應遊戲成功 {boss['hp']} 次")
    print(f"----------------------------------------")
    
    choice = input("按 Enter 戰鬥，輸入 'exit' 逃跑: ").strip().lower()
    if choice == 'exit':
        print("你選擇了戰略性撤退...")
        time.sleep(1)
        return

    current_hp = boss['hp']
    round_count = 1
    
    while current_hp > 0:
        print(f"\n🔥 Round {round_count} (魔王血量: {current_hp})")
        result = quick_reaction_game_strict(boss['word_len'], seconds_per_char=time_per_char)
        
        if result == 'escape':
            print("\n💨 你在戰鬥中途轉身逃跑了！")
            time.sleep(1)
            return 

        elif result is True:
            current_hp -= 1
            print(f"⚔️  你對 {boss['name']} 造成了重創！")
        else:
            print(f"🛡️  {boss['name']} 擋下了你的攻擊！")
        
        round_count += 1
        time.sleep(0.5)
    
    print(f"\n🏆 恭喜！你擊敗了 {boss['name']}！")
    game_state.defeated_bosses.append(boss['id'])
    save_game(game_state)
    
    if len(game_state.defeated_bosses) == 5:
        input("🎉 全破！按 Enter 進入結局...")
        generate_ending_story(game_state)
        sys.exit() 
    else:
        input("按 Enter 返回營地...")

def do_gym(game_state):
    print("\n🏋️  進入異世界道館...")
    trained_list = start_training_session(game_state.player)
    if trained_list:
        print("\n📈 結算訓練成果：")
        p = game_state.player
        for part in trained_list:
            if part == "胸部": p.training_chest += 1
            elif part == "背部": p.training_back += 1
            elif part == "腿部": p.training_leg += 1
            elif part == "手臂": p.training_hand += 1
            elif part == "肩部": p.training_shoulder += 1
            elif part == "核心": p.training_belly += 1
            print(f"  - {part} 熟練度 +1")
        save_game(game_state)
    else:
        print("沒有進行任何訓練。")

def do_archive(game_state):
    print("\n📜 --- 魔王討伐名冊 --- 📜")
    if not game_state.defeated_bosses:
        print("目前一片空白...去戰鬥吧，勇者！")
    else:
        for boss in game_state.bosses:
            if boss['id'] in game_state.defeated_bosses:
                print(f"✅ {boss['title']} {boss['name']}")
                print(f"   描述：{boss['deed']}")
                print("-" * 20)
    input("\n按 Enter 返回...")

def do_status(game_state):
    p = game_state.player
    alive_count = 5 - len(game_state.defeated_bosses)
    diff_name = DIFFICULTY_SETTINGS[game_state.difficulty_lv]["name"]
    
    print(f"\n📊 --- {p.name} 的狀態 --- 📊")
    print(f"難度: {diff_name} | 存檔: {game_state.slot_id}")
    print(f"討伐進度：{len(game_state.defeated_bosses)} / 5")
    print(f"身體數值：{p.weight}kg / {p.height}cm / {p.age}歲")
    
    print("\n[累積訓練次數]")
    print(f"  胸:{p.training_chest:<3} 背:{p.training_back:<3} 腿:{p.training_leg:<3}")
    print(f"  手:{p.training_hand:<3} 肩:{p.training_shoulder:<3} 腹:{p.training_belly:<3}")
    
    print("\n[當前體力 / 最大值]")
    print(f"  胸: {p.energy_chest}/{p.chest_max}")
    print(f"  背: {p.energy_back}/{p.back_max}")
    print(f"  腿: {p.energy_leg}/{p.leg_max}")
    print(f"  手: {p.energy_hand}/{p.hand_max}")
    print(f"  肩: {p.energy_shoulder}/{p.shoulder_max}")
    print(f"  腹: {p.energy_belly}/{p.belly_max}")
    
    input("\n按 Enter 返回...")

# --- Main ---

def main():
    ensure_save_dir()
    
    clear_screen()
    print("=== 🔑 初始化設定 ===")
    user_key = input("請輸入您的 OpenAI API Key (直接 Enter 可跳過但無法使用 AI 功能): ").strip()
    setup_openai(user_key)
    time.sleep(1)
    
    while True:
        clear_screen()
        print("=== ⚔️  異世界健身大冒險 ⚔️  ===")
        print("1. 開始新遊戲")
        print("2. 讀取進度")
        print("Q. 離開")
        choice = input("請選擇: ").upper()

        if choice == 'Q':
            break

        if choice == '2':
            game_state = load_game_menu()
            if game_state:
                print(f"歡迎回來，{game_state.player.name}！")
                time.sleep(1)
                game_loop(game_state)

        elif choice == '1':
            random.seed() # 重設亂數
            
            # 1. 選擇存檔欄位
            list_save_slots()
            slot = input(f"請選擇要覆蓋的存檔欄位 (1-{MAX_SAVES}): ")
            if not slot.isdigit() or not (1 <= int(slot) <= MAX_SAVES):
                print("無效欄位！")
                time.sleep(1)
                continue
            
            # 2. 選擇難度
            clear_screen()
            print("【請選擇遊戲難度】")
            print("決定了你討伐魔王時，每個單字允許的反應秒數。")
            print("-" * 30)
            for k, v in DIFFICULTY_SETTINGS.items():
                print(f" ({k}) {v['name']} - 每字 {v['time']} 秒")
            print("-" * 30)
            
            diff = input("請選擇 (1-5): ")
            if not (diff.isdigit() and 1 <= int(diff) <= 5):
                diff = 2 # 預設普通
                print("輸入無效，預設為【普通】。")
            else:
                diff = int(diff)

            # 3. 輸入名字
            name = input("\n請輸入勇者的大名: ")
            if not name: name = "努伊特"
            
            # 4. 產生資料
            player = Player(name)
            # 確保 training 屬性存在
            if not hasattr(player, 'training_chest'):
                player.training_chest = 0
                player.training_back = 0
                player.training_leg = 0
                player.training_hand = 0
                player.training_shoulder = 0
                player.training_belly = 0

            game_state = GameState(player, slot_id=slot, difficulty_lv=diff)
            
            intro_story(player)
            save_game(game_state)
            game_loop(game_state)

def game_loop(game_state):
    while True:
        clear_screen()
        alive_bosses = 5 - len(game_state.defeated_bosses)
        p = game_state.player
        diff_name = DIFFICULTY_SETTINGS[game_state.difficulty_lv]["name"]
        
        print(f"\n🏰 營地 ({p.name}) | 難度: {diff_name}")
        print(f"存檔欄位: {game_state.slot_id} | 剩餘魔王: {alive_bosses}")
        print("-" * 30)
        print("(0) 🛌 休息 (補血存檔)")
        print("(1) ⚔️  討伐魔王")
        print("(2) 🏋️  道館訓練")
        print("(3) 📜 魔王檔案")
        print("(4) 📊 屬性查看")
        print("(5) 📖 故事總攬 (生成日誌)")
        print("(Q) 回主選單")
        print("-" * 30)
        
        action = input("請選擇: ").upper()
        
        if action == '0': do_rest(game_state)
        elif action == '1': do_fight(game_state)
        elif action == '2': do_gym(game_state)
        elif action == '3': do_archive(game_state)
        elif action == '4': do_status(game_state)
        elif action == '5': do_story_review(game_state)
        elif action == 'Q': return 

if __name__ == "__main__":
    main()
