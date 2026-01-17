import streamlit as st
import csv

# =========================
# データロード
# =========================
@st.cache_data
def load_moves():
    moves = {}
    with open("moves_ja.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            moves[row["ja_name"]] = {
                "en_name": row["en_name"],
                "target_type": row["target_type"],  # single / all / self / none / auto
            }
    return moves

moves = load_moves()
move_names = list(moves.keys())

# =========================
# 共通ユーティリティ
# =========================
def exclusive_toggle(group_key, labels, selected_label):
    """
    排他トグルの状態を session_state に反映
    """
    for l in labels:
        st.session_state[f"{group_key}_{l}"] = (l == selected_label)

def get_selected(group_key, labels, default=None):
    for l in labels:
        if st.session_state.get(f"{group_key}_{l}"):
            return l
    return default

# =========================
# UI: 技選択
# =========================
st.title("たみぷる　わざ入力補助ツール")

selected_move = st.selectbox(
    "わざ名検索",
    options=move_names,
    index=None,
    placeholder="技名を入力（部分一致）",
)

if not selected_move:
    st.stop()

target_type = moves[selected_move]["target_type"]

st.caption(f"対象タイプ: {target_type}")

# =========================
# UI: 使用者選択（2×3 排他）
# =========================
st.subheader("わざ使用者")

user_labels = ["1", "2", "3"]

with st.container(border=True):
    for row in range(1):
        cols = st.columns(3)
        for col, label in zip(cols, user_labels[row*3:(row+1)*3]):
            with col:
                st.toggle(
                    label,
                    key=f"user_{label}",
                    on_change=exclusive_toggle,
                    args=("user", user_labels, label),
                )

selected_user = get_selected("user", user_labels, "未選択")

# =========================
# UI: 対象選択（条件付き）
# =========================
st.subheader("わざ対象")

target_labels = ["ア", "イ", "ウ", "1", "2", "3"]

selected_target = ""

if target_type in ("single",):
    with st.container(border=True):
        for row in range(2):
            cols = st.columns(3)
            for col, label in zip(cols, target_labels[row*3:(row+1)*3]):
                with col:
                    st.toggle(
                        label,
                        key=f"target_{label}",
                        on_change=exclusive_toggle,
                        args=("target", target_labels, label),
                    )

    selected_target = get_selected("target", target_labels, "")
else:
    st.info("この技は対象選択が不要です")

# =========================
# 出力生成
# =========================
if target_type in ("all", "self", "none", "auto"):
    output = f"{selected_user}{selected_move} "
else:
    output = f"{selected_user}{selected_move}{selected_target}"

st.subheader("出力")
st.text_input("結果", output)
