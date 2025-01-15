import streamlit as st
import pandas as pd
import requests
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
import time

# Naver API 키 가져오기
try:
    NAVER_CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
    NAVER_CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
except Exception as e:
    st.error("Naver API 키가 설정되지 않았습니다. .streamlit/secrets.toml 파일을 확인해주세요.")
    st.stop()

def get_blog_content(url):
    try:
        # 블로그 아이디와 포스트 번호 추출
        if 'blog.naver.com' in url:
            # URL에서 블로그 아이디와 포스트 번호 추출
            match = re.search(r'blog\.naver\.com/([^/]+)/([0-9]+)', url)
            if not match:
                return ""
            
            blog_id = match.group(1)
            post_id = match.group(2)
            
            # 모바일 뷰 URL 사용 (더 깔끔한 HTML 구조)
            mobile_url = f'https://m.blog.naver.com/PostView.naver?blogId={blog_id}&logNo={post_id}'
            
            # 헤더 설정
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            }
            
            # 본문 가져오기
            response = requests.get(mobile_url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            content = []
            
            # 본문 컨테이너 찾기 (여러 에디터 버전 지원)
            containers = soup.select('.se-component, .se_component, #viewTypeSelector, .post_ct')
            
            for container in containers:
                # 이미지 설명 텍스트
                img_descriptions = container.select('.se-caption, .se_caption, .se-text')
                for desc in img_descriptions:
                    text = desc.get_text(strip=True)
                    if text:
                        content.append(text)
                
                # 일반 텍스트
                text_blocks = container.select('.se-text-paragraph, .se_textarea, .se_component_wrap')
                for block in text_blocks:
                    text = block.get_text(strip=True)
                    if text:
                        content.append(text)
            
            # 구버전 에디터
            if not content:
                old_content = soup.select_one('#postViewArea, .post_ct')
                if old_content:
                    content = [old_content.get_text(strip=True)]
            
            # 모든 텍스트를 공백으로 구분하여 한 줄로 합치기
            return ' '.join(content) if content else ""
            
        return ""
        
    except Exception as e:
        st.error(f"본문 추출 중 오류: {str(e)}")
        return ""

def search_blogs(keyword, client_id, client_secret, display=10):
    url = "https://openapi.naver.com/v1/search/blog"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    params = {
        "query": keyword,
        "display": display,
        "start": 1,
        "sort": "sim"  # 정확도순 정렬
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API 호출 중 오류 발생: {str(e)}")
        return None

def get_blog_posts(keyword, post_count=10, progress_bar=None):
    """블로그 포스트를 검색하고 내용을 수집합니다."""
    results = []
    total_pages = (post_count + 9) // 10  # 올림 나눗셈
    
    for page in range(total_pages):
        display = min(10, post_count - (page * 10))  # 마지막 페이지 처리
        
        # 검색 API 호출
        posts = search_blogs(keyword, NAVER_CLIENT_ID, NAVER_CLIENT_SECRET, display)
        
        if not posts:
            break
            
        for i, post in enumerate(posts):
            if len(results) >= post_count:
                break
                
            # 본문 내용 가져오기
            content = get_blog_content(post['link'])
            
            results.append({
                '순위': len(results) + 1,
                '제목': post['title'].replace('<b>', '').replace('</b>', ''),
                '작성자': post['bloggername'],
                '작성일': post['postdate'],
                '링크': post['link'],
                '본문': content
            })
            
            # 진행률 업데이트
            if progress_bar is not None:
                current_progress = (len(results) / post_count)
                progress_bar.progress(current_progress, text=f"수집 진행중... ({len(results)}/{post_count})")
            
            # API 호출 제한 방지를 위한 딜레이
            time.sleep(0.1)
    
    return results

def increment_visitor_count():
    if 'visitor_count' not in st.session_state:
        st.session_state.visitor_count = 0
    st.session_state.visitor_count += 1
    return st.session_state.visitor_count

# 스트림릿 앱 설정
st.set_page_config(page_title="네이버 블로그 검색 수집기", page_icon="📝", layout="wide")

# 방문자 수를 우측 상단에 표시
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500&display=swap');
        
        .visitor-counter {
            position: fixed;
            top: 60px;
            right: 20px;
            padding: 10px 20px;
            background: linear-gradient(135deg, #6c5ce7, #a367fc);
            border-radius: 25px;
            font-size: 0.95em;
            z-index: 1000;
            box-shadow: 0 4px 15px rgba(108, 92, 231, 0.2);
            font-family: 'Noto Sans KR', sans-serif;
            color: white;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .visitor-counter:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(108, 92, 231, 0.3);
        }
        
        .visitor-counter .icon {
            font-size: 1.2em;
            margin-right: 2px;
        }
        
        .visitor-counter .count {
            font-weight: 500;
            color: #ffffff;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }
        
        .visitor-counter .label {
            opacity: 0.9;
            font-size: 0.9em;
        }
    </style>
""", unsafe_allow_html=True)

visitor_count = increment_visitor_count()
st.markdown(f"""
    <div class="visitor-counter">
        <span class="icon">👥</span>
        <span class="count">{visitor_count:,}</span>
        <span class="label">방문자</span>
    </div>
""", unsafe_allow_html=True)

# 메인 화면
st.title("네이버 블로그 검색 결과 수집기 ✨")

# 사용 방법 안내
st.markdown("""
### 안녕하세요! 👋 네이버 블로그 검색 결과를 쉽게 수집할 수 있어요.

#### 📌 사용 방법
1. 검색하고 싶은 키워드를 입력해주세요.
2. 수집하고 싶은 게시글 수를 선택해주세요. (1~100개)
3. '검색 시작' 버튼을 클릭하면 끝!

#### ✨ 특징
- 검색 결과는 네이버 검색 노출 순위 그대로 가져옵니다.
- 1번이 네이버 검색에서 가장 상위에 노출된 게시글이에요.
- 블로그 본문 내용까지 모두 수집합니다.
- 수집된 결과는 엑셀 파일로 다운로드할 수 있어요.

#### 🔍 더 많은 정보를 원하시나요?
제작자의 스레드를 방문해보세요: [k.javis_____](https://www.threads.net/@k.javis_____)
""")

# 구분선 추가
st.markdown("---")

# 검색 설정
col1, col2 = st.columns([2, 1])
with col1:
    keyword = st.text_input("검색어를 입력하세요")
with col2:
    post_count = st.number_input("수집할 게시글 수", min_value=1, max_value=100, value=10)

if st.button("검색 시작", type="primary"):
    if keyword:
        progress_container = st.empty()
        progress_bar = progress_container.progress(0, text="수집 준비중...")
        
        with st.spinner("데이터를 수집하는 중입니다..."):
            results = get_blog_posts(keyword, post_count, progress_bar)
            
            progress_container.empty()
            
            if results:
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True)
                
                # 엑셀 다운로드 버튼
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="엑셀 파일 다운로드",
                    data=csv,
                    file_name=f'네이버블로그_검색결과_{keyword}_{len(results)}건.csv',
                    mime='text/csv'
                )
            else:
                st.error("검색 결과를 찾을 수 없습니다.")
    else:
        st.warning("검색어를 입력해주세요.")