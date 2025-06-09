
import streamlit as st
import pandas as pd

# 初始化 Session State
if "history" not in st.session_state:
    st.session_state.history = []
if "game_count" not in st.session_state:
    st.session_state.game_count = 0

st.title("🎴 百家樂記錄與下注建議系統")

# 花色與點數選項
suits = ["♠️", "♥️", "♦️", "♣️"]
points = list(range(10))

def card_input(player):
    cols = st.columns(3)
    cards = []
    for i in range(3):
        with cols[i]:
            suit = st.selectbox(f"{player} 牌 {i+1} 花色", suits, key=f"{player}_suit_{i}")
            point = st.selectbox(f"{player} 牌 {i+1} 點數", points, key=f"{player}_point_{i}")
            cards.append((suit, point))
    return cards

# 開牌輸入
st.subheader("🂠 開牌紀錄")
player_cards = card_input("閒家")
banker_cards = card_input("莊家")

# 計算點數
def calc_total(cards):
    return sum([card[1] for card in cards]) % 10

player_total = calc_total(player_cards)
banker_total = calc_total(banker_cards)

# 自動判斷勝負
auto_result = "Tie"
if player_total > banker_total:
    auto_result = "Player"
elif banker_total > player_total:
    auto_result = "Banker"

# 顯示點數與自動判定
st.write(f"閒家點數：{player_total}")
st.write(f"莊家點數：{banker_total}")
st.write(f"🔍 自動判斷勝負：**{auto_result}**")

# 下注與實際結果輸入
st.subheader("🎯 下注資訊")
bet_side = st.selectbox("你下注的是", ["Player", "Banker"])
bet_amount = st.number_input("下注金額", min_value=0, value=100)
actual_result = st.selectbox("實際勝方", ["Player", "Banker", "Tie"])
winlose = st.selectbox("這局結果", ["Win", "Lose", "Tie"])

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
        "閒家牌": player_cards,
        "莊家牌": banker_cards,
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

# 顯示歷史紀錄
if st.session_state.history:
    st.subheader("📋 歷史紀錄")
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df)

    total_profit = sum([r["盈虧"] for r in st.session_state.history])
    st.write(f"💰 總盈虧：{round(total_profit, 2)}")

    # 每 10 局統計
    if st.session_state.game_count % 10 == 0:
        last10 = st.session_state.history[-10:]
        bets = [r for r in last10 if r["勝負"] in ["Win", "Lose"]]
        wins = [r for r in bets if r["勝負"] == "Win"]
        win_rate = len(wins) / len(bets) * 100 if bets else 0
        st.subheader("📊 最近 10 局下注統計")
        st.write(f"勝率：{win_rate:.1f}%")
        st.write(f"盈虧：{sum(r['盈虧'] for r in last10)}")

# 重置
if st.button("🔁 重置所有紀錄"):
    st.session_state.history = []
    st.session_state.game_count = 0
    st.success("已重置所有資料。")
