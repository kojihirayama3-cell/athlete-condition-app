import streamlit as st
import pandas as pd
from datetime import date, datetime
import os

st.set_page_config(page_title="アスリート・コンディション記録", page_icon="🏃", layout="centered")

# --- 23人限定：認証エリア ---
# 合言葉（パスワード）
CORRECT_PASSWORD = "saitama2026"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 アスリート・コンディション記録")
    st.info("本システムは共同研究参加者（23名）専用です。")
    password = st.text_input("アクセスパスコードを入力してください", type="password")
    if st.button("ログイン"):
        if password == CORRECT_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("パスコードが正しくありません。")
    st.stop()
# ---------------------------

# メイン入力画面
st.title("🏃 アスリート・コンディション")
st.caption("埼玉医科大学 × ニールメッド 共同研究プロジェクト")

query_params = st.query_params
default_id = query_params.get("id", "")

ATHLETE_LIST = [f"選手_{i:02d}" for i in range(1, 24)]
default_index = ATHLETE_LIST.index(default_id) if default_id in ATHLETE_LIST else 0

athlete_id = st.selectbox("選手IDを選択してください", ATHLETE_LIST, index=default_index)
today = date.today()

with st.form("condition_form", clear_on_submit=False):
    st.subheader("Q1. 今朝の「足取り・脚の軽さ」")
    st.caption("1 (鉛のように重い) 〜 5 (普通) 〜 10 (羽のように軽い)")
    legs_score = st.slider("足取りスコア (1-10)", min_value=1, max_value=10, value=5)

    st.subheader("Q2. 昨夜の睡眠の質・回復感")
    sleep_score = st.radio(
        "睡眠スコア",
        [1, 2, 3, 4, 5],
        captions=["非常に悪い", "やや悪い", "普通", "良い", "非常に良い（疲労回復）"],
        horizontal=True,
        index=2
    )

    st.subheader("Q3. 鼻・喉の自覚症状")
    symptom_none = st.checkbox("特に異常なし（クリア）", value=True)
    symptom_block = st.checkbox("鼻づまりがある")
    symptom_runny = st.checkbox("鼻水・ムズムズ・くしゃみ")
    symptom_throat = st.checkbox("喉の違和感・痛み")

    st.subheader("Q4. 過去24時間以内の服薬状況")
    med_status = st.radio(
        "服薬有無",
        ["服用なし", "抗アレルギー薬（内服）", "点鼻スプレー（ステロイド等）", "風邪薬・解熱鎮痛剤", "その他"],
        index=0
    )
    med_detail = ""
    if med_status == "その他":
        med_detail = st.text_input("薬品名または用途をご記入ください")

    st.subheader("Q5. サイナス・リンスの実施")
    rinse_status = st.selectbox(
        "昨夜〜今朝の実施状況",
        ["朝・晩の2回実施", "1回実施（朝または練習後）", "1回実施（就寝前）", "実施しなかった"]
    )

    notes = st.text_input("特記事項（任意）")

    submitted = st.form_submit_button("コンディションを送信する")

    if submitted:
        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date": str(today),
            "athlete_id": athlete_id,
            "legs_score": legs_score,
            "sleep_score": sleep_score,
            "symptom_block": symptom_block,
            "symptom_runny": symptom_runny,
            "symptom_throat": symptom_throat,
            "med_status": med_status if med_status != "その他" else f"その他: {med_detail}",
            "rinse_status": rinse_status,
            "notes": notes
        }
        
        df_new = pd.DataFrame([record])
        file_path = "athlete_records.csv"
        if not os.path.exists(file_path):
            df_new.to_csv(file_path, index=False, encoding="utf-8-sig")
        else:
            df_new.to_csv(file_path, mode="a", header=False, index=False, encoding="utf-8-sig")
            
        st.success("✅ 送信が完了しました！今日も万全の呼吸で練習に臨みましょう！")
        st.balloons()
