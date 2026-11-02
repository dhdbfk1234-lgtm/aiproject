import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path

# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="국가별 MBTI 분석",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 국가별 MBTI 분석")
st.write("국가를 선택하면 16가지 MBTI 유형별 비율을 막대그래프로 보여줍니다.")

# ==========================================
# 2. MBTI 유형
# ==========================================

MBTI_TYPES = [
    "INFJ", "ISFJ", "INTP", "ISFP",
    "ENTP", "INFP", "ENTJ", "ISTP",
    "INTJ", "ESFP", "ESTJ", "ENFP",
    "ESTP", "ISTJ", "ENFJ", "ESFJ"
]

# ==========================================
# 3. CSV 파일 찾기
# ==========================================

def find_csv_file():
    possible_paths = [
        Path("countriesMBTI_16types.csv"),
        Path("data/countriesMBTI_16types.csv"),
        Path("dataset/countriesMBTI_16types.csv"),
        Path(__file__).resolve().parent / "countriesMBTI_16types.csv",
        Path(__file__).resolve().parent / "data/countriesMBTI_16types.csv",
        Path(__file__).resolve().parent / "dataset/countriesMBTI_16types.csv",
    ]

    for path in possible_paths:
        if path.is_file():
            return path

    return None


# ==========================================
# 4. 데이터 불러오기
# ==========================================

@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)

    required_columns = ["Country"] + MBTI_TYPES

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "CSV 파일에 다음 열이 없습니다: "
            + ", ".join(missing_columns)
        )

    df = df[required_columns].copy()

    df["Country"] = df["Country"].astype(str).str.strip()

    for col in MBTI_TYPES:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=required_columns)
    df = df[df["Country"] != ""]
    df = df.drop_duplicates(subset=["Country"])

    if df.empty:
        raise ValueError("분석할 데이터가 없습니다.")

    return df


csv_path = find_csv_file()

# CSV 파일을 찾지 못했을 때 직접 업로드할 수 있도록 설정
if csv_path is None:
    st.warning(
        "GitHub 저장소에서 CSV 파일을 찾을 수 없습니다. "
        "아래에서 파일을 직접 업로드해 주세요."
    )

    uploaded_file = st.file_uploader(
        "countriesMBTI_16types.csv 업로드",
        type=["csv"]
    )

    if uploaded_file is None:
        st.info(
            "CSV 파일을 업로드하거나 GitHub 저장소에 "
            "countriesMBTI_16types.csv 파일을 추가해 주세요."
        )
        st.stop()

    try:
        df = pd.read_csv(uploaded_file)

        required_columns = ["Country"] + MBTI_TYPES

        missing_columns = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:
            st.error(
                "필요한 열이 없습니다: "
                + ", ".join(missing_columns)
            )
            st.stop()

        df = df[required_columns].copy()
        df["Country"] = df["Country"].astype(str).str.strip()

        for col in MBTI_TYPES:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=required_columns)
        df = df[df["Country"] != ""]
        df = df.drop_duplicates(subset=["Country"])

    except Exception as e:
        st.error(f"CSV 파일을 읽을 수 없습니다: {e}")
        st.stop()

else:
    try:
        df = load_data(str(csv_path))

    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        st.stop()


# ==========================================
# 5. 국가 선택
# ==========================================

countries = sorted(df["Country"].unique().tolist())

if not countries:
    st.error("선택할 국가가 없습니다.")
    st.stop()

selected_country = st.selectbox(
    "🌎 국가 선택",
    countries
)

# 선택한 국가의 데이터
country_data = df[
    df["Country"] == selected_country
].iloc[0]

# ==========================================
# 6. MBTI 비율 계산
# ==========================================

mbti_data = country_data[MBTI_TYPES].astype(float)

# 원본이 0~1 사이 비율이라면 백분율로 변환
if mbti_data.max() <= 1:
    mbti_data = mbti_data * 100

chart_data = pd.DataFrame({
    "MBTI": MBTI_TYPES,
    "비율": mbti_data.values
})

# 비율이 높은 순서대로 정렬
chart_data = chart_data.sort_values(
    "비율",
    ascending=False
).reset_index(drop=True)

# 1위 MBTI
top_mbti = chart_data.iloc[0]["MBTI"]
top_ratio = chart_data.iloc[0]["비율"]

# ==========================================
# 7. 상단 통계
# ==========================================

col1, col2, col3 = st.columns(3)

col1.metric(
    "분석 국가",
    selected_country
)

col2.metric(
    "1위 MBTI",
    top_mbti
)

col3.metric(
    "1위 비율",
    f"{top_ratio:.2f}%"
)

# ==========================================
# 8. 그래프 색상 설정
# ==========================================

st.divider()

st.subheader(
    f"📊 {selected_country}의 MBTI 비율"
)

# 1위는 빨간색
first_color = "#E53935"

# 나머지는 진한 파랑에서 연한 파랑으로
blue_gradient = LinearSegmentedColormap.from_list(
    "blue_gradient",
    ["#1565C0", "#DCEBFF"]
)

colors = [first_color]

remaining_count = len(chart_data) - 1

for i in range(remaining_count):
    if remaining_count > 1:
        position = i / (remaining_count - 1)
    else:
        position = 0

    colors.append(blue_gradient(position))


# ==========================================
# 9. 막대그래프 생성
# ==========================================

fig, ax = plt.subplots(figsize=(11, 8))

bars = ax.barh(
    chart_data["MBTI"],
    chart_data["비율"],
    color=colors,
    height=0.72
)

# 1위가 위에 표시되도록 설정
ax.invert_yaxis()

ax.set_title(
    f"{selected_country} - MBTI Distribution",
    fontsize=16,
    pad=15
)

ax.set_xlabel("비율 (%)", fontsize=11)
ax.set_ylabel("MBTI 유형", fontsize=11)

# 그래프 격자
ax.grid(
    axis="x",
    linestyle="--",
    alpha=0.25
)

ax.set_axisbelow(True)

# 막대 끝에 비율 표시
max_value = max(
    float(chart_data["비율"].max()),
    1
)

ax.set_xlim(
    0,
    max_value * 1.22
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

fig.tight_layout()

st.pyplot(
    fig,
    use_container_width=True
)

plt.close(fig)

# ==========================================
# 10. 데이터 표
# ==========================================

with st.expander("📋 MBTI 비율 자세히 보기"):
    display_data = chart_data.copy()

    display_data["비율"] = display_data["비율"].map(
        lambda value: f"{value:.2f}%"
    )

    st.dataframe(
        display_data,
        hide_index=True,
        use_container_width=True
    )

# ==========================================
# 11. 안내 문구
# ==========================================

st.divider()

st.caption(
    "이 그래프는 제공된 CSV 파일의 국가별 MBTI 비율을 나타냅니다. "
    "조사 표본 및 방법에 따라 실제 인구의 분포와 다를 수 있습니다."
)
