import streamlit as st
import pandas as pd

st.set_page_config(page_title="百家樂智能記錄與下注建議", layout="centered")

# 初始化 session state
if "history" not in st.session_state:
    st.session_state.history = []  # 本局結果 Player/Banker/Tie
if "bets" not in st.session_state:
    st.session_state.bets = []     # 下注金額
if "earnings" not in st.session_state:
    st.session_state.earnings = [] # 盈虧
if "cards" not in st.session_state:
    st.session_state.cards = []    # 開牌牌型描述

def record_result(result, bet, earning, card_info):
    st.session_state.history.append(result)
    st.session_state.bets.append(bet)
    st.session_state.earnings.append(earning)
    st.session_state.cards.append(card_info)

def reset_all():
    st.session_state.history = []
    st.session_state.bets = []
    st.session_state.earnings = []
    st.session_state.cards = []

def calc_streak():
    if not st.session_state.history:
        return 0, None
    streak = 1
    last = st.session_state.history[-1]
    for r in reversed(st.session_state.history[:-1]):
        if r == last and r != "Tie":
            streak += 1
        else:
            break
    return streak, last

st.title("🟟 百家樂智能記錄與下注建議")

# 計算統計
total = len(st.session_state.history)
player_count = st.session_state.history.count("Player")
banker_count = st.session_state.history.count("Banker")
tie_count = st.session_state.history.count("Tie")

st.markdown("### 🟟 統計結果")
st.write(f"總局數：{total}")
st.write(f"Player 勝：{player_count}")
st.write(f"Banker 勝：{banker_count}")
st.write(f"Tie 和：{tie_count}")

# 計算勝率避免除0
games_for_rate = total if total > 0 else 1
player_rate = player_count / games_for_rate
banker_rate = banker_count / games_for_rate

streak, streak_side = calc_streak()

st.markdown("### 🟟 智能下注建議")

if player_rate > banker_rate:
    recommended_side = "Player"
    confidence = player_rate - banker_rate
else:
    recommended_side = "Banker"
    confidence = banker_rate - player_rate

base_bet = 10
max_bet = 100
bet_amount = base_bet + int(confidence * (max_bet - base_bet))

if streak_side == recommended_side:
    bet_amount = int(bet_amount * 1.5)
elif streak_side is not None and streak_side != recommended_side:
    bet_amount = int(bet_amount * 0.7)

if bet_amount < 10:
    bet_amount = 10

st.write(f"建議下注方：**{recommended_side}**")
st.write(f"建議下注金額：**{bet_amount} 元**")
if streak_side is not None:
    streak_type = "勝利" if streak_side == recommended_side else "失敗"
    st.write(f"目前連續{streak}局{streak_type}")

# 輸入本局完整結果
st.markdown("### 🟟 輸入本局完整結果")

with st.form("full_result_form"):
    result = st.selectbox("本局結果", ["Player", "Banker", "Tie"])
    card_info = st.text_input("開牌牌型/點數（可輸入描述）", "")
    bet_side = st.selectbox("下注方", ["Player", "Banker"])
    bet = st.number_input("下注金額", min_value=1, value=bet_amount)
    win_lose = st.selectbox("下注結果", ["贏", "輸", "和局"])
    submitted = st.form_submit_button("記錄本局")

    if submitted:
        earning = 0
        if win_lose == "贏":
            if bet_side == "Banker":
                earning = bet * 0.95
            else:
                earning = bet * 2
        elif win_lose == "輸":
            earning = -bet
        else:
            earning = 0

        record_result(result, bet, earning, card_info)
        st.success(f"本局記錄完成，盈虧：{earning:.2f} 元")

# 顯示下注歷史與盈虧
st.markdown("### 🟟 下注歷史與盈虧")

if total > 0:
    data = []
    for i in range(total):
        data.append({
            "局數": i + 1,
            "結果": st.session_state.history[i],
            "牌型": st.session_state.cards[i],
            "下注金額": st.session_state.bets[i],
            "盈虧": st.session_state.earnings[i]
        })
    df = pd.DataFrame(data)
    st.dataframe(df)

    total_earning = sum(st.session_state.earnings)
    st.markdown(f"**總盈虧：{total_earning:.2f} 元**")
else:
    st.write("尚無記錄")

if st.button("🟟 重置所有記錄"):
    reset_all()
    st.success("所有資料已清除")