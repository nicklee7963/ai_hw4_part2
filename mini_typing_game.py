from inputimeout import inputimeout, TimeoutOccurred
import random

def quick_reaction_game_strict(num, seconds_per_char=0.5):
    """
    num: 單字數量 (決定題目長度)
    seconds_per_char: 每個字元給予的秒數 (由遊戲難度決定)
    """
    word_list = [
        # A-C
        "abs", "active", "agility", "ankle", "arm", "athlete", "back", "balance", "barbell", "belly",
        "bench", "biceps", "bike", "body", "bone", "box", "breath", "build", "burn", "burpee",
        "calves", "cardio", "chest", "chinup", "coach", "core", "crossfit", "crunch", "curl", "cycle",
        # D-F
        "deadlift", "delts", "diet", "dip", "dumbbell", "eat", "effort", "elbow", "energy", "exercise",
        "fast", "fat", "fit", "fitness", "flex", "focus", "food", "form", "gain", "gear",
        # G-I
        "glutes", "goal", "gym", "habit", "hamstrings", "hand", "health", "heart", "heavy", "hiit",
        "hike", "hips", "hit", "hold", "hydrate", "inch", "intensity", "iron", "jog", "joint",
        # J-M
        "jump", "kick", "knee", "leg", "lift", "lose", "lunge", "mass", "mat", "meal",
        "meat", "move", "muscle", "neck", "nutrition", "pace", "pain", "plank", "plate", "power",
        # P-R
        "press", "protein", "pull", "pullup", "pulse", "pump", "push", "pushup", "quads", "race",
        "rack", "rank", "recovery", "reps", "rest", "ribs", "ride", "rope", "row", "run",
        # S-T
        "salad", "sets", "shape", "shoulder", "size", "skin", "sleep", "slim", "slow", "speed",
        "sport", "sprint", "squat", "stamina", "step", "strength", "stretch", "strong", "sweat", "swim",
        # T-Y
        "target", "team", "thigh", "time", "tone", "torso", "train", "triceps", "walk", "warmup",
        "water", "weight", "wellness", "win", "work", "workout", "wrist", "yoga", "young", "zone"
    ]
    
    target_list = []
    # 隨機選字
    for i in range(num):
        target_word = random.choice(word_list)
        target_list.append(target_word)

    target = " ".join(target_list)
    
    # 計算時間限制
    time_limit = round(len(target) * seconds_per_char, 2)
    
    print("\n" + "="*30)
    print("⚡ 極限反應特訓 ⚡")
    print(f"題目長度: {len(target)} 字元")
    print(f"極限時間: {time_limit} 秒 (難度係數: {seconds_per_char}s/字)")
    print(f"請輸入：【 {target} 】")
    print("="*30)

    # 這裡可以輸入 q 逃跑
    user_wait = input(">> 按 Enter 開始 (或輸入 q / esc 逃跑)... ").strip().lower()
    if user_wait in ['q', 'esc', 'exit']:
        return 'escape'

    print("GO!")

    try:
        # 使用 inputimeout 進行計時
        user_input = inputimeout(prompt='輸入: ', timeout=time_limit)

        # 去除空白後比較
        if user_input.replace(" ", "") == target.replace(" ", ""):
            print(f"\n✅ 成功！速度驚人！")
            return True
        else:
            print(f"\n❌ 失敗！打錯字了！")
            return False

    except TimeoutOccurred:
        print(f"\n\n⏰ 嗶嗶！時間到！你輸了！")
        return False

if __name__ == "__main__":
    # 測試：屌炸天難度 (0.1秒/字)
    quick_reaction_game_strict(3, 0.1)
