import streamlit as st
import pandas as pd
import plotly.express as px

# 初始化 Session State
if "history" not in st.session_state:
    st.session_state.history = []
if "game_count" not in st.session_state:
    st.session_state.game_count = 0

st.title("🎴 百家樂記錄與下注建議系統")

suits = ["♠️", "♥️", "♦️", "♣️"]

def card_input(player):
    cols = st.columns(3)
    cards = []
    for i in range(3):
        with cols[i]:
            suit = st.selectbox(f"{player} 牌 {i+1} 花色", suits, key=f"{player}_suit_{i}")
            point = st.number_input(f"{player} 牌 {i+1} 點數", min_value=0, max_value=9, value=0, step=1, key=f"{player}_point_{i}")
            cards.append((suit, point))
    return cards

def format_cards(cards):
    return " ".join([f"{suit}{point}" for suit, point in cards])

def calc_total(cards):
    return sum([card[1] for card in cards]) % 10

def determine_result(player_total, banker_total):
    if player_total > banker_total:
        return "Player"
    elif banker_total > player_total:
        return "Banker"
    else:
        return "Tie"

def determine_winlose(bet_side, actual_result):
    if actual_result == "Tie":
        return "Tie"
    elif bet_side == actual_result:
        return "Win"
    else:
        return "Lose"

### 新增函數：依照前五把數據建議下注 ###
def suggest_bet(history, n=5):
    if len(history) < n:
        return "資料不足，無法建議下注。"

    last_n = history[-n:]
    # 計算 Player 和 Banker 實際勝場（排除 Tie）
    player_wins = sum(1 for r in last_n if r["實際結果"] == "Player")
    banker_wins = sum(1 for r in last_n if r["實際結果"] == "Banker")
    total_games = sum(1 for r in last_n if r["實際結果"] in ["Player", "Banker"])

    if total_games == 0:
        return "最近5局沒有有效勝負，無法建議下注。"

    player_rate = player_wins / total_games
    banker_rate = banker_wins / total_games

    threshold = 0.6  # 勝率門檻60%

    if player_rate >= threshold and player_rate > banker_rate:
        return f"建議下注『Player』（最近{n}局 Player 勝率 {player_rate*100:.1f}%）"
    elif banker_rate >= threshold and banker_rate > player_rate:
        return f"建議下注『Banker』（最近{n}局 Banker 勝率 {banker_rate*100:.1f}%）"
    else:
        return f"建議觀望，無明顯優勢（Player 勝率 {player_rate*100:.1f}%，Banker 勝率 {banker_rate*100:.1f}%）"

# 開牌輸入
st.subheader("🂠 開牌紀錄")
player_cards = card_input("閒家")
banker_cards = card_input("莊家")

player_total = calc_total(player_cards)
banker_total = calc_total(banker_cards)

auto_result = determine_result(player_total, banker_total)

st.write(f"閒家牌組：{format_cards(player_cards)}，點數：{player_total}")
st.write(f"莊家牌組：{format_cards(banker_cards)}，點數：{banker_total}")
st.write(f"🔍 自動判斷勝負：**{auto_result}**")

# 下注與實際結果輸入
st.subheader("🎯 下注資訊")
bet_side = st.selectbox("你下注的是", ["Player", "Banker"])
bet_amount = st.number_input("下注金額", min_value=0, value=100, step=100)
actual_result = st.selectbox("實際勝方", ["Player", "Banker", "Tie"])

winlose = determine_winlose(bet_side, actual_result)

st.write(f"本局結果判定為：**{winlose}**")

# 儲存資料
if st.button("✅ 紀錄本局"):
    outcome = 0
    if winlose == "Win":
        if bet_side == "Player":
            outcome = bet_amount
        elif bet_side == "Banker":
            outcome = bet_amount * 0.95
    elif winlose == "Lose":
        outcome = -bet_amount

    record = {
        "閒家牌": format_cards(player_cards),
        "莊家牌": format_cards(banker_cards),
        "閒家點數": player_total,
        "莊家點數": banker_total,
        "判定結果": auto_result,
        "實際結果": actual_result,
        "下注": bet_side,
        "下注金額": bet_amount,
        "勝負": winlose,
        "盈虧": round(outcome, 2)
    }
    st.session_state.history.append(record)
    st.session_state.game_count += 1
    st.success("已儲存本局！")

# 顯示歷史紀錄及統計
if st.session_state.history:
    st.subheader("📋 歷史紀錄")
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df)

    total_profit = sum([r["盈虧"] for r in st.session_state.history])
    st.write(f"💰 總盈虧：{round(total_profit, 2)}")

    # 最近 10 局下注統計
    if st.session_state.game_count % 10 == 0:
        last10 = st.session_state.history[-10:]
        bets = [r for r in last10 if r["勝負"] in ["Win", "Lose"]]
        wins = [r for r in bets if r["勝負"] == "Win"]
        win_rate = len(wins) / len(bets) * 100 if bets else 0
        st.subheader("📊 最近 10 局下注統計")
        st.write(f"勝率：{win_rate:.1f}%")
        st.write(f"盈虧：{sum(r['盈虧'] for r in last10)}")

    # 盈虧走勢圖
    df["局數"] = range(1, len(df)+1)
    fig = px.line(df, x="局數", y="盈虧", title="盈虧走勢")
    st.plotly_chart(fig)

    ### 新增區塊：下注建議按鈕 ###
    st.subheader("💡 下注建議")
    if st.button("根據最近5局數據建議下注"):
        suggestion = suggest_bet(st.session_state.history, n=5)
        st.info(suggestion)

# 重置
if st.button("🔁 重置所有紀錄"):
    st.session_state.history = []
    st.session_state.game_count = 0
    st.success("已重置所有資料。")

