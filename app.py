import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# ──────────────────────────────────────────
# 페이지 설정
# ──────────────────────────────────────────
st.set_page_config(
    page_title="가공식품 트렌드 플랫폼",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────
# 스타일
# ──────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a2e;
    }
    .category-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1rem;
        border-left: 4px solid #4361ee;
        margin-bottom: 0.5rem;
    }
    .kpi-label { font-size: 0.8rem; color: #666; margin-bottom: 4px; }
    .kpi-value { font-size: 1.6rem; font-weight: 700; color: #1a1a2e; }
    .kpi-delta { font-size: 0.85rem; }
    .badge-hot {
        background: #ff4757; color: white;
        border-radius: 20px; padding: 2px 10px;
        font-size: 0.75rem; font-weight: 600;
    }
    .badge-up {
        background: #2ed573; color: white;
        border-radius: 20px; padding: 2px 10px;
        font-size: 0.75rem; font-weight: 600;
    }
    .badge-stable {
        background: #a4b0be; color: white;
        border-radius: 20px; padding: 2px 10px;
        font-size: 0.75rem; font-weight: 600;
    }
    .insight-box {
        background: #eef2ff;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        border-left: 4px solid #4361ee;
        margin: 0.5rem 0;
    }
    .share-box {
        background: #f1f3f5;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        font-family: monospace;
        font-size: 0.9rem;
        word-break: break-all;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────
# 더미 데이터
# ──────────────────────────────────────────
CATEGORIES = {
    "전체": "all",
    "오일 / 발사믹": "oil",
    "과자 / 스낵": "snack",
    "파스타면": "pasta",
    "소스": "sauce",
    "향신료": "spice",
    "HMR": "hmr",
    "우유 / 유제품": "dairy",
    "음료": "beverage",
    "치즈": "cheese",
    "샤퀴테리": "charcuterie",
    "캐비아 (프리미엄)": "caviar",
}

CATEGORY_ICONS = {
    "전체": "🏠",
    "오일 / 발사믹": "🫒",
    "과자 / 스낵": "🍿",
    "파스타면": "🍝",
    "소스": "🥫",
    "향신료": "🌶️",
    "HMR": "🍱",
    "우유 / 유제품": "🥛",
    "음료": "🧃",
    "치즈": "🧀",
    "샤퀴테리": "🥩",
    "캐비아 (프리미엄)": "🫧",
}

def generate_trend_data(category_key: str, weeks: int = 12):
    """최근 N주 트렌드 시계열 데이터 생성"""
    np.random.seed(hash(category_key) % (2**31))
    base = random.randint(60, 90)
    noise = np.random.randn(weeks) * 5
    trend = np.linspace(0, random.randint(-10, 20), weeks)
    scores = np.clip(base + trend + noise, 20, 100).tolist()
    dates = [datetime.today() - timedelta(weeks=weeks - i) for i in range(weeks)]
    return pd.DataFrame({"날짜": dates, "트렌드 점수": scores})


def category_kpis(key: str):
    """카테고리별 KPI 반환"""
    np.random.seed(hash(key) % (2**31))
    score = int(np.random.randint(55, 96))
    growth = round(np.random.uniform(-5, 30), 1)
    avg_price = int(np.random.randint(8000, 85000))
    return score, growth, avg_price


def top_products(key: str, n: int = 5):
    """카테고리별 상위 상품 반환"""
    catalog = {
        "oil":         ["에트나 엑스트라버진 올리브유", "모데나 발사믹 10년산", "아보카도 오일 500ml", "화이트 트러플 오일", "포도씨 오일"],
        "snack":       ["노르딕 크래커", "흑임자 쌀과자", "쑥 마들렌", "오트밀 그래놀라바", "리코타 치즈칩"],
        "pasta":       ["유기농 세몰리나 스파게티", "블랙 스퀴드 링귀네", "글루텐프리 펜네", "통밀 리가토니", "트러플 탈리아텔레"],
        "sauce":       ["산마르차노 토마토 소스", "페스토 알라 제노베제", "아란치니 아라비아타", "화이트 크림 알프레도", "아시안 후무스 소스"],
        "spice":       ["스모크 파프리카", "시칠리안 오레가노", "말돈 씨솔트", "사프란 실크", "유기농 바닐라빈"],
        "hmr":         ["프리미엄 트러플 리조또", "양고기 카레", "랍스터 비스크 수프", "버섯 크림 리조또", "쇼유 라멘"],
        "dairy":       ["그래스페드 버터", "유기농 플레인 요거트", "크렘프레쉬 35%", "무항생제 우유 1L", "그릭 요거트 제로"],
        "beverage":    ["콤부차 진저레몬", "유기농 콜드브루 질소", "히비스커스 허브티", "스파클링 라임에이드", "비트 클렌즈 주스"],
        "cheese":      ["파르미지아노 레지아노 24개월", "브리 드 모", "그뤼에르 알파인", "부라타 프레스카", "훈제 고다"],
        "charcuterie": ["이베리코 하몽 벨로타", "밀라노 살라미", "코파 디 테스타", "프로슈토 디 파르마", "모르타델라"],
        "caviar":      ["벨루가 캐비아 30g", "세브루가 캐비아 50g", "오세트라 골드 캐비아", "연어알 (이쿠라)", "송어알 프리미엄"],
        "all":         ["트러플 리조또", "이베리코 하몽", "부라타 프레스카", "유기농 올리브유", "파르미지아노 레지아노"],
    }
    prods = catalog.get(key, catalog["all"])
    np.random.seed(hash(key + "p") % (2**31))
    scores = sorted(np.random.randint(60, 100, len(prods)).tolist(), reverse=True)
    growth = [round(np.random.uniform(-3, 25), 1) for _ in prods]
    return pd.DataFrame({"상품명": prods, "트렌드 점수": scores, "성장률(%)": growth})


def category_insights(key: str):
    catalog = {
        "oil":         ["올리브유 수요 전년 대비 +18% 증가", "트러플 오일 프리미엄 라인 강세", "아보카도 오일 건강 카테고리 유입 증가"],
        "snack":       ["글루텐프리 스낵 수요 급증 (+32%)", "홈파티 트렌드로 크래커류 성장", "오트밀·견과류 기반 스낵 주목"],
        "pasta":       ["글루텐프리 파스타 2030세대 인기", "블랙 스퀴드·컬러 파스타 SNS 확산", "유기농 통밀 라인 프리미엄 고객 흡수"],
        "sauce":       ["토마토 소스 시장 정체 → 페스토류 성장", "아시안 퓨전 소스 신규 등록 증가", "홈쿡 트렌드로 고급 소스 객단가 상승"],
        "spice":       ["스모크 향신료 BBQ 트렌드와 동반 성장", "유기농 바닐라빈 베이킹 수요 증가", "말돈 솔트 프리미엄 선물 세트 강세"],
        "hmr":         ["트러플·랍스터 프리미엄 HMR 급성장", "1인 가구 증가로 소용량 HMR 수요↑", "냉동 리조또 반복 구매율 업계 최고"],
        "dairy":       ["그래스페드 버터 건강 인식 확산으로 성장", "그릭 요거트 저당 트렌드 주도", "크렘프레쉬 제과·홈쿡 시장 침투 중"],
        "beverage":    ["콤부차 장 건강 트렌드 최대 수혜", "콜드브루 질소 충전 프리미엄 수요↑", "저당·기능성 음료 20대 구매 집중"],
        "cheese":      ["파르미지아노 장기숙성 프리미엄 선호", "부라타 SNS 바이럴 → 판매 +45%", "치즈 보드 문화 확산으로 다품종 소량 구매"],
        "charcuterie": ["이베리코 하몽 프리미엄 선물 시장 1위", "살라미 홈파티·치즈 보드 세트 인기", "국내산 숙성 샤퀴테리 브랜드 성장 중"],
        "caviar":      ["캐비아 VIP 고객 재구매율 68%", "소용량 캐비아 MZ 탐색 구매 증가", "연어알·송어알 가성비 캐비아 진입장벽 완화"],
        "all":         ["전체 가공식품 프리미엄화 가속", "건강·유기농 키워드 전 카테고리 공통 상승세", "SNS 바이럴 → 즉시 구매 전환 패턴 증가"],
    }
    return catalog.get(key, catalog["all"])


# ──────────────────────────────────────────
# 사이드바
# ──────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 트렌드 플랫폼")
    st.markdown("백화점 식품 바이어 전용")
    st.divider()

    selected_label = st.radio(
        "카테고리 선택",
        list(CATEGORIES.keys()),
        format_func=lambda x: f"{CATEGORY_ICONS[x]} {x}",
    )
    selected_key = CATEGORIES[selected_label]

    st.divider()
    st.markdown("**🔗 링크 공유**")
    base_url = "https://food-trend.internal"
    share_url = f"{base_url}/category/{selected_key}"
    st.markdown(f'<div class="share-box">{share_url}</div>', unsafe_allow_html=True)
    st.code(share_url, language=None)
    st.caption("위 URL을 담당자에게 공유하세요.")

    st.divider()
    updated = datetime.today().strftime("%Y-%m-%d %H:%M")
    st.caption(f"마지막 업데이트: {updated}")

# ──────────────────────────────────────────
# 메인 화면
# ──────────────────────────────────────────
icon = CATEGORY_ICONS[selected_label]
st.markdown(f'<p class="main-title">{icon} {selected_label} 트렌드 리포트</p>', unsafe_allow_html=True)
st.caption(f"경로: /category/{selected_key}  ·  기준일: {datetime.today().strftime('%Y년 %m월 %d일')}")
st.divider()

# ── KPI 카드 ──────────────────────────────
score, growth, avg_price = category_kpis(selected_key)

badge_score = "🔴 HOT" if score >= 80 else ("🟢 상승" if score >= 65 else "⚪ 보통")
badge_growth = "▲ 성장중" if growth > 0 else "▼ 하락중"

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("트렌드 점수", f"{score} / 100", f"{badge_score}")
with col2:
    st.metric("전월 대비 성장률", f"{growth:+.1f}%", badge_growth)
with col3:
    st.metric("평균 객단가", f"₩{avg_price:,}")
with col4:
    top_n = top_products(selected_key)
    best = top_n.iloc[0]["상품명"]
    st.metric("이번 주 1위 상품", best[:10] + "…" if len(best) > 10 else best)

st.divider()

# ── 차트 + 상품 랭킹 ──────────────────────
col_chart, col_rank = st.columns([2, 1])

with col_chart:
    st.subheader("📈 최근 12주 트렌드 점수")
    df_trend = generate_trend_data(selected_key)
    fig = px.area(
        df_trend, x="날짜", y="트렌드 점수",
        color_discrete_sequence=["#4361ee"],
        template="plotly_white",
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=20, b=0),
        yaxis=dict(range=[0, 105]),
        hovermode="x unified",
    )
    fig.add_hline(y=80, line_dash="dot", line_color="#ff4757", annotation_text="HOT 기준선")
    st.plotly_chart(fig, use_container_width=True)

with col_rank:
    st.subheader("🏆 상위 상품 랭킹")
    df_top = top_products(selected_key)
    for i, row in df_top.iterrows():
        medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i]
        trend_icon = "▲" if row["성장률(%)"] > 0 else "▼"
        color = "#2ed573" if row["성장률(%)"] > 0 else "#ff4757"
        st.markdown(
            f"""<div class="category-card">
                {medal} <b>{row['상품명']}</b><br>
                점수 <b>{row['트렌드 점수']}</b>
                &nbsp;|&nbsp;
                <span style="color:{color}">{trend_icon} {row['성장률(%)']:+.1f}%</span>
            </div>""",
            unsafe_allow_html=True,
        )

st.divider()

# ── 카테고리별 인사이트 ─────────────────────
st.subheader("💡 핵심 인사이트")
insights = category_insights(selected_key)
cols = st.columns(len(insights))
for col, insight in zip(cols, insights):
    with col:
        st.markdown(f'<div class="insight-box">📌 {insight}</div>', unsafe_allow_html=True)

st.divider()

# ── 전체 카테고리 비교 (전체 뷰에서만) ────────
if selected_key == "all":
    st.subheader("📊 카테고리별 트렌드 점수 비교")
    cat_keys = [v for k, v in CATEGORIES.items() if v != "all"]
    cat_labels = [k for k in CATEGORIES.keys() if k != "전체"]
    scores_all = [category_kpis(k)[0] for k in cat_keys]
    growths_all = [category_kpis(k)[1] for k in cat_keys]

    df_compare = pd.DataFrame({
        "카테고리": cat_labels,
        "트렌드 점수": scores_all,
        "성장률(%)": growths_all,
    }).sort_values("트렌드 점수", ascending=False)

    fig2 = px.bar(
        df_compare, x="카테고리", y="트렌드 점수",
        color="성장률(%)",
        color_continuous_scale=["#ff4757", "#ffa502", "#2ed573"],
        text="트렌드 점수",
        template="plotly_white",
    )
    fig2.update_layout(margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

# ── 공유 버튼 섹션 ────────────────────────
st.subheader("🔗 담당자 공유")
st.markdown("카테고리별 URL을 복사해 담당자에게 바로 전달하세요.")

share_cols = st.columns(4)
sub_cats = [(k, v) for k, v in CATEGORIES.items() if v != "all"]
for idx, (label, key) in enumerate(sub_cats):
    with share_cols[idx % 4]:
        url = f"https://food-trend.internal/category/{key}"
        st.markdown(f"**{CATEGORY_ICONS[label]} {label}**")
        st.code(url, language=None)
