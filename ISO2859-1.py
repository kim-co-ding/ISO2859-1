import streamlit as st
import math

# 제목 줄바꿈
st.title("ISO 2859-1 샘플링 계산기\n(보통검사1회)")

# 사용자 입력을 가로로 배치
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
        step=1,
        value=1000  # 초기값 1,000
    )

# ISO 2859-1 보통검사 1회 기준 샘플링 수량 (G-2 기준)
sample_table = [
    (2, 8, 2),
    (9, 15, 3),
    (16, 25, 5),
    (26, 50, 8),
    (51, 90, 13),
    (91, 150, 20),
    (151, 280, 32),
    (281, 500, 50),
    (501, 1200, 80),
    (1201, 3200, 125),
    (3201, 10000, 200),
    (10001, 35000, 315),
    (35001, 150000, 500),
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

# AQL별 허용불량
aql_table = {
    0.1: 0.1,
    0.15: 0.15,
    0.25: 0.25,
    0.4: 0.4,
    0.65: 0.65,
    1.0: 1.0,
    1.5: 1.5,
    2.5: 2.5
}

# LOT 범위 자동 조회
def get_sample_size(lot):
    for min_lot, max_lot, n in sample_table:
        if min_lot <= lot <= max_lot:
            return n, (min_lot, max_lot)
    return math.ceil(math.sqrt(lot)), (lot, lot)

base_sample, lot_range = get_sample_size(lot_size)

# 검사수준 보정
factor = inspection_factors[inspection_level]
adjusted_sample = math.ceil(base_sample * factor)

# Ac, Re 계산
Ac = math.floor(adjusted_sample * aql_table[aql] / 100)
Re = Ac + 1

# 결과 표시
st.subheader("[ 샘플링 수량 및 Ac/Re 계산결과 ]")
st.write(f"1. LOT크기 범위: {lot_range[0]} ~ {lot_range[1]}")
st.write(f"2. 샘플링 수량: {adjusted_sample}")
st.write(f"3. Ac/Re : {Ac} / {Re}")
