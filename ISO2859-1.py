import streamlit as st
import pandas as pd

# -------------------------------
# CSV 파일 로드 (인코딩 cp949)
# -------------------------------
ac_df = pd.read_csv("Ac.csv", encoding="cp949")
lotcode_df = pd.read_csv("LotCode.csv", encoding="cp949")

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="ISO 2859-1 샘플링 계산기", layout="wide")
st.title("ISO 2859-1 샘플링 계산기")

st.markdown("---")

# -------------------------------
# 입력 영역 (3컬럼)
# -------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    inspection_level = st.selectbox(
        "검사수준 선택",
        ["S-1","S-2","S-3","S-4","G-1","G-2","G-3"],
        index=5,
        help="검사수준 선택 (기본 G-2)"
    )

with col2:
    aql_values = [0.010,0.015,0.025,0.040,0.065,0.10,0.15,0.25,0.40,0.65,1.0,1.5,2.5,4.0,6.5,10,15,25,40,65,100,150,250,400,650,1000]
    aql = st.selectbox(
        "AQL 선택",
        aql_values,
        index=aql_values.index(0.65),
        help="AQL 선택 (기본 0.65)"
    )

with col3:
    lot_size = st.number_input(
        "LOT 크기 입력",
        min_value=1,
        step=100,
        value=1000,
        help="LOT 수량 입력 (±100 단위 증가)"
    )

st.markdown("---")

# -------------------------------
# LOT 크기로 시료문자 찾기
# -------------------------------
def find_sample_code(lot_size, inspection_level):
    for _, row in lotcode_df.iterrows():
        start = int(str(row["Start Lot Qty"]).replace(",", ""))
        end = row["End Lot Qty"]
        if str(end).lower() == "over":
            end = float("inf")
        else:
            end = int(str(end).replace(",", ""))
        if start <= lot_size <= end:
            return row[inspection_level]
    return None

# -------------------------------
# Ac 값 가져오기
# -------------------------------
def get_ac(sample_char, aql_value):
    if aql_value < 1:
        aql_str = f"{aql_value:.3f}".rstrip("0").rstrip(".")
    else:
        aql_str = str(int(aql_value))
    ac_row = ac_df[ac_df['시료문자']==sample_char].iloc[0]
    ac_val = ac_row[aql_str]
    return ac_val

# -------------------------------
# 화살표 처리
# -------------------------------
def resolve_arrow(ac_val, sample_char, aql_value):
    while str(ac_val) in ["↓","↑"]:
        ac_idx = ac_df.index[ac_df['시료문자']==sample_char][0]
        if ac_val == "↓":
            ac_idx += 1
        elif ac_val == "↑":
            ac_idx -= 1
        if ac_idx < 0 or ac_idx >= len(ac_df):
            break
        sample_char = ac_df.iloc[ac_idx]['시료문자']
        ac_val = get_ac(sample_char, aql_value)
    return sample_char, ac_val

# -------------------------------
# 값 자동 계산
# -------------------------------
sample_char = find_sample_code(lot_size, inspection_level)
if sample_char is None:
    st.error("해당 LOT 크기에 대한 시료문자를 찾을 수 없습니다.")
else:
    ac_val = get_ac(sample_char, aql)
    final_char, final_ac = resolve_arrow(ac_val, sample_char, aql)
    sample_size = ac_df[ac_df['시료문자']==final_char]['샘플크기'].values[0]
    try:
        re_val = int(final_ac) + 1
    except:
        re_val = "계산불가"

    # -------------------------------
    # 결과 영역 스타일링
    # -------------------------------
    with st.container():
        st.markdown("### [ 샘플크기 및 Ac/Re 계산 결과 ]")
        st.markdown(f"""
        **1. 시료문자 :** {final_char}  
        **2. 샘플크기 :** {sample_size} 개  
        **3. Ac :** {final_ac}  
        **4. Re :** {re_val}  
        """)
