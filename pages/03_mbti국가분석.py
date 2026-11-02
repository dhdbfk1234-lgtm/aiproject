import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# 페이지 설정
st.set_page_config(
    page_title="국가별 MBTI 비율",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 국가별 MBTI 비율 분석")
st.write("국가를 선택하면 해당 국가의 16가지 MBTI 비율을 확인할 수 있습니다.")

# MBTI 유형
MBTI_TYPES = [
    "INFJ", "ISFJ", "INTP", "ISFP",
    "ENTP", "INFP", "ENTJ", "ISTP",
    "INTJ", "ESFP", "ESTJ", "ENFP",
    "ESTP", "ISTJ", "ENFJ", "ESFJ"
]

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("countriesMBTI_16types.csv")

    required_columns = ["Country"] + MBTI_TYPES

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"CSV에 필요한 열이 없습니다: {missing_columns}"
        )

    df = df[required_columns].copy()

    for col in MBTI_TYPES:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=required_columns)

    return df


try:
    df = load_data()

except FileNotFoundError:
    st.error(
        "countriesMBTI_16types.csv 파일을 찾을 수 없습니다. "
        "app.py와 같은 GitHub 저장소에 CSV 파일을 올려 주세요."
    )
    st.stop()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# 국가 선택
countries = sorted(df["Country"].unique())

selected_country = st.selectbox(
    "국가를 선택하세요.",
    countries
)

# 선택한 국가 데이터
country_data = df[
    df["Country"] == selected_country
].iloc[0]

# MBTI 비율 추출
mbti_data = country_data[MBTI_TYPES].astype(float)

# 원본 값이 0~1 범위의 비율이면 백분율로 변환
if mbti_data.max() <= 1:
    mbti_data = mbti_data * 100

# 높은 비율부터 정렬
chart_data = pd.DataFrame({
    "MBTI": MBTI_TYPES,
    "비율": mbti_data.values
})

chart_data = chart_data.sort_values(
    "비율",
    ascending=False
).reset_index(drop=True)


# 가장 높은 MBTI
top_mbti = chart_data.iloc[0]["MBTI"]
top_ratio = chart_data.iloc[0]["비율"]

col1, col2 = st.columns(2)

col1.metric(
    "선택한 국가",
    selected_country
)

col2.metric(
    "비율이 가장 높은 MBTI",
    top_mbti,
    f"{top_ratio:.2f}%"
)


# 그래프 제목
st.subheader(f"📊 {selected_country}의 MBTI 비율")


# 색상 설정
# 1위는 빨간색
# 나머지는 진한 파랑에서 연한 파랑으로 변화
blue_gradient = LinearSegmentedColormap.from_list(
    "blue_gradient",
    ["#1769D2", "#DCEBFF"]
)

colors = ["#E53935"]

for i in range(1, len(chart_data)):
    position = (i - 1) / (len(chart_data) - 2)

    colors.append(
        blue_gradient(position)
    )


# 막대그래프 생성
fig, ax = plt.subplots(figsize=(10, 7))

bars = ax.barh(
    chart_data["MBTI"],
    chart_data["비율"],
    color=colors
)

# 1위가 그래프 맨 위에 오도록 설정
ax.invert_yaxis()

# 축과 제목
ax.set_xlabel("비율 (%)")
ax.set_ylabel("MBTI 유형")
ax.set_title(f"{selected_country} - MBTI Distribution")

# 배경 격자
ax.grid(
    axis="x",
    linestyle="--",
    alpha=0.3
)

ax.set_axisbelow(True)

# 막대 끝에 비율 표시
max_value = max(chart_data["비율"].max(), 1)

ax.set_xlim(
    0,
    max_value * 1.2
)

for bar, value in zip(
    bars,
    chart_data["비율"]
):
    ax.text(
        bar.get_width() + max_value * 0.015,
        bar.get_y() + bar.get_height() / 2,
        f"{value:.2f}%",
        va="center",
        fontsize=9
    )

# 레이아웃 정리
fig.tight_layout()

# Streamlit에 그래프 출력
st.pyplot(fig, use_container_width=True)

plt.close(fig)


# 데이터 표
with st.expander("📋 MBTI 비율 자세히 보기"):
    display_data = chart_data.copy()

    display_data["비율"] = display_data["비율"].map(
        lambda x: f"{x:.2f}%"
    )

    st.dataframe(
        display_data,
        hide_index=True,
        use_container_width=True
    )


# 안내 문구
st.caption(
    "※ 본 그래프는 제공된 CSV 데이터의 국가별 MBTI 비율을 나타냅니다."
)
