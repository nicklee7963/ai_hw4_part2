import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
import random
import os
import glob
import math

# 設定 Matplotlib 繪圖風格與中文字型
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Taipei Sans TC', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# ==========================================
# 1. 基礎設定與讀取資料
# ==========================================
print("🚀 初始化系統中...")

if not os.path.exists("exercise_movement.csv"):
    print("❌ 錯誤：找不到 exercise_movement.csv")
    exit()

# 讀取動作資料庫
mv_df = pd.read_csv("exercise_movement.csv")
# 依照部位分類
parts_dfs = {
    "胸部": mv_df[mv_df["訓練部位"] == "胸部"],
    "背部": mv_df[mv_df["訓練部位"] == "背部"],
    "肩部": mv_df[mv_df["訓練部位"] == "肩部"],
    "手臂": mv_df[mv_df["訓練部位"] == "手臂"],
    "腿部": mv_df[mv_df["訓練部位"] == "腿部"],
    "核心": mv_df[mv_df["訓練部位"] == "核心"]
}

# 讀取所有模型
model_files = glob.glob("models/*.pkl")
MODELS = {}
if not model_files:
    print("❌ 錯誤：models 資料夾為空，請先執行 train_multi_models.py")
    exit()

print(f"📂 載入 {len(model_files)} 個模型...")
for f in model_files:
    model_name = os.path.basename(f).replace(".pkl", "")
    try:
        MODELS[model_name] = joblib.load(f)
        print(f"   ✅ 載入 {model_name}")
    except Exception as e:
        print(f"   ⚠️ 無法載入 {model_name}: {e}")

# ==========================================
# 2. 核心功能函式
# ==========================================
def generate_random_player(idx):
    return {
        'id': idx,
        '性別': random.choice([0, 1]),
        '年紀': random.randint(18, 65),
        '體重': round(random.uniform(50.0, 100.0), 1),
        '難度': random.randint(1, 5),
        'chest_max': random.randint(200, 500),
        'shoulder_max': random.randint(200, 500),
        'back_max': random.randint(200, 500),
        'hand_max': random.randint(200, 500),
        'belly_max': random.randint(200, 500),
        'leg_max': random.randint(200, 500),
        '胸體力值': 0, '肩體力值': 0, '背體力值': 0,
        '手體力值': 0, '腹體力值': 0, '腿體力值': 0
    }

def generate_greedy_menu(player):
    current_energy = {
        "胸部": player['chest_max'], "肩部": player['shoulder_max'],
        "背部": player['back_max'], "手臂": player['hand_max'],
        "核心": player['belly_max'], "腿部": player['leg_max']
    }
    menu = {}
    total_real_score = 0
    used_actions = []
    body_parts = ["胸部", "背部", "肩部", "手臂", "腿部", "核心"]

    for part in body_parts:
        part_df = parts_dfs[part]
        coda = current_energy[part]
        part_menu = []
        perfect_score = part_df.apply(lambda x: x["部位得到肌肉量"] / x["部位消耗體力值"] if x["部位消耗體力值"] > 0 else 0, axis=1).sum()
        if perfect_score == 0: perfect_score = 1
        actual_score = 0
        for _ in range(50):
            if len(part_df) == 0: break
            exercise = part_df.sample(1).iloc[0]
            if (exercise["動作名稱"] not in part_menu) and (coda >= exercise["部位消耗體力值"]) and (exercise["動作難度"] <= player['難度']):
                coda -= exercise["部位消耗體力值"]
                part_menu.append(exercise["動作名稱"])
                used_actions.append(exercise["動作名稱"])
                if exercise["部位消耗體力值"] > 0:
                    actual_score += exercise["部位得到肌肉量"] / exercise["部位消耗體力值"]
            if random.random() < 0.1: break
        total_real_score += (actual_score / perfect_score) * 20
    return menu, total_real_score, used_actions

def get_ml_choice(player, model_data, candidates):
    model = model_data['model']
    features = model_data['features']
    input_rows = []
    base_info = {k: player[k] for k in features if k in player}
    map_energy = {'胸體力值':'chest_max', '肩體力值':'shoulder_max', '背體力值':'back_max', '手體力值':'hand_max', '腹體力值':'belly_max', '腿體力值':'leg_max'}
    for k, v in map_energy.items():
        if k in features: base_info[k] = player[v]

    for cand in candidates:
        row = base_info.copy()
        for f in features:
            if f.startswith("act_"): row[f] = 0
        for action in cand['actions']:
            col_name = f"act_{action}"
            if col_name in row: row[col_name] = 1
        input_rows.append(row)
    
    X_pred = pd.DataFrame(input_rows, columns=features).fillna(0)
    predicted_scores = model.predict(X_pred)
    best_idx = np.argmax(predicted_scores)
    return candidates[best_idx]['real_score']

# ==========================================
# 3. 主實驗流程
# ==========================================
NUM_PLAYERS = 100
CANDIDATE_POOL_SIZE = 50 

print(f"\n⚡ 開始進行實驗 (玩家數: {NUM_PLAYERS}, AI 候選池: {CANDIDATE_POOL_SIZE})...")

results = { "Random": [] }
for m_name in MODELS: results[m_name] = []

