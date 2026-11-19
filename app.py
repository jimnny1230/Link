import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="링크 매핑 & 미리보기", page_icon="🔀", layout="centered")

st.title("🔀 링크 주소 매핑 & 열기")
st.caption("입력한 링크를 지정한 대상 주소(예: 포스타입)로 연결합니다. (외부 사이트의 실제 콘텐츠를 임의 주소로 위장해 띄우는 것은 해당 사이트 정책상 제한됩니다.)")

source_url = st.text_input("원본 링크 입력", placeholder="예: https://my-link.example/123")
target_url = st.text_input("실제로 열 대상 링크", value="https://www.postype.com/")

def fetch_preview(url: str):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=6)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else "제목 없음"
        desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        desc = desc_tag["content"].strip() if desc_tag and desc_tag.get("content") else "설명 정보 없음"
        return title, desc, None
    except Exception as e:
        return None, None, str(e)

if target_url:
    clean_target = target_url.strip()
    if not clean_target.startswith(("http://", "https://")):
        clean_target = "https://" + clean_target

    st.markdown("---")
    st.markdown(f"**입력한 링크:** `{source_url.strip() if source_url.strip() else '(없음)'}`")
    st.markdown(f"**실제 연결될 링크:** `{clean_target}`")
    st.link_button("↗️ 대상 링크 새 탭에서 열기", clean_target, use_container_width=True)

    with st.expander("📄 대상 페이지 미리보기 가져오기"):
        title, desc, err = fetch_preview(clean_target)
        if err:
            st.warning(f"미리보기를 불러오지 못했습니다: {err}")
        else:
            st.markdown(f"**페이지 제목:** {title}")
            st.markdown(f"**요약:** {desc}")
