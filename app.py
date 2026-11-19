import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="링크 매핑 & 열기", page_icon="🔀", layout="centered")

st.title("🔀 원본 링크 → 포스타입 연결기")
st.caption("원본 링크를 입력하면 지정한 대상 주소(기본: 포스타입)로 연결합니다.")

source_url = st.text_input("원본 링크 입력", placeholder="예: https://youtube.com/... 또는 아무 링크")
target_url = st.text_input("실제로 열 대상 링크", value="https://www.postype.com/")

def normalize_url(url: str) -> str:
    u = url.strip()
    if not u:
        return ""
    if not u.startswith(("http://", "https://")):
        return "https://" + u
    return u

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

clean_source = normalize_url(source_url)
clean_target = normalize_url(target_url)

if clean_source:
    # 원본 링크가 입력되었을 때 대상 링크(기본 포스타입)를 최종 목적지로 사용
    final_link = clean_target if clean_target else "https://www.postype.com/"

    st.markdown("---")
    st.markdown(f"**입력한 원본 링크:** `{clean_source}`")
    st.markdown(f"**실제 연결될 링크:** `{final_link}`")
    st.link_button("↗️ 포스타입 새 탭에서 열기", final_link, use_container_width=True)

    with st.expander("📄 대상 페이지 미리보기 가져오기"):
        title, desc, err = fetch_preview(final_link)
        if err:
            st.warning(f"미리보기를 불러오지 못했습니다: {err}")
        else:
            st.markdown(f"**페이지 제목:** {title}")
            st.markdown(f"**요약:** {desc}")
else:
    st.info("위 **원본 링크 입력** 칸에 링크를 먼저 입력해 주세요.")