for i in range(NUM_PLAYERS):
    if (i+1) % 10 == 0: print(f"   進度: {i+1}/{NUM_PLAYERS} 位玩家...")
    p = generate_random_player(i)
    _, rand_score, _ = generate_greedy_menu(p)
    results["Random"].append(rand_score)
    candidates = []
    for _ in range(CANDIDATE_POOL_SIZE):
        _, r_score, actions = generate_greedy_menu(p)
        candidates.append({'actions': actions, 'real_score': r_score})
    for m_name, m_data in MODELS.items():
        best_choice_score = get_ml_choice(p, m_data, candidates)
        results[m_name].append(best_choice_score)

# ==========================================
# 4. 畫圖 (動態 Y 軸調整版)
# ==========================================
print("\n📊 正在繪製圖表...")

# 計算動態 Y 軸上限 (最大值無條件進位到 10 的倍數)
all_scores = [score for method_scores in results.values() for score in method_scores]
max_score_val = max(all_scores)
y_limit = math.ceil(max_score_val / 10.0) * 10
print(f"   (偵測到最高分: {max_score_val:.2f}, Y軸上限設定為: {y_limit})")

# 定義顯示順序 (依平均分排序，讓圖表好看)
stats = []
for method, scores in results.items():
    stats.append((method, np.mean(scores)))
stats.sort(key=lambda x: x[1], reverse=True)
plot_order = [x[0] for x in stats] # 依強弱排序
# 確保 Random 總是在第一個，方便比較 (可選)
if "Random" in plot_order:
    plot_order.remove("Random")
    plot_order.insert(0, "Random")

colors = ['gray', '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

# --- 圖表 1: 直方圖 (Histogram - 2x3) ---
plt.figure(figsize=(12, 10))
for idx, method in enumerate(plot_order):
    if idx >= 6: break 
    plt.subplot(3, 2, idx+1)
    scores = results[method]
    avg_score = np.mean(scores)
    plt.hist(scores, bins=15, color=colors[idx % len(colors)], alpha=0.7, edgecolor='black')
    plt.title(f"{method} (Avg: {avg_score:.1f})")
    plt.xlabel("Score")
    plt.ylabel("Count")
    plt.xlim(0, y_limit) # 動態上限

plt.tight_layout()
plt.savefig("chart_1_histogram.png")
print("✅ 圖表 1 已儲存: chart_1_histogram.png (直方圖)")
plt.close()

# --- 圖表 2: 個別散佈圖 (Scatter Split - 2x3) ---
# 改用散佈圖，去除連線，避免誤導
plt.figure(figsize=(15, 10))
x_axis = range(1, NUM_PLAYERS + 1)

for idx, method in enumerate(plot_order):
    if idx >= 6: break
    plt.subplot(3, 2, idx+1)
    
    # 畫點 (Scatter)
    plt.scatter(x_axis, results[method], s=15, alpha=0.7, color=colors[idx % len(colors)])
    
    # 畫平均線 (讓觀眾知道平均水準在哪)
    avg_score = np.mean(results[method])
    plt.axhline(y=avg_score, color='black', linestyle='--', alpha=0.5, label=f'Avg: {avg_score:.1f}')
    
    plt.title(f"{method} - Score Distribution")
    plt.xlabel("Player ID")
    plt.ylabel("Score")
    plt.ylim(0, y_limit) # 動態上限
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("chart_2_players_split.png")
print("✅ 圖表 2 已儲存: chart_2_players_split.png (個別散佈圖)")
plt.close()

# --- 圖表 3: 整合散佈圖 (Combined Scatter) ---
plt.figure(figsize=(15, 8))

for idx, method in enumerate(plot_order):
    if method == "Random":
        # Random 用灰色小點
        plt.scatter(x_axis, results[method], s=10, color='gray', alpha=0.4, label=f"Random (Avg: {np.mean(results[method]):.1f})")
    else:
        # 其他模型用彩色點，稍微大一點
        plt.scatter(x_axis, results[method], s=25, alpha=0.8, 
                 color=colors[idx % len(colors)], label=f"{method} (Avg: {np.mean(results[method]):.1f})")

plt.title(f"Comparison of Models Across {NUM_PLAYERS} Players (Scatter)")
plt.xlabel("Player ID")
plt.ylabel("Score")
plt.ylim(0, y_limit) # 動態上限
plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0.)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("chart_3_combined.png")
print("✅ 圖表 3 已儲存: chart_3_combined.png (整合散佈圖)")
plt.close()

# --- (額外贈送) 圖表 4: 箱形圖 (Box Plot) ---
# 這是科學比較最標準的圖，可以一目了然看分佈高低
plt.figure(figsize=(10, 6))
plot_data = [results[m] for m in plot_order]
plt.boxplot(plot_data, labels=plot_order, patch_artist=True, 
            boxprops=dict(facecolor="lightblue"))
plt.title(f"Model Performance Comparison (Box Plot)")
plt.ylabel("Score")
plt.ylim(0, y_limit)
plt.grid(True, axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig("chart_4_boxplot.png")
print("✅ 圖表 4 已儲存: chart_4_boxplot.png (箱形圖 - 強烈建議放入報告)")
plt.close()

# ==========================================
# 5. 文字排名輸出
# ==========================================
print("\n" + "="*30)
print("🏆 模型效能排行榜 (平均分數)")
print("="*30)
for rank, (name, score) in enumerate(stats, 1):
    print(f"{rank}. {name:<15} : {score:.2f}")
print("="*30)
