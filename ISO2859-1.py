import streamlit as st
import pandas as pd

# -------------------------------
# CSV 파일 로드 (인코딩 cp949)
# -------------------------------
try:
    ac_df = pd.read_csv("Ac.csv", encoding="cp949")
    lotcode_df = pd.read_csv("LotCode.csv", encoding="cp949")
except FileNotFoundError as e:
    st.error(f"CSV 파일을 찾을 수 없습니다: {e}")
    st.stop()

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="ISO 2859-1 샘플링 계산기", layout="wide")
st.title("🧾 ISO 2859-1 보통검사1회 샘플링 계산기")
st.markdown("---")

# -------------------------------
# 입력과 결과를 좌우 컬럼으로 배치
# -------------------------------
input_col, output_col = st.columns([1, 1])  # 왼쪽 입력, 오른쪽 결과

with input_col:
    st.subheader("입력값")
    lot_size = st.number_input(
        "LOT 크기 입력",
        min_value=1,
        step=100,
        value=1000,
        help="LOT 수량 입력 (±100 단위 증가)"
    )
    inspection_level = st.selectbox(
        "검사수준 선택",
        ["S-1","S-2","S-3","S-4","G-1","G-2","G-3"],
        index=5,
        help="검사수준 선택 (기본 G-2)"
    )
    aql_values = [0.010,0.015,0.025,0.040,0.065,0.10,0.15,0.25,0.40,0.65,1.0,1.5,2.5,4.0,6.5,10,15,25,40,65,100,150,250,400,650,1000]
    aql = st.selectbox(
        "AQL 선택",
        aql_values,
        index=aql_values.index(0.65),
        help="AQL 선택 (기본 0.65)"
    )

# -------------------------------
# LOT 크기로 시료문자 찾기
# -------------------------------
def find_sample_code(lot_size, inspection_level):
    for _, row in lotcode_df.iterrows():
        try:
            start = int(str(row["Start Lot Qty"]).replace(",", "").strip())
        except:
            continue
        end = row["End Lot Qty"]
        if str(end).strip().lower() == "over":
            end = float("inf")
        else:
            try:
                end = int(str(end).replace(",", "").strip())
            except:
                continue
        if start <= lot_size <= end:
            return row.get(inspection_level, None), start, end
    return None, None, None

# -------------------------------
# Ac 값 가져오기
# -------------------------------
def get_ac(sample_char, aql_value):
    if sample_char is None:
        return None
    if aql_value < 1:
        aql_str = f"{aql_value:.3f}".rstrip("0").rstrip(".")
    else:
        aql_str = str(int(aql_value))
    df_row = ac_df[ac_df['시료문자']==sample_char]
    if df_row.empty or aql_str not in df_row.columns:
        return None
    return df_row.iloc[0][aql_str]

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
# 샘플링 계산 및 결과 표시
# -------------------------------
with output_col:
    st.subheader("샘플링")
    
    sample_char, lot_start, lot_end = find_sample_code(lot_size, inspection_level)

    if sample_char is None:
        st.error("해당 LOT 크기에 대한 시료문자를 찾을 수 없습니다.")
    else:
        ac_val = get_ac(sample_char, aql)
        if ac_val is None:
            st.error("해당 AQL에 대한 Ac 값을 찾을 수 없습니다.")
        else:
            final_char, final_ac = resolve_arrow(ac_val, sample_char, aql)
            df_row = ac_df[ac_df['시료문자']==final_char]
            sample_size = df_row['샘플크기'].values[0]

            lot_end_display = "∞" if lot_end == float('inf') else f"{lot_end:,}"

            # Ac/Re 계산 (전수검사 여부와 관계없이 항상 표시)
            try:
                re_val = int(float(final_ac)) + 1
            except:
                re_val = "계산불가"
            ac_re_text = f"{final_ac} / {re_val}"

            # 샘플링 수량 표시 (전수검사일 경우 "전수검사")
            if sample_size >= lot_size:
                sample_size_text = "전수검사"
            else:
                sample_size_text = f"{sample_size} 개"

            result_df = pd.DataFrame({
                "항목": ["LOT 크기 범위", "시료문자", "샘플링 수량", "Ac/Re"],
                "값": [
                    f"{lot_start:,} ~ {lot_end_display} 개",
                    final_char,
                    sample_size_text,
                    ac_re_text
                ]
            })

            st.table(result_df)

