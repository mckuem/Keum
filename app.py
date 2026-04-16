import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta

st.set_page_config(
    page_title="식품 트렌드 인텔리전스 허브",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    html, body, [class*="css"], [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    }
    .stApp { background: #f8f9fb; color: #1f2937; }
    .block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1440px; }
    .hero {
        background: linear-gradient(135deg, #ffffff 0%, #f7f1ff 55%, #f6fbff 100%);
        border: 1px solid #ebe5f7; border-radius: 28px; padding: 28px 30px; margin-bottom: 18px;
        box-shadow: 0 10px 30px rgba(26, 26, 26, 0.04);
    }
    .hero-title { font-size: 32px; font-weight: 800; letter-spacing: -0.02em; color: #111827; margin-bottom: 8px; }
    .hero-sub { color: #5b6472; font-size: 15px; line-height: 1.7; }
    .section-title { font-size: 22px; font-weight: 800; letter-spacing: -0.02em; color: #111827; margin: 8px 0 14px 0; }
    .section-sub { color: #667085; font-size: 14px; margin-top: -6px; margin-bottom: 14px; }
    .metric-card {
        background: white; border-radius: 22px; padding: 18px 18px 16px 18px;
        border: 1px solid #ececf2; box-shadow: 0 8px 24px rgba(17, 24, 39, 0.04); min-height: 120px;
    }
    .metric-label { color: #6b7280; font-size: 13px; margin-bottom: 10px; }
    .metric-value { color: #111827; font-size: 30px; font-weight: 800; line-height: 1.1; }
    .metric-delta-up { color: #0f9f6e; font-size: 13px; font-weight: 700; margin-top: 8px; }
    .metric-delta-down { color: #e5484d; font-size: 13px; font-weight: 700; margin-top: 8px; }
    .content-card {
        background: white; border-radius: 24px; padding: 20px 22px; border: 1px solid #ececf2;
        box-shadow: 0 8px 24px rgba(17, 24, 39, 0.04); margin-bottom: 16px;
    }
    .tag {
        display: inline-block; background: #f5f3ff; color: #6d28d9; border: 1px solid #e9ddff;
        border-radius: 999px; padding: 6px 10px; margin: 0 8px 8px 0; font-size: 12px; font-weight: 700;
    }
    .soft-tag {
        display: inline-block; background: #f8fafc; color: #475467; border: 1px solid #eaecf0;
        border-radius: 999px; padding: 6px 10px; margin: 0 8px 8px 0; font-size: 12px; font-weight: 600;
    }
    .insight-box {
        background: linear-gradient(180deg, #fcfcfd 0%, #f9fafb 100%);
        border: 1px solid #ececf2; border-radius: 18px; padding: 16px 18px; margin-bottom: 10px;
    }
    .insight-title { font-weight: 800; color: #111827; font-size: 15px; margin-bottom: 6px; }
    .insight-body { color: #5d6674; font-size: 14px; line-height: 1.7; }
    .kicker { color: #7c3aed; font-size: 12px; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; }
    div[data-testid="stTabs"] button { font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True,
)

today = datetime.today()
dates = pd.date_range(today - timedelta(days=11), periods=12, freq="W")

category_data = pd.DataFrame({
    "카테고리": ["오일·발사믹", "과자·스낵", "파스타면", "소스", "향신료", "HMR", "우유·유제품", "음료", "치즈", "샤퀴테리", "캐비아"],
    "트렌드점수": [78, 91, 76, 94, 72, 96, 83, 89, 86, 68, 62],
    "매출지수": [82, 88, 73, 91, 69, 95, 84, 87, 80, 65, 59],
    "SNS화제성": [71, 93, 67, 90, 74, 92, 79, 95, 85, 63, 70],
    "검색증가율(%)": [12, 27, 9, 31, 11, 29, 14, 25, 16, 6, 8],
    "전년대비매출(%)": [8, 12, 5, 14, 4, 17, 9, 11, 10, 3, 6],
})

hot_items = pd.DataFrame({
    "상품명": ["두쫀쿠 피스타치오 크림쿠키", "트러플 머쉬룸 파스타소스", "저당 고단백 요거트", "바질 페스토", "프리미엄 올리브오일", "제로슈가 탄산음료", "크림치즈 딥", "우유버터 비스킷"],
    "카테고리": ["과자·스낵", "소스", "우유·유제품", "소스", "오일·발사믹", "음료", "치즈", "과자·스낵"],
    "SNS증가율(%)": [38, 27, 24, 21, 18, 22, 19, 17],
    "검색증가율(%)": [42, 31, 26, 19, 15, 28, 16, 14],
    "구매전환추정": [7.6, 6.9, 8.4, 5.7, 6.1, 7.2, 5.9, 4.8],
    "트렌드유형": ["유사상품 탐색형", "실구매 확장형", "실구매 확장형", "레시피 연관형", "프리미엄 원재료형", "기능성 대체형", "홈파티 연관형", "캐릭터/선물형"]
})

brand_popup = pd.DataFrame({
    "브랜드": ["브레디크", "라구델리", "그릭랩", "오로바일렌", "치즈하우스", "테이스티테이블"],
    "연관 카테고리": ["과자·스낵", "소스·파스타", "유제품", "오일·발사믹", "치즈", "HMR"],
    "트렌드 키워드": ["피스타치오, 쿠키, 선물", "트러플, 파스타, 홈파인다이닝", "고단백, 저당, 아침식사", "싱글오리진, 엑스트라버진", "와인안주, 플래터", "셰프컬래버, 냉장간편식"],
    "팝업 적합도": [92, 89, 90, 84, 87, 94],
    "추천 액션": ["디저트 큐레이션 존", "주말 미식 테마전", "헬시 브런치 존", "명절 선물 세트", "와인 페어링 존", "셰프 협업 팝업"]
})

sales_weekly = []
for cat, base in zip(category_data["카테고리"], [70, 82, 60, 85, 55, 92, 77, 80, 73, 48, 39]):
    rng = np.random.default_rng(abs(hash(cat)) % (2**32))
    values = np.maximum(base + np.cumsum(rng.integers(-4, 7, size=len(dates))), 20)
    for d, v in zip(dates, values):
        sales_weekly.append({"주차": d, "카테고리": cat, "매출지수": int(v)})

sales_df = pd.DataFrame(sales_weekly)

hashtag_df = pd.DataFrame({
    "해시태그": ["#피스타치오", "#트러플파스타", "#고단백요거트", "#제로슈가", "#올리브오일", "#홈파티치즈", "#냉장간편식", "#발사믹"],
    "7일증가율(%)": [64, 48, 37, 35, 29, 25, 31, 18],
    "추정 조회지수": [96, 84, 79, 82, 68, 63, 74, 55],
    "연관 카테고리": ["과자·스낵", "소스·파스타", "우유·유제품", "음료", "오일·발사믹", "치즈", "HMR", "오일·발사믹"],
    "해석": [
        "직접 구매보다 유사 풍미 탐색이 함께 증가",
        "레시피/집밥 콘텐츠 유입과 연결",
        "실구매·재구매형 검색 신호가 강함",
        "대체재 비교 검색이 동반됨",
        "프리미엄 선물 수요와 연계 가능",
        "와인/홈파티 맥락 검색과 연결",
        "간편식 신제품 탐색 수요 반영",
        "샐러드·드레싱 연관 검색 동반"
    ]
})

holiday_news = pd.DataFrame({
    "업로드일": ["2026-01-10", "2026-01-18", "2026-01-24", "2026-09-16"],
    "제목": ["설 선물세트 초반 매출 속보", "설 직전 HMR 집중 판매 현황", "설 연휴 직후 카테고리 회고", "추석 선물세트 주간 속보"],
    "상태": ["게시", "게시", "초안", "예정"],
    "주요 카테고리": ["오일·발사믹, 치즈", "HMR, 소스", "전 카테고리", "유제품, 오일·발사믹"]
})

with st.sidebar:
    st.markdown("## 식품 트렌드 허브")
    st.caption("마켓컬리 톤의 깔끔한 바이어용 운영 대시보드")
    selected_categories = st.multiselect(
        "보고 싶은 상품군",
        options=category_data["카테고리"].tolist(),
        default=category_data["카테고리"].tolist()[:6],
    )
    if not selected_categories:
        selected_categories = category_data["카테고리"].tolist()
    period = st.selectbox("조회 기간", ["최근 7일", "최근 30일", "최근 90일", "최근 12주"], index=1)
    buyer_goal = st.radio("사용 목적", ["트렌드 확인", "매출 추이 확인", "팝업 기획", "명절 속보 업로드 준비"], index=0)

filtered_category = category_data[category_data["카테고리"].isin(selected_categories)].copy()
filtered_sales = sales_df[sales_df["카테고리"].isin(selected_categories)].copy()

def metric_card(label, value, delta, positive=True):
    klass = "metric-delta-up" if positive else "metric-delta-down"
    st.markdown(
        f'''
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="{klass}">{delta}</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

def section_header(title, subtitle=""):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="section-sub">{subtitle}</div>', unsafe_allow_html=True)

st.markdown(
    '''
    <div class="hero">
        <div class="kicker">Food Buyer Intelligence</div>
        <div class="hero-title">가공식품 트렌드 & 매출 인텔리전스 허브</div>
        <div class="hero-sub">
            백화점 바이어와 영업담당자가 한 화면에서 트렌드, 검색 증가, SNS 화제성, 브랜드 팝업 기회, 카테고리별 매출 흐름,
            명절 매출 속보까지 빠르게 확인할 수 있도록 설계한 운영용 웹앱입니다.
        </div>
    </div>
    ''',
    unsafe_allow_html=True,
)

tabs = st.tabs([
    "전체 요약",
    "인기 상품 급상승",
    "트렌드 상세 분석",
    "브랜드·팝업 기획",
    "상품군별 매출",
    "인스타 해시태그 인텔리전스",
    "명절 매출 속보"
])

with tabs[0]:
    section_header("전체 요약", "그래프, 숫자, 베스트셀러, 우선 대응 카테고리를 한눈에 볼 수 있는 첫 화면")
    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("이번 주 전체 트렌드 지수", "91", "+11.4% vs 지난주", True)
    with c2: metric_card("SNS 화제성 상위 카테고리", "음료", "+25.0% 검색 증가", True)
    with c3: metric_card("매출 탄력 최고", "HMR", "+17.0% 전년대비", True)
    with c4: metric_card("주의 필요 카테고리", "샤퀴테리", "-2.1% 재구매율", False)

    left, right = st.columns([1.35, 1])
    with left:
        section_header("카테고리 트렌드 맵", "트렌드점수와 매출지수를 같이 보며 우선순위를 판단")
        bubble = alt.Chart(filtered_category).mark_circle(opacity=0.85).encode(
            x=alt.X("트렌드점수:Q", scale=alt.Scale(domain=[50, 100])),
            y=alt.Y("매출지수:Q", scale=alt.Scale(domain=[40, 100])),
            size=alt.Size("SNS화제성:Q", scale=alt.Scale(range=[200, 1400])),
            color=alt.Color("카테고리:N", legend=None),
            tooltip=["카테고리", "트렌드점수", "매출지수", "SNS화제성", "검색증가율(%)", "전년대비매출(%)"]
        ).properties(height=380)
        st.altair_chart(bubble, use_container_width=True)

    with right:
        section_header("이번 주 베스트 셀러/주목 상품", "실무자 공유용 핵심 포인트")
        top5 = hot_items.sort_values(["검색증가율(%)", "SNS증가율(%)"], ascending=False).head(5)
        for _, row in top5.iterrows():
            st.markdown(
                f'''
                <div class="insight-box">
                    <div class="insight-title">{row["상품명"]}</div>
                    <div class="insight-body">{row["카테고리"]} · 검색 +{row["검색증가율(%)"]}% · SNS +{row["SNS증가율(%)"]}%<br/>해석: {row["트렌드유형"]}</div>
                </div>
                ''',
                unsafe_allow_html=True,
            )

    bottom_left, bottom_right = st.columns([1, 1])
    with bottom_left:
        section_header("빠른 운영 제안", "바이어-영업담당자가 보면 좋은 실행 항목")
        st.markdown('<span class="tag">HMR 집중 전개</span><span class="tag">소스/파스타 연계 진열</span><span class="tag">피스타치오 유사상품 큐레이션</span><span class="tag">제로/기능성 음료 비교존</span>', unsafe_allow_html=True)
        st.markdown(
            '''
            - **트렌드 확인**: SNS 화제성만 높은 상품과 실제 구매 신호가 강한 상품을 구분해 운영
            - **매출 추이 확인**: HMR·소스·음료는 주 단위 체크, 샤퀴테리·캐비아는 시즌 단위 체크 권장
            - **영업 활용**: 브랜드 미팅 시 ‘검색 증가 근거 + 유사상품 파생 수요’ 자료로 활용
            - **행사 기획**: 피스타치오, 트러플, 홈파티, 저당/고단백 테마로 미니 팝업 기획 가능
            '''
        )
    with bottom_right:
        section_header("카테고리별 상태 요약")
        status_df = filtered_category[["카테고리", "트렌드점수", "검색증가율(%)", "전년대비매출(%)"]].sort_values("트렌드점수", ascending=False)
        st.dataframe(status_df, use_container_width=True, hide_index=True)

with tabs[1]:
    section_header("현재 SNS·검색에서 급상승 중인 상품", "인기가 실제 구매로 이어지는지, 유사상품 탐색형인지 빠르게 보는 탭")
    hot_view = hot_items.copy()
    hot_view["판단"] = np.where((hot_view["검색증가율(%)"] >= 25) & (hot_view["구매전환추정"] >= 7), "실구매 확대 가능성 높음", "유사상품/관심 탐색 가능성 높음")
    left, right = st.columns([1.2, 1])
    with left:
        chart = alt.Chart(hot_view).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
            x=alt.X("상품명:N", sort="-y", title=None),
            y=alt.Y("검색증가율(%):Q", title="검색 증가율(%)"),
            color=alt.Color("카테고리:N", legend=None),
            tooltip=["상품명", "카테고리", "SNS증가율(%)", "검색증가율(%)", "구매전환추정", "트렌드유형", "판단"]
        ).properties(height=360)
        st.altair_chart(chart, use_container_width=True)
    with right:
        section_header("운영 해석")
        st.markdown(
            '''
            - **피스타치오 계열**은 직접 구매뿐 아니라 ‘피스타치오 맛’ 자체를 탐색하는 유사상품 검색이 동반될 수 있습니다.
            - **고단백 요거트**는 해시태그, 검색, 구매전환이 함께 올라 실구매 확장형 신호로 볼 수 있습니다.
            - **트러플 파스타소스 / 바질 페스토**는 레시피 연관 검색이 강해 파스타면, 치즈와 크로스 진열 효과가 큽니다.
            '''
        )
        st.markdown('<span class="soft-tag">유사상품 탐색형</span><span class="soft-tag">실구매 확장형</span><span class="soft-tag">레시피 연관형</span>', unsafe_allow_html=True)
    section_header("상품별 상세 테이블")
    st.dataframe(hot_view.sort_values(["검색증가율(%)", "SNS증가율(%)"], ascending=False), use_container_width=True, hide_index=True)

with tabs[2]:
    section_header("트렌드 상세 분석", "왜 오르는지, 실반응 기반인지, 유사 검색인지 깊게 보는 탭")
    picked = st.selectbox("상세 분석할 카테고리", filtered_category["카테고리"].tolist(), index=0)
    row = category_data[category_data["카테고리"] == picked].iloc[0]
    a, b, c = st.columns(3)
    with a: metric_card("트렌드점수", f'{row["트렌드점수"]}', f'+{row["검색증가율(%)"]}% 검색 증가', True)
    with b: metric_card("SNS 화제성", f'{row["SNS화제성"]}', "콘텐츠 언급량 상위권", True)
    with c: metric_card("전년대비 매출", f'+{row["전년대비매출(%)"]}%', "실매출 연동 신호", True)
    related_items = hot_items[(hot_items["카테고리"] == picked)]
    if related_items.empty:
        related_items = hot_items.sample(3, random_state=7)
    left, right = st.columns([1, 1])
    with left:
        section_header(f"{picked} 인사이트")
        st.markdown(
            f'''
            <div class="insight-box"><div class="insight-title">1) 왜 오르는가</div><div class="insight-body">{picked} 카테고리는 최근 SNS 콘텐츠, 레시피 확산, 프리미엄/건강 키워드 확장이 겹치며 관심이 증가하고 있습니다.</div></div>
            <div class="insight-box"><div class="insight-title">2) 실제 고객 반응인가</div><div class="insight-body">검색 증가와 매출지수가 함께 오르면 실구매형, 검색만 빠르게 오르면 탐색형일 가능성이 큽니다. 현재 {picked}는 두 신호가 모두 양호합니다.</div></div>
            <div class="insight-box"><div class="insight-title">3) 유사상품 검색 가능성</div><div class="insight-body">대표 상품의 풍미/원재료가 화제가 되면 유사 SKU 검색이 동반됩니다. 예: 피스타치오, 트러플, 저당, 고단백.</div></div>
            ''',
            unsafe_allow_html=True,
        )
    with right:
        section_header("연관 상품 시그널")
        st.dataframe(related_items[["상품명", "검색증가율(%)", "SNS증가율(%)", "트렌드유형"]], use_container_width=True, hide_index=True)
    section_header("실무 적용 포인트")
    st.markdown(
        '''
        - **바이어 관점**: ‘이 카테고리가 진짜 매출로 연결되는가’를 먼저 보고 입점/확대 판단
        - **영업 관점**: 브랜드사 미팅에서 검색 증가율, 해시태그 증가, 유사상품 수요를 함께 제시
        - **MD 관점**: 단품보다 테마 진열이 유효한 카테고리는 교차 제안 (예: 파스타면 + 소스 + 치즈)
        - **행사 관점**: 탐색형 트렌드는 체험/시식형 프로모션, 실구매형 트렌드는 물량/광고 집중 운영
        '''
    )

with tabs[3]:
    section_header("트렌드 기반 브랜드/팝업 행사 기획", "어떤 브랜드를 연결할지, 어떤 테마로 팝업을 열지 보는 탭")
    left, right = st.columns([1.2, 1])
    with left:
        bar = alt.Chart(brand_popup).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
            x=alt.X("브랜드:N", sort="-y", title=None),
            y=alt.Y("팝업 적합도:Q"),
            color=alt.value("#7c3aed"),
            tooltip=["브랜드", "연관 카테고리", "트렌드 키워드", "팝업 적합도", "추천 액션"]
        ).properties(height=360)
        st.altair_chart(bar, use_container_width=True)
    with right:
        section_header("행사 기획 제안")
        st.markdown(
            '''
            1. **홈파인 다이닝 위크**: 파스타소스 · 치즈 · 올리브오일 연계
            2. **헬시 브런치 존**: 고단백 요거트 · 저당 음료 · 그래놀라/스낵
            3. **명절 프리미엄 미식 선물전**: 발사믹 · 오일 · 치즈 · 캐비아
            4. **화제 상품 시식존**: 피스타치오/트러플 계열 유사상품 비교 큐레이션
            '''
        )
    section_header("브랜드 후보 리스트")
    st.dataframe(brand_popup.sort_values("팝업 적합도", ascending=False), use_container_width=True, hide_index=True)

with tabs[4]:
    section_header("상품군별 매출 추이", "카테고리별 주차 흐름과 우선 대응 대상을 빠르게 확인")
    sales_pick = st.multiselect("그래프에 표시할 카테고리", options=selected_categories, default=selected_categories[: min(4, len(selected_categories))], key="sales_pick")
    if not sales_pick:
        sales_pick = selected_categories[: min(4, len(selected_categories))]
    sales_chart_df = filtered_sales[filtered_sales["카테고리"].isin(sales_pick)].copy()
    line = alt.Chart(sales_chart_df).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X("주차:T", title=None),
        y=alt.Y("매출지수:Q"),
        color=alt.Color("카테고리:N"),
        tooltip=["주차:T", "카테고리", "매출지수"]
    ).properties(height=380)
    st.altair_chart(line, use_container_width=True)
    summary_sales = (
    sales_chart_df.groupby("카테고리", as_index=False)
    .agg(
        평균_매출지수=("매출지수", "mean"),
        최고_매출지수=("매출지수", "max"),
    )
    .rename(
        columns={
            "평균_매출지수": "평균 매출지수",
            "최고_매출지수": "최고 매출지수",
        }
    )
)
    col1, col2 = st.columns([1, 1])
    with col1:
        section_header("카테고리 평균/최고 매출")
        st.dataframe(summary_sales.sort_values("평균 매출지수", ascending=False), use_container_width=True, hide_index=True)
    with col2:
        section_header("바이어 체크포인트")
        st.markdown(
            '''
            - **HMR / 소스 / 음료**: 신제품 반응 속도가 빨라 주간 모니터링 추천
            - **오일·발사믹 / 치즈**: 선물 수요·행사 시즌 영향을 크게 받음
            - **파스타면 / 향신료**: 단독보다 레시피 연계 매출이 중요
            - **샤퀴테리 / 캐비아**: 객단가와 VIP 수요 중심으로 해석 필요
            '''
        )

with tabs[5]:
    section_header("인스타그램 해시태그 인텔리전스", "최근 #검색 및 조회가 늘어나는 식품 중심으로 트렌드를 파악하는 페이지")
    st.info("현재 버전은 샘플 데이터 기반입니다. 실제 운영 시에는 인스타그램 API/대체 수집 데이터, 검색량 데이터, 자체 수집 로직을 연결하면 됩니다.")
    left, right = st.columns([1.15, 1])
    with left:
        h_chart = alt.Chart(hashtag_df).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
            x=alt.X("해시태그:N", sort="-y", title=None),
            y=alt.Y("7일증가율(%):Q", title="7일 증가율(%)"),
            color=alt.value("#5b21b6"),
            tooltip=["해시태그", "7일증가율(%)", "추정 조회지수", "연관 카테고리", "해석"]
        ).properties(height=360)
        st.altair_chart(h_chart, use_container_width=True)
    with right:
        section_header("이 페이지로 가능한 것")
        st.markdown(
            '''
            - 최근 해시태그 증가 폭이 큰 식품/원재료 확인
            - **실제 구매형인지, 관심 탐색형인지** 해석
            - 연관 카테고리로 입점/행사/콘텐츠 연결
            - 브랜드사 미팅 시 “SNS 화제성 근거” 자료로 활용
            '''
        )
        st.markdown('<span class="tag">#피스타치오</span><span class="tag">#트러플파스타</span><span class="tag">#고단백요거트</span><span class="tag">#제로슈가</span>', unsafe_allow_html=True)
    section_header("해시태그 상세 표")
    st.dataframe(hashtag_df.sort_values("7일증가율(%)", ascending=False), use_container_width=True, hide_index=True)

with tabs[6]:
    section_header("명절 매출 속보", "설/추석 등 시즌 매출 현황을 빠르게 업로드하고 쉽게 접근하기 위한 별도 페이지")
    col1, col2 = st.columns([1.2, 1])
    with col1:
        section_header("속보 업로드 템플릿")
        st.text_input("제목", value="설 선물세트 2주차 매출 속보")
        st.text_input("대상 기간", value="2026-01-12 ~ 2026-01-18")
        st.multiselect("핵심 카테고리", options=category_data["카테고리"].tolist(), default=["오일·발사믹", "치즈", "HMR"])
        st.text_area("핵심 메모", value="오일·발사믹과 치즈 선물세트 반응이 좋고, HMR은 연휴 직전 수요가 급증했습니다.", height=140)
        st.button("속보 저장", use_container_width=True)
    with col2:
        section_header("운영 팁")
        st.markdown(
            '''
            - 제목은 **시즌 + 주차 + 핵심 카테고리** 중심으로 표기
            - 담당자 공유용 링크를 바로 복사할 수 있게 구성
            - 전주 대비 증감, 베스트셀러, 이슈 상품, 행사 반응을 함께 기록
            - 향후에는 엑셀 업로드 후 자동 요약 기능으로 확장 가능
            '''
        )
    section_header("등록된 명절 속보")
    st.dataframe(holiday_news, use_container_width=True, hide_index=True)

st.caption(f'현재 목적: {buyer_goal} · 조회 기간: {period} · 마지막 업데이트: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
