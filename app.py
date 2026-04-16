# ============================================================
# 가공식품 트렌드 & 매출 인텔리전스 허브
# app.py  ·  Streamlit >= 1.35
# ============================================================
# 구조:
#   1. 페이지 설정 & 전역 CSS
#   2. 샘플 데이터 (→ 실데이터 교체 포인트 명시)
#   3. 재사용 컴포넌트 (kpi_card, section_header, insight_row …)
#   4. 사이드바
#   5. 탭별 뷰 함수
#   6. main()
# ============================================================

from __future__ import annotations

import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from datetime import datetime, timedelta

# ─────────────────────────────────────────────────────────────
# 1. 페이지 설정
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="식품 트렌드 인텔리전스 허브",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# 1-a. 전역 CSS
# ─────────────────────────────────────────────────────────────

GLOBAL_CSS = """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');

html, body, [class*="css"],
[data-testid="stAppViewContainer"],
[data-testid="stSidebar"],
[data-testid="stHeader"],
.stTabs [data-baseweb="tab-list"] {
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

:root {
    --bg:          #f7f8fa;
    --surface:     #ffffff;
    --surface-2:   #f4f5f8;
    --border:      #e8eaed;
    --border-2:    #d1d5db;
    --text-1:      #0d0f12;
    --text-2:      #3d4350;
    --text-3:      #6b7280;
    --text-4:      #9ca3af;
    --brand:       #5033EA;
    --brand-light: #ede9fe;
    --brand-mid:   #7c5ff5;
    --green:       #059669;
    --green-bg:    #d1fae5;
    --red:         #dc2626;
    --red-bg:      #fee2e2;
    --amber:       #d97706;
    --amber-bg:    #fef3c7;
    --radius-sm:   10px;
    --radius-md:   16px;
    --radius-lg:   24px;
    --radius-xl:   32px;
    --shadow-sm:   0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
    --shadow-md:   0 4px 16px rgba(0,0,0,.07), 0 2px 4px rgba(0,0,0,.04);
}

.stApp { background: var(--bg); color: var(--text-1); }
.block-container { padding: 1.4rem 2rem 3rem; max-width: 1540px; }
section[data-testid="stSidebar"] > div:first-child { padding-top: 1.2rem; }

/* Hero */
.hero {
    background: linear-gradient(130deg, #ffffff 0%, #f5f2ff 45%, #f0f7ff 100%);
    border: 1px solid #e6e0f8;
    border-radius: var(--radius-xl);
    padding: 28px 32px 24px;
    margin-bottom: 4px;
    box-shadow: var(--shadow-md);
    position: relative; overflow: hidden;
}
.hero::before {
    content: ''; position: absolute; top: -40px; right: -40px;
    width: 240px; height: 240px;
    background: radial-gradient(circle, rgba(112,80,245,.10) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-eyebrow { font-size: 11px; font-weight: 700; letter-spacing: .12em;
    text-transform: uppercase; color: var(--brand); margin-bottom: 8px; }
.hero-title   { font-size: 28px; font-weight: 800; letter-spacing: -.025em;
    color: var(--text-1); line-height: 1.25; margin-bottom: 8px; }
.hero-sub     { font-size: 14px; color: var(--text-3); line-height: 1.75; max-width: 780px; }

/* Section header */
.sec-title { font-size: 18px; font-weight: 800; letter-spacing: -.02em;
    color: var(--text-1); margin: 4px 0 4px; }
.sec-sub   { font-size: 13px; color: var(--text-3); margin-bottom: 14px; line-height: 1.6; }

/* Card */
.card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-lg); padding: 20px 22px;
    box-shadow: var(--shadow-sm);
}

/* KPI card */
.kpi-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-lg); padding: 20px 22px 18px;
    box-shadow: var(--shadow-sm); min-height: 116px;
}
.kpi-eyebrow { font-size: 11px; font-weight: 700; letter-spacing: .09em;
    text-transform: uppercase; color: var(--text-4); margin-bottom: 10px; }
.kpi-value   { font-size: 32px; font-weight: 900; letter-spacing: -.03em;
    color: var(--text-1); line-height: 1; }
.kpi-sub     { font-size: 12px; color: var(--text-3); margin-top: 6px; }
.kpi-delta-up  { display: inline-flex; align-items: center; gap: 4px; font-size: 12px;
    font-weight: 700; color: var(--green); background: var(--green-bg);
    border-radius: 999px; padding: 3px 10px; margin-top: 10px; }
.kpi-delta-dn  { display: inline-flex; align-items: center; gap: 4px; font-size: 12px;
    font-weight: 700; color: var(--red); background: var(--red-bg);
    border-radius: 999px; padding: 3px 10px; margin-top: 10px; }
.kpi-delta-neu { display: inline-flex; align-items: center; gap: 4px; font-size: 12px;
    font-weight: 700; color: var(--amber); background: var(--amber-bg);
    border-radius: 999px; padding: 3px 10px; margin-top: 10px; }

/* Insight row */
.insight-row {
    display: flex; gap: 14px; align-items: flex-start;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-md); padding: 16px 18px; margin-bottom: 10px;
    box-shadow: var(--shadow-sm);
}
.insight-icon  { font-size: 22px; flex-shrink: 0; margin-top: 2px; }
.insight-title { font-size: 14px; font-weight: 800; color: var(--text-1); margin-bottom: 4px; }
.insight-text  { font-size: 13px; color: var(--text-3); line-height: 1.65; }

/* Badge */
.badge { display: inline-block; border-radius: 999px; padding: 4px 12px;
    font-size: 11px; font-weight: 700; letter-spacing: .03em; margin: 0 6px 6px 0; }
.badge-brand { background: var(--brand-light); color: var(--brand); }
.badge-green { background: var(--green-bg);    color: var(--green); }
.badge-amber { background: var(--amber-bg);    color: var(--amber); }
.badge-gray  { background: var(--surface-2);   color: var(--text-3); }

/* Rank item */
.rank-item {
    display: flex; align-items: center; gap: 14px;
    padding: 12px 16px; border-radius: var(--radius-md);
    border: 1px solid var(--border); background: var(--surface);
    margin-bottom: 8px;
}
.rank-no       { font-size: 15px; font-weight: 900; color: var(--text-4); min-width: 24px; text-align: center; }
.rank-no.top   { color: var(--brand); }
.rank-body     { flex: 1; }
.rank-name     { font-size: 14px; font-weight: 700; color: var(--text-1); }
.rank-meta     { font-size: 12px; color: var(--text-3); margin-top: 2px; }
.rank-right    { text-align: right; }
.rank-val      { font-size: 15px; font-weight: 800; color: var(--text-1); }
.rank-delta-up { font-size: 11px; font-weight: 700; color: var(--green); }
.rank-delta-dn { font-size: 11px; font-weight: 700; color: var(--red); }

/* Divider */
.divider { border: none; border-top: 1px solid var(--border); margin: 18px 0; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 2px solid var(--border); background: transparent; }
.stTabs [data-baseweb="tab"] { border-radius: var(--radius-sm) var(--radius-sm) 0 0;
    font-weight: 700; font-size: 13px; padding: 10px 18px; color: var(--text-3); }
.stTabs [aria-selected="true"] { background: var(--brand-light);
    color: var(--brand) !important; border-bottom: 2px solid var(--brand); }

/* Sidebar labels */
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] .stSlider label {
    font-size: 12px; font-weight: 700; color: var(--text-2);
    text-transform: uppercase; letter-spacing: .05em;
}
.sidebar-logo    { font-size: 13px; font-weight: 800; letter-spacing: .06em;
    text-transform: uppercase; color: var(--brand); margin-bottom: 4px; }
.sidebar-tagline { font-size: 12px; color: var(--text-3); margin-bottom: 20px; }

/* Upload zone */
.upload-zone {
    background: var(--surface-2); border: 2px dashed var(--border-2);
    border-radius: var(--radius-lg); padding: 24px; text-align: center;
    color: var(--text-3); font-size: 13px;
}

/* Footer */
.footer { font-size: 11px; color: var(--text-4); text-align: right;
    margin-top: 32px; padding-top: 16px; border-top: 1px solid var(--border); }
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# 2. 샘플 데이터
#    ★ 실데이터 교체 포인트: @st.cache_data 함수를 CSV/API 로드로 교체
# ─────────────────────────────────────────────────────────────

TODAY = datetime.today()
WEEKS = pd.date_range(TODAY - timedelta(weeks=11), periods=12, freq="W")
BRAND_PALETTE = [
    "#5033EA", "#7c5ff5", "#059669", "#dc2626", "#d97706",
    "#0891b2", "#7c3aed", "#db2777", "#65a30d", "#0369a1",
]


@st.cache_data(ttl=600)
def load_category_data() -> pd.DataFrame:
    """카테고리 KPI — 교체 포인트 ①: pd.read_csv('data/category_kpi.csv')"""
    return pd.DataFrame({
        "카테고리":       ["오일·발사믹","과자·스낵","파스타면","소스","향신료",
                          "HMR","우유·유제품","음료","치즈","샤퀴테리","캐비아"],
        "트렌드점수":     [78,91,76,94,72,96,83,89,86,68,62],
        "매출지수":       [82,88,73,91,69,95,84,87,80,65,59],
        "SNS화제성":      [71,93,67,90,74,92,79,95,85,63,70],
        "검색증가율":     [12,27, 9,31,11,29,14,25,16, 6, 8],
        "전년대비매출":   [ 8,12, 5,14, 4,17, 9,11,10, 3, 6],
    })


@st.cache_data(ttl=600)
def load_hot_items() -> pd.DataFrame:
    """급상승 상품 — 교체 포인트 ②"""
    return pd.DataFrame({
        "상품명":     ["두쫀쿠 피스타치오 크림쿠키","트러플 머쉬룸 파스타소스","저당 고단백 요거트",
                      "바질 페스토","프리미엄 올리브오일","제로슈가 탄산음료","크림치즈 딥","우유버터 비스킷"],
        "카테고리":   ["과자·스낵","소스","우유·유제품","소스","오일·발사믹","음료","치즈","과자·스낵"],
        "SNS증가율":  [38,27,24,21,18,22,19,17],
        "검색증가율": [42,31,26,19,15,28,16,14],
        "구매전환":   [7.6,6.9,8.4,5.7,6.1,7.2,5.9,4.8],
        "트렌드유형": ["유사상품 탐색형","실구매 확장형","실구매 확장형",
                      "레시피 연관형","프리미엄 원재료형","기능성 대체형","홈파티 연관형","캐릭터/선물형"],
    })


@st.cache_data(ttl=600)
def load_brand_popup() -> pd.DataFrame:
    """브랜드·팝업 — 교체 포인트 ③"""
    return pd.DataFrame({
        "브랜드":    ["브레디크","라구델리","그릭랩","오로바일렌","치즈하우스","테이스티테이블"],
        "카테고리":  ["과자·스낵","소스·파스타","유제품","오일·발사믹","치즈","HMR"],
        "키워드":    ["피스타치오, 쿠키, 선물","트러플, 파스타, 홈파인다이닝",
                     "고단백, 저당, 아침식사","싱글오리진, 엑스트라버진",
                     "와인안주, 플래터","셰프컬래버, 냉장간편식"],
        "팝업적합도":[92,89,90,84,87,94],
        "추천액션":  ["디저트 큐레이션 존","주말 미식 테마전","헬시 브런치 존",
                     "명절 선물 세트","와인 페어링 존","셰프 협업 팝업"],
    })


@st.cache_data(ttl=600)
def load_sales_weekly() -> pd.DataFrame:
    """주차별 매출지수 — 교체 포인트 ④"""
    cat_df = load_category_data()
    bases = [70,82,60,85,55,92,77,80,73,48,39]
    rows = []
    for cat, base in zip(cat_df["카테고리"], bases):
        rng = np.random.default_rng(abs(hash(cat)) % (2**32))
        vals = np.maximum(base + np.cumsum(rng.integers(-4, 7, size=len(WEEKS))), 20)
        for d, v in zip(WEEKS, vals):
            rows.append({"주차": d, "카테고리": cat, "매출지수": int(v)})
    return pd.DataFrame(rows)


@st.cache_data(ttl=600)
def load_hashtag_data() -> pd.DataFrame:
    """해시태그 인텔리전스 — 교체 포인트 ⑤"""
    return pd.DataFrame({
        "해시태그":    ["#피스타치오","#트러플파스타","#고단백요거트","#제로슈가",
                       "#올리브오일","#홈파티치즈","#냉장간편식","#발사믹"],
        "7일증가율":   [64,48,37,35,29,25,31,18],
        "조회지수":    [96,84,79,82,68,63,74,55],
        "카테고리":    ["과자·스낵","소스·파스타","우유·유제품","음료",
                       "오일·발사믹","치즈","HMR","오일·발사믹"],
        "해석":        ["직접 구매보다 유사 풍미 탐색이 함께 증가",
                       "레시피/집밥 콘텐츠 유입과 연결",
                       "실구매·재구매형 검색 신호가 강함",
                       "대체재 비교 검색이 동반됨",
                       "프리미엄 선물 수요와 연계 가능",
                       "와인/홈파티 맥락 검색과 연결",
                       "간편식 신제품 탐색 수요 반영",
                       "샐러드·드레싱 연관 검색 동반"],
    })


@st.cache_data(ttl=600)
def load_holiday_news() -> pd.DataFrame:
    """명절 속보 목록 — 교체 포인트 ⑥"""
    return pd.DataFrame({
        "업로드일":  ["2026-01-10","2026-01-18","2026-01-24","2026-09-16"],
        "제목":      ["설 선물세트 초반 매출 속보","설 직전 HMR 집중 판매 현황",
                     "설 연휴 직후 카테고리 회고","추석 선물세트 주간 속보"],
        "상태":      ["게시","게시","초안","예정"],
        "핵심 카테고리":["오일·발사믹, 치즈","HMR, 소스","전 카테고리","유제품, 오일·발사믹"],
    })


# ─────────────────────────────────────────────────────────────
# 3. 재사용 컴포넌트
# ─────────────────────────────────────────────────────────────

def section_header(title: str, subtitle: str = "") -> None:
    st.markdown(f'<div class="sec-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="sec-sub">{subtitle}</div>', unsafe_allow_html=True)


def kpi_card(label: str, value: str, delta: str,
             delta_dir: str = "up", sub: str = "") -> None:
    cls = {"up": "kpi-delta-up", "down": "kpi-delta-dn", "neutral": "kpi-delta-neu"}.get(delta_dir, "kpi-delta-neu")
    icon = {"up": "▲", "down": "▼", "neutral": "–"}.get(delta_dir, "–")
    sub_html = f"<div class='kpi-sub'>{sub}</div>" if sub else ""
    st.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-eyebrow">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'{sub_html}'
        f'<div class="{cls}">{icon} {delta}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def insight_row(icon: str, title: str, body: str) -> None:
    st.markdown(
        f'<div class="insight-row">'
        f'<div class="insight-icon">{icon}</div>'
        f'<div><div class="insight-title">{title}</div>'
        f'<div class="insight-text">{body}</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def rank_item(rank: int, name: str, meta: str,
              val: str, delta: str, up: bool) -> None:
    top_cls = "top" if rank <= 3 else ""
    dcls = "rank-delta-up" if up else "rank-delta-dn"
    dicon = "▲" if up else "▼"
    st.markdown(
        f'<div class="rank-item">'
        f'<div class="rank-no {top_cls}">#{rank}</div>'
        f'<div class="rank-body">'
        f'<div class="rank-name">{name}</div>'
        f'<div class="rank-meta">{meta}</div></div>'
        f'<div class="rank-right">'
        f'<div class="rank-val">{val}</div>'
        f'<div class="{dcls}">{dicon} {delta}</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def badge_html(text: str, color: str = "brand") -> str:
    return f'<span class="badge badge-{color}">{text}</span>'


def divider() -> None:
    st.markdown('<hr class="divider">', unsafe_allow_html=True)


# Altair 공통 테마
def _altair_theme():
    return {
        "config": {
            "view":   {"strokeWidth": 0},
            "axis":   {"grid": True, "gridColor": "#e8eaed", "gridOpacity": .7,
                       "labelFont": "Pretendard", "titleFont": "Pretendard",
                       "labelColor": "#6b7280", "titleColor": "#3d4350",
                       "labelFontSize": 11, "titleFontSize": 11},
            "legend": {"labelFont": "Pretendard", "titleFont": "Pretendard",
                       "labelFontSize": 11, "titleFontSize": 11},
            "font":   "Pretendard",
        }
    }

alt.themes.register("hub", _altair_theme)
alt.themes.enable("hub")


# ─────────────────────────────────────────────────────────────
# 4. 사이드바
# ─────────────────────────────────────────────────────────────

def render_sidebar(cat_df: pd.DataFrame) -> dict:
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">🛒 Food Intel Hub</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sidebar-tagline">백화점 바이어 & 영업담당자 전용</div>',
            unsafe_allow_html=True,
        )
        st.divider()

        all_cats = cat_df["카테고리"].tolist()
        selected_cats = st.multiselect(
            "상품군 필터",
            options=all_cats,
            default=all_cats[:7],
            placeholder="카테고리를 선택하세요…",
        )
        if not selected_cats:
            selected_cats = all_cats

        period = st.selectbox(
            "조회 기간",
            ["최근 7일", "최근 30일", "최근 90일", "최근 12주"],
            index=3,
        )

        goal = st.radio(
            "사용 목적",
            ["트렌드 확인", "매출 추이", "팝업 기획", "명절 속보"],
            index=0,
        )

        threshold = st.slider(
            "SNS 급상승 기준 (%)",
            min_value=5, max_value=80, value=20, step=5,
        )

        st.divider()
        st.markdown(
            f"<div style='font-size:11px;color:#9ca3af;line-height:1.8;'>"
            f"마지막 업데이트<br>"
            f"<b style='color:#6b7280'>{TODAY.strftime('%Y-%m-%d %H:%M')}</b>"
            f"</div>",
            unsafe_allow_html=True,
        )

    return {
        "categories": selected_cats,
        "period":     period,
        "goal":       goal,
        "threshold":  threshold,
    }


# ─────────────────────────────────────────────────────────────
# 5. 탭별 뷰 함수
# ─────────────────────────────────────────────────────────────

# ── 탭 0: 전체 요약 ──────────────────────────────────────────

def tab_summary(cat_df: pd.DataFrame, hot_df: pd.DataFrame, filters: dict) -> None:
    filtered = cat_df[cat_df["카테고리"].isin(filters["categories"])]
    top_trend = filtered.nlargest(1, "트렌드점수").iloc[0]
    top_sns   = filtered.nlargest(1, "SNS화제성").iloc[0]
    top_sale  = filtered.nlargest(1, "전년대비매출").iloc[0]
    low_sale  = filtered.nsmallest(1, "매출지수").iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("이번 주 트렌드 TOP", top_trend["카테고리"],
                      f"+{top_trend['검색증가율']}% 검색 증가", "up",
                      f"트렌드점수 {top_trend['트렌드점수']}")
    with c2: kpi_card("SNS 화제성 1위", top_sns["카테고리"],
                      f"화제성 {top_sns['SNS화제성']}점", "up",
                      f"검색 +{top_sns['검색증가율']}%")
    with c3: kpi_card("매출 성장 최고", top_sale["카테고리"],
                      f"+{top_sale['전년대비매출']}% 전년대비", "up",
                      f"매출지수 {top_sale['매출지수']}")
    with c4: kpi_card("관심 필요 카테고리", low_sale["카테고리"],
                      f"매출지수 {low_sale['매출지수']}", "neutral",
                      "모니터링 권장")

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    left, right = st.columns([1.4, 1])

    with left:
        section_header("카테고리 포지션 맵",
                       "트렌드점수 × 매출지수 — 버블 크기: SNS 화제성")
        bubble = (
            alt.Chart(filtered)
            .mark_circle(opacity=0.82, stroke="white", strokeWidth=1.5)
            .encode(
                x=alt.X("트렌드점수:Q", scale=alt.Scale(domain=[45, 100])),
                y=alt.Y("매출지수:Q",   scale=alt.Scale(domain=[35, 100])),
                size=alt.Size("SNS화제성:Q",
                              scale=alt.Scale(range=[200, 1600]),
                              legend=alt.Legend(title="SNS 화제성")),
                color=alt.Color("카테고리:N",
                                scale=alt.Scale(range=BRAND_PALETTE),
                                legend=alt.Legend(title="카테고리")),
                tooltip=["카테고리","트렌드점수","매출지수","SNS화제성",
                         "검색증가율","전년대비매출"],
            ).properties(height=380)
        )
        labels = (
            alt.Chart(filtered)
            .mark_text(dy=-14, fontSize=11, fontWeight="bold", color="#3d4350")
            .encode(
                x=alt.X("트렌드점수:Q"),
                y=alt.Y("매출지수:Q"),
                text="카테고리:N",
            )
        )
        st.altair_chart(bubble + labels, use_container_width=True)

    with right:
        section_header("베스트 & 주목 상품 TOP 5",
                       "검색·SNS 기준 이번 주 주목 상품")
        top5 = hot_df.sort_values(["검색증가율","SNS증가율"], ascending=False).head(5)
        for i, (_, row) in enumerate(top5.iterrows(), 1):
            rank_item(i, row["상품명"],
                      f"{row['카테고리']} · {row['트렌드유형']}",
                      f"검색 +{row['검색증가율']}%",
                      f"SNS +{row['SNS증가율']}%", True)

    divider()
    bl, br = st.columns(2)

    with bl:
        section_header("빠른 운영 제안")
        insight_row("🎯","즉시 전개 추천",
                    "HMR·소스·음료는 신제품 반응이 빠릅니다. 주간 단위 모니터링 후 입점·확대를 검토하세요.")
        insight_row("🔗","크로스 진열 기회",
                    "파스타면 + 소스 + 치즈는 레시피 검색이 동시에 증가 중입니다. 묶음 진열 및 레시피 카드를 연계하세요.")
        insight_row("📣","행사 테마 제안",
                    "피스타치오, 트러플, 홈파티, 저당·고단백 키워드로 미니 팝업 기획이 가능합니다.")

    with br:
        section_header("카테고리별 상태 요약")
        display = (
            filtered[["카테고리","트렌드점수","SNS화제성","검색증가율","전년대비매출"]]
            .sort_values("트렌드점수", ascending=False)
            .reset_index(drop=True)
        )
        st.dataframe(display, use_container_width=True, hide_index=True)


# ── 탭 1: 인기 상품 급상승 ──────────────────────────────────

def tab_hot_items(hot_df: pd.DataFrame, filters: dict) -> None:
    thresh = filters["threshold"]
    df = hot_df.copy()
    df["판단"] = np.where(
        (df["검색증가율"] >= 25) & (df["구매전환"] >= 7),
        "✅ 실구매 확장 가능성 높음",
        "🔍 유사상품·관심 탐색 가능성 높음",
    )
    filt = df[df["SNS증가율"] >= thresh]
    if filt.empty:
        filt = df

    left, right = st.columns([1.3, 1])

    with left:
        section_header("SNS · 검색 급상승 상품",
                       f"SNS 증가율 {thresh}% 이상 필터 적용")
        # 그룹형 바 차트 (fold)
        fold_df = filt[["상품명","SNS증가율","검색증가율"]].copy()
        fold_df = fold_df.rename(columns={"SNS증가율":"SNS 증가율(%)","검색증가율":"검색 증가율(%)"})
        melted = fold_df.melt("상품명", var_name="지표", value_name="값")
        bar = (
            alt.Chart(melted)
            .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
            .encode(
                x=alt.X("상품명:N", sort="-y", title=None,
                        axis=alt.Axis(labelAngle=-28, labelLimit=140)),
                y=alt.Y("값:Q", title="증가율 (%)"),
                color=alt.Color("지표:N",
                                scale=alt.Scale(range=["#5033EA","#0891b2"]),
                                legend=alt.Legend(title="지표")),
                xOffset="지표:N",
                tooltip=["상품명","지표","값"],
            ).properties(height=360)
        )
        st.altair_chart(bar, use_container_width=True)

    with right:
        section_header("운영 해석 가이드")
        insight_row("🍵","피스타치오 계열",
                    "풍미 탐색형 유사상품 검색이 동반됩니다. SKU 다양화보다 대표 상품 집중 큐레이션이 유효합니다.")
        insight_row("🥛","고단백 요거트",
                    "해시태그·검색·구매전환이 함께 오르는 실구매 확장형 신호입니다. 재고 확보 및 단독 진열을 강화하세요.")
        insight_row("🍝","트러플·페스토 소스",
                    "레시피 연관 검색이 강해 파스타면·치즈와의 크로스 진열 효과가 큽니다.")
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            badge_html("유사상품 탐색형","brand")
            + badge_html("실구매 확장형","green")
            + badge_html("레시피 연관형","amber"),
            unsafe_allow_html=True,
        )

    divider()
    section_header("상품별 상세 테이블")
    st.dataframe(
        df.sort_values(["검색증가율","SNS증가율"], ascending=False).reset_index(drop=True),
        use_container_width=True, hide_index=True,
    )


# ── 탭 2: 트렌드 상세 분석 ──────────────────────────────────

def tab_trend_detail(cat_df: pd.DataFrame, hot_df: pd.DataFrame, filters: dict) -> None:
    filtered = cat_df[cat_df["카테고리"].isin(filters["categories"])]
    picked = st.selectbox("상세 분석 카테고리 선택",
                          filtered["카테고리"].tolist(), index=0)
    row = cat_df[cat_df["카테고리"] == picked].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("트렌드 점수",  str(row["트렌드점수"]),
                      f"+{row['검색증가율']}% 검색", "up")
    with c2: kpi_card("SNS 화제성",   str(row["SNS화제성"]),
                      "콘텐츠 언급 상위", "up")
    with c3: kpi_card("매출지수",     str(row["매출지수"]),
                      f"전년대비 +{row['전년대비매출']}%", "up")
    with c4:
        sig = "실구매형" if (row["트렌드점수"] >= 80 and row["매출지수"] >= 80) else "탐색형"
        kpi_card("트렌드 신호", sig,
                 "검색+매출 동반 여부", "up" if sig == "실구매형" else "neutral")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    left, right = st.columns(2)

    with left:
        section_header(f"{picked} — 인사이트")
        insight_row("📈","왜 오르는가",
                    f"{picked} 카테고리는 SNS 콘텐츠 확산, 레시피 트렌드, "
                    f"프리미엄·건강 키워드가 교차하며 검색과 관심이 동시에 증가 중입니다.")
        insight_row("🛒","실제 고객 반응인가",
                    f"검색 증가(+{row['검색증가율']}%)와 매출지수({row['매출지수']})가 "
                    f"함께 오르면 실구매 신호입니다. 현재 {picked}는 두 지표 모두 양호합니다.")
        insight_row("🔄","유사상품 검색 가능성",
                    "대표 상품의 풍미·원재료가 화제가 되면 유사 SKU 탐색이 동반됩니다. "
                    "유사 라인업을 미리 준비하는 것이 유리합니다.")

    with right:
        section_header(f"{picked} 연관 상품 시그널")
        related = hot_df[hot_df["카테고리"] == picked]
        if related.empty:
            related = hot_df.sample(3, random_state=7)
        st.dataframe(
            related[["상품명","검색증가율","SNS증가율","구매전환","트렌드유형"]].reset_index(drop=True),
            use_container_width=True, hide_index=True,
        )

    divider()
    section_header("실무 적용 포인트")
    cols = st.columns(4)
    points = [
        ("🛍 바이어",  "입점·확대 판단 시 실매출 연동 여부를 먼저 확인하세요."),
        ("💼 영업",    "브랜드사 미팅에서 검색·SNS 증가율을 수치 근거로 활용하세요."),
        ("🗂 MD",      "레시피 연결 카테고리는 파스타면·소스·치즈 교차 제안이 유효합니다."),
        ("🎪 행사",    "탐색형→시식 프로모션, 실구매형→물량·광고 집중으로 구분하세요."),
    ]
    for col, (title, text) in zip(cols, points):
        with col:
            st.markdown(
                f'<div class="card">'
                f'<div style="font-weight:800;font-size:13px;margin-bottom:8px;">{title}</div>'
                f'<div style="font-size:12px;color:var(--text-3);line-height:1.7;">{text}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


# ── 탭 3: 브랜드·팝업 기획 ─────────────────────────────────

def tab_brand_popup(brand_df: pd.DataFrame) -> None:
    left, right = st.columns([1.3, 1])

    with left:
        section_header("브랜드별 팝업 적합도",
                       "트렌드 키워드와 카테고리 연계 기준")
        bar = (
            alt.Chart(brand_df)
            .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
            .encode(
                x=alt.X("브랜드:N", sort="-y", title=None),
                y=alt.Y("팝업적합도:Q", scale=alt.Scale(domain=[0, 100])),
                color=alt.Color("브랜드:N",
                                scale=alt.Scale(range=BRAND_PALETTE),
                                legend=None),
                tooltip=["브랜드","카테고리","키워드","팝업적합도","추천액션"],
            ).properties(height=360)
        )
        text_layer = (
            alt.Chart(brand_df)
            .mark_text(dy=-8, fontSize=12, fontWeight="bold", color="#111827")
            .encode(
                x=alt.X("브랜드:N", sort="-y"),
                y=alt.Y("팝업적합도:Q"),
                text=alt.Text("팝업적합도:Q"),
            )
        )
        st.altair_chart(bar + text_layer, use_container_width=True)

    with right:
        section_header("행사 기획 제안 4선")
        ideas = [
            ("🍽","홈파인 다이닝 위크",   "파스타소스·치즈·올리브오일 연계 3종 기획전"),
            ("🥗","헬시 브런치 존",       "고단백 요거트·저당 음료·그래놀라·스낵 묶음"),
            ("🎁","명절 프리미엄 선물전", "발사믹·오일·치즈·캐비아 선물 세트 큐레이션"),
            ("🔬","화제 시식 비교존",     "피스타치오·트러플 계열 유사상품 직접 비교 체험"),
        ]
        for icon, title, desc in ideas:
            insight_row(icon, title, desc)

    divider()
    section_header("브랜드 후보 리스트 전체")
    st.dataframe(
        brand_df.sort_values("팝업적합도", ascending=False).reset_index(drop=True),
        use_container_width=True, hide_index=True,
    )


# ── 탭 4: 상품군별 매출 ─────────────────────────────────────

def tab_sales(sales_df: pd.DataFrame, cat_df: pd.DataFrame, filters: dict) -> None:
    sel = filters["categories"]
    filt = sales_df[sales_df["카테고리"].isin(sel)]

    pick4 = st.multiselect(
        "그래프에 표시할 카테고리",
        options=sel,
        default=sel[:min(4, len(sel))],
        key="sales_pick",
    )
    if not pick4:
        pick4 = sel[:min(4, len(sel))]

    chart_df = filt[filt["카테고리"].isin(pick4)]
    area = (
        alt.Chart(chart_df)
        .mark_area(opacity=0.08)
        .encode(
            x=alt.X("주차:T", title=None),
            y=alt.Y("매출지수:Q"),
            color=alt.Color("카테고리:N",
                            scale=alt.Scale(range=BRAND_PALETTE), legend=None),
        )
    )
    line = (
        alt.Chart(chart_df)
        .mark_line(point=alt.OverlayMarkDef(size=60), strokeWidth=2.5)
        .encode(
            x=alt.X("주차:T", title=None),
            y=alt.Y("매출지수:Q", title="매출지수"),
            color=alt.Color("카테고리:N",
                            scale=alt.Scale(range=BRAND_PALETTE),
                            legend=alt.Legend(title="카테고리")),
            tooltip=["주차:T","카테고리","매출지수"],
        ).properties(height=380)
    )
    st.altair_chart(area + line, use_container_width=True)

    divider()
    left, right = st.columns(2)

    with left:
        section_header("카테고리 평균 / 최고 매출지수")
        summary = (
            filt.groupby("카테고리")["매출지수"]
            .agg(평균=lambda x: round(x.mean(), 1),
                 최고=lambda x: int(x.max()))
            .reset_index()
            .sort_values("평균", ascending=False)
        )
        st.dataframe(summary, use_container_width=True, hide_index=True)

    with right:
        section_header("바이어 체크포인트")
        insight_row("📌","주간 모니터링",
                    "HMR · 소스 · 음료는 신제품 반응 속도가 빠릅니다. 주간 단위 체크를 권장합니다.")
        insight_row("📅","시즌 모니터링",
                    "오일·발사믹 · 치즈는 선물 수요와 행사 시즌 영향이 큽니다.")
        insight_row("🤝","레시피 연계",
                    "파스타면 · 향신료는 단독보다 레시피 연계 매출 비중이 높습니다.")


# ── 탭 5: 인스타 해시태그 인텔리전스 ─────────────────────────

def tab_hashtag(ht_df: pd.DataFrame, filters: dict) -> None:
    thresh = filters["threshold"]
    st.info(
        "현재 버전은 샘플 데이터 기반입니다. "
        "실제 운영 시에는 인스타그램 API 또는 대체 수집 데이터를 연결하세요.",
        icon="ℹ️",
    )
    filt = ht_df[ht_df["7일증가율"] >= thresh]
    if filt.empty:
        filt = ht_df

    left, right = st.columns([1.3, 1])

    with left:
        section_header("7일 해시태그 급상승 랭킹",
                       f"증가율 {thresh}% 이상 필터")
        h_bar = (
            alt.Chart(filt)
            .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
            .encode(
                x=alt.X("해시태그:N", sort="-y", title=None,
                        axis=alt.Axis(labelAngle=-20, labelLimit=160)),
                y=alt.Y("7일증가율:Q", title="7일 증가율 (%)"),
                color=alt.Color("7일증가율:Q",
                                scale=alt.Scale(scheme="purples"), legend=None),
                tooltip=["해시태그","7일증가율","조회지수","카테고리","해석"],
            ).properties(height=340)
        )
        st.altair_chart(h_bar, use_container_width=True)

    with right:
        section_header("해시태그 인텔리전스 활용법")
        insight_row("📊","트렌드 진단",
                    "증가 폭이 큰 태그는 관심이 높은 원재료·풍미를 의미합니다.")
        insight_row("🛒","구매 신호 구분",
                    "실구매형: 태그+검색+구매전환 동반 상승 / 탐색형: 태그만 상승.")
        insight_row("📎","브랜드 연결",
                    "SNS 화제 키워드와 실제 취급 브랜드를 매핑해 영업·입점 자료로 활용하세요.")
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            "".join(badge_html(t, "brand") for t in filt["해시태그"].tolist()),
            unsafe_allow_html=True,
        )

    divider()
    section_header("해시태그 상세 데이터")
    st.dataframe(
        filt.sort_values("7일증가율", ascending=False).reset_index(drop=True),
        use_container_width=True, hide_index=True,
    )


# ── 탭 6: 명절 매출 속보 ─────────────────────────────────────

def tab_holiday(holiday_df: pd.DataFrame, cat_df: pd.DataFrame) -> None:
    all_cats = cat_df["카테고리"].tolist()
    col1, col2 = st.columns([1.2, 1])

    with col1:
        section_header("속보 작성 템플릿",
                       "담당자 공유용 명절 매출 속보를 빠르게 기록하세요.")
        title_i  = st.text_input("제목", value="설 선물세트 2주차 매출 속보")
        period_i = st.text_input("대상 기간", value="2026-01-12 ~ 2026-01-18")
        cat_i    = st.multiselect("핵심 카테고리", options=all_cats,
                                  default=["오일·발사믹","치즈","HMR"])
        memo_i   = st.text_area(
            "핵심 메모",
            value="오일·발사믹과 치즈 선물세트 반응이 좋고, HMR은 연휴 직전 수요가 급증했습니다.",
            height=140,
        )
        if st.button("💾  속보 저장", use_container_width=True, type="primary"):
            st.success(f"✅ 속보 저장 완료: {title_i}")

    with col2:
        section_header("속보 작성 팁")
        insight_row("📝","제목 규칙",
                    "시즌 + 주차 + 핵심 카테고리 형식으로 표기하면 검색이 쉬워집니다.")
        insight_row("📤","공유 구조",
                    "URL 기반 공유 → 담당자가 별도 파일 없이 바로 확인 가능합니다.")
        insight_row("📋","필수 기재 항목",
                    "전주 대비 증감 / 베스트셀러 / 이슈 상품 / 행사 반응을 함께 기록하세요.")
        insight_row("🔮","향후 확장",
                    "엑셀 업로드 후 자동 요약 기능으로 확장 예정입니다.")

    divider()
    section_header("등록된 명절 속보 목록")
    st.dataframe(holiday_df, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div class="upload-zone">'
        '📂 엑셀/CSV 파일을 드래그하거나 클릭해 업로드하면 자동으로 속보 형태로 변환됩니다.<br>'
        '<small style="color:#9ca3af;">'
        '(실제 운영 시 st.file_uploader + pandas 파이프라인으로 교체)</small>'
        '</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────
# 6. main
# ─────────────────────────────────────────────────────────────

def main() -> None:
    cat_df     = load_category_data()
    hot_df     = load_hot_items()
    brand_df   = load_brand_popup()
    sales_df   = load_sales_weekly()
    ht_df      = load_hashtag_data()
    holiday_df = load_holiday_news()

    filters = render_sidebar(cat_df)

    # 히어로 배너
    st.markdown(
        '<div class="hero">'
        '<div class="hero-eyebrow">🛒 Food Buyer Intelligence</div>'
        '<div class="hero-title">가공식품 트렌드 &amp; 매출 인텔리전스 허브</div>'
        '<div class="hero-sub">'
        '백화점 바이어와 영업담당자가 한 화면에서 트렌드, 검색 급상승, SNS 화제성, '
        '브랜드 팝업 기회, 카테고리별 매출 흐름, 명절 매출 속보까지 확인하는 운영용 인텔리전스 플랫폼입니다.'
        '</div></div>',
        unsafe_allow_html=True,
    )

    tabs = st.tabs([
        "📊 전체 요약",
        "🔥 인기 상품 급상승",
        "🔍 트렌드 상세 분석",
        "🎪 브랜드·팝업 기획",
        "📈 상품군별 매출",
        "# 인스타 해시태그",
        "🎁 명절 매출 속보",
    ])

    with tabs[0]: tab_summary(cat_df, hot_df, filters)
    with tabs[1]: tab_hot_items(hot_df, filters)
    with tabs[2]: tab_trend_detail(cat_df, hot_df, filters)
    with tabs[3]: tab_brand_popup(brand_df)
    with tabs[4]: tab_sales(sales_df, cat_df, filters)
    with tabs[5]: tab_hashtag(ht_df, filters)
    with tabs[6]: tab_holiday(holiday_df, cat_df)

    st.markdown(
        f'<div class="footer">'
        f'목적: {filters["goal"]} &nbsp;·&nbsp; '
        f'기간: {filters["period"]} &nbsp;·&nbsp; '
        f'업데이트: {TODAY.strftime("%Y-%m-%d %H:%M")}'
        f'</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
