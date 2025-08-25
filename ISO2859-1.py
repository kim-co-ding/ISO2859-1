import streamlit as st
import math

st.title("ISO 2859-1 샘플링 계산기\n(보통검사1회)")

# --- 사용자 입력 ---
col1, col2, col3 = st.columns(3)

with col1:
    inspection_level = st.selectbox(
        "검사수준 선택", 
        ['S-1','S-2','S-3','S-4','G-1','G-2','G-3'],
        index=5  # 'G-2' 초기값
    )

with col2:
    aql = st.selectbox(
        "AQL 선택", 
        [0.1,0.15,0.25,0.4,0.65,1.0,1.5,2.5],
        index=4  # 0.65 초기값
    )

with col3:
    lot_size = st.number_input(
        "LOT 크기 입력", 
        min_value=1, 
        step=100,
        value=1000  # 초기값
    )

# --- ISO 2859-1 G-2 기준 샘플링 테이블 (보통검사1회) ---
# LOT 범위 -> 기본 샘플 수, 시료문자 (Code Letter)
lot_table = [
    (2, 8, 'A', 2),
    (9, 15, 'B', 3),
    (16, 25, 'C', 5),
    (26, 50, 'D', 8),
    (51, 90, 'E', 13),
    (91, 150, 'F', 20),
    (151, 280, 'G', 32),
    (281, 500, 'H', 50),
    (501, 1200, 'J', 80),
    (1201, 3200, 'K', 125),
    (3201, 10000, 'L', 200),
    (10001, 35000, 'M', 315),
    (35001, 150000, 'N', 500),
    (150001, 500000, 'P', 800),
    (500001, 1000000, 'Q', 1250),
    (1000001, 3500000, 'R', 2000),
    (3500001, 15000000, 'S', 3150),
    (15000001, 50000000, 'T', 5000),
    (50000001, 100000000, 'U', 8000),
    (100000001, 350000000, 'V', 12500),
]

# 검사수준 보정계수
inspection_factors = {
    'S-1': 0.4,
    'S-2': 0.6,
    'S-3': 0.8,
    'S-4': 1.0,
    'G-1': 0.8,
    'G-2': 1.0,
    'G-3': 1.2
}

# AQL별 비율 (Percent)
aql_table = {0.1:0.1, 0.15:0.15, 0.25:0.25, 0.4:0.4, 0.65:0.65, 1.0:1.0, 1.5:1.5, 2.5:2.5}

# --- LOT 크기 -> 샘플 크기 및 시료문자 ---
def get_sample_info(lot):
    for min_lot, max_lot, code, base_sample in lot_table:
        if min_lot <= lot <= max_lot:
            return code, base_sample, (min_lot, max_lot)
    return None, math.ceil(math.sqrt(lot)), (lot, lot)

code_letter, base_sample, lot_range = get_sample_info(lot_size)

# 검사수준 보정
factor = inspection_factors[inspection_level]
adjusted_sample = math.ceil(base_sample * factor)

# Ac, Re 계산
Ac = math.floor(adjusted_sample * aql_table[aql] / 100)
Re = Ac + 1

# --- 결과 출력 ---
st.subheader("[ 샘플링 수량 및 Ac/Re 계산결과 ]")
st.write(f"1. LOT크기 범위 : {lot_range[0]:,} ~ {lot_range[1]:,} 개")
st.write(f"2. 시료문자 : {code_letter}")
st.write(f"3. 샘플링 수량 : {adjusted_sample:,} 개")
st.write(f"4. Ac/Re : {Ac} / {Re}")

