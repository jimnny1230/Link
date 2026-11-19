import streamlit as st
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import re

st.set_page_config(page_title="스마트 링크 변환기", page_icon="🔗", layout="centered")

def convert_url(raw_url: str) -> dict:
    url = raw_url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    results = {"원본 정리": url}

    # 1. 유튜브 (YouTube) 링크 변환
    if "youtube.com" in domain or "youtu.be" in domain:
        video_id = None
        if "youtu.be" in domain:
            video_id = parsed.path.lstrip("/").split("/")[0]
        elif "/shorts/" in parsed.path:
            video_id = parsed.path.split("/shorts/")[1].split("/")[0]
        elif "/live/" in parsed.path:
            video_id = parsed.path.split("/live/")[1].split("/")[0]
        else:
            qs = parse_qs(parsed.query)
            video_id = qs.get("v", [None])[0]

        if video_id:
            results["표준 시청 링크 (추적 제거)"] = f"https://www.youtube.com/watch?v={video_id}"
            results["단축 공유 링크"] = f"https://youtu.be/{video_id}"
            results["전체화면 임베드 플레이어"] = f"https://www.youtube.com/embed/{video_id}"

    # 2. 포스타입 (Postype) 링크 변환
    elif "postype.com" in domain:
        # 불필요한 UTM/공유 파라미터 제거
        clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))
        results["깔끔한 포스타입 링크 (파라미터 제거)"] = clean_url

        # 모바일 서브도메인(m.) 또는 www 정리
        if domain.startswith("m."):
            desktop_domain = domain[2:]
            results["PC 버전 링크"] = urlunparse((parsed.scheme, desktop_domain, parsed.path, "", "", ""))

    # 3. X (트위터) 링크 변환
    elif "x.com" in domain or "twitter.com" in domain:
        clean_path = parsed.path
        results["X (x.com) 링크"] = f"https://x.com{clean_path}"
        results["Twitter (twitter.com) 링크"] = f"https://twitter.com{clean_path}"
        results["미리보기 최적화 (vxtwitter)"] = f"https://vxtwitter.com{clean_path}"

    # 4. 기타 일반 링크 (추적 파라미터 utm_ 등 제거)
    else:
        qs = parse_qs(parsed.query)
        filtered_qs = {k: v for k, v in qs.items() if not k.startswith("utm_") and k not in ["si", "fbclid", "igshid"]}
        new_query = urlencode(filtered_qs, doseq=True)
        clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
        results["추적 파라미터 제거 링크"] = clean_url

    return results

# --- UI 구성 ---
st.title("🔗 링크 변환 & 바로 열기")
st.caption("유튜브, 포스타입, X(트위터) 등의 링크에서 불필요한 추적 꼬리표를 떼어내고 원하는 형식으로 변환합니다.")

input_url = st.text_input("변환할 링크를 붙여넣으세요", placeholder="https://www.youtube.com/shorts/... 또는 https://...postype.com/post/...")

# 커스텀 치환 규칙 (선택 사항)
with st.expander("⚙️ 고급: 직접 문자열 치환하기 (선택)"):
    col1, col2 = st.columns(2)
    with col1:
        find_str = st.text_input("찾을 문자열", placeholder="예: m.postype.com")
    with col2:
        replace_str = st.text_input("바꿀 문자열", placeholder="예: www.postype.com")

if input_url:
    converted_dict = convert_url(input_url)

    # 사용자 지정 치환이 입력된 경우 추가
    if find_str and replace_str:
        custom_url = input_url.strip().replace(find_str, replace_str)
        if not custom_url.startswith(("http://", "https://")):
            custom_url = "https://" + custom_url
        converted_dict["사용자 지정 치환 링크"] = custom_url

    st.subheader("변환 결과")
    for label, link in converted_dict.items():
        with st.container(border=True):
            st.markdown(f"**{label}**")
            st.code(link, language=None)
            st.link_button("↗️ 새 탭에서 바로 열기", link, use_container_width=True)
