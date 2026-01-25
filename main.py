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
# 初期化
# =========================
if "pokemon_names" not in st.session_state:
    st.session_state.pokemon_names = ["", "", ""]

# =========================
# タイトル
# =========================
st.title("民プル　投票コメント生成ツール")

output_parts = []
# =========================
# 各ポケモンの入力
# =========================

for i in range(3):
    position = str(i + 1)
    default_target = ["Ａ", "Ｂ", "Ｃ"][i]
    
    st.subheader(f"ポケモン {position} の行動")
    
    with st.container(border=True):
        # 行動タイプ選択
        action_type = st.radio(
            "行動タイプ",
            ["技", "交代", "ムーブ"],
            key=f"action_type_{i}",
            horizontal=True
        )
        
        if action_type == "技":
            col1, col2 = st.columns([3, 1])
            
            with col1:
                selected_move = st.selectbox(
                    "技名",
                    options=move_names,
                    index=None,
                    placeholder="技を選択",
                    key=f"move_{i}"
                )
            
            with col2:
                no_mega = st.checkbox(
                    "メガシンカしない",
                    key=f"no_mega_{i}"
                )
            
            if selected_move:
                target_type = moves[selected_move]["target_type"]
                
                # 対象選択（単体技の場合のみ）
                if target_type == "single":
                    st.caption("対象選択")
                    target_options = ["省略(正面)", "Ａ", "Ｂ", "Ｃ", "１", "２", "３"]
                    selected_target = st.radio(
                        "対象",
                        target_options,
                        index=0,
                        key=f"target_{i}",
                        horizontal=True,
                        label_visibility="collapsed"
                    )
                    
                    # 出力生成
                    mega_mark = "？" if no_mega else ""
                    if selected_target == "省略(正面)":
                        output_parts.append(f"{position}{mega_mark}{selected_move}")
                    else:
                        output_parts.append(f"{position}{mega_mark}{selected_move}{selected_target}")
                else:
                    st.info(f"この技は対象選択不要（{target_type}）")
                    mega_mark = "？" if no_mega else ""
                    output_parts.append(f"{position}{mega_mark}{selected_move}")
            else:
                output_parts.append("")
        
        elif action_type == "交代":
            pokemon_name = st.text_input(
                "交代先ポケモン名",
                key=f"switch_{i}",
                placeholder="例: モロバレル"
            )
            
            if pokemon_name:
                st.session_state.pokemon_names[i] = pokemon_name
                output_parts.append(f"{position}{pokemon_name}")
            else:
                output_parts.append("")
        
        elif action_type == "ムーブ":
            output_parts.append(f"{position}ムーブ")


# =========================
# 出力
# =========================
st.subheader("生成された投票コメント")

# 空の部分を除外
final_output = " ".join([part for part in output_parts if part])

if final_output:
    st.code(final_output, language=None)
    st.button("📋 クリップボードにコピー", 
              on_click=lambda: st.write("※ブラウザの機能を使ってコピーしてください"))
else:
    st.info("行動を選択してください")

# =========================
# 補足情報
# =========================
with st.expander("📖 投票ルール詳細"):
    st.markdown("""
    ### ポケモンの位置
    ```
    奥　側　Ａ　Ｂ　Ｃ
    手前側　１　２　３
    ```
    
    ### 投票例
    - `1まもる 2でんこうせっかＢ 3モロバレル`
      - 1: まもる
      - 2: Bにでんこうせっか
      - 3: モロバレルに交代
    
    ### 補足
    - 対象省略時は正面を攻撃（1→Ａ、2→Ｂ、3→Ｃ）
    - 交代: ポケモン名を直接記載
    - ムーブ: `1ムーブ` または `3ムーブ`
    - メガシンカしない: 技名の前に`？`マークをつける
    - 半角全角どちらでもOK
    """)
