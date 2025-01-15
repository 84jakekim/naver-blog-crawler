# 네이버 블로그 검색 수집기

네이버 블로그의 검색 결과를 쉽게 수집하고 엑셀 파일로 저장할 수 있는 웹 애플리케이션입니다.

## 주요 기능

- 키워드 기반 네이버 블로그 검색
- 검색 결과의 본문 내용까지 수집
- 엑셀 파일로 결과 다운로드
- 실시간 방문자 카운터

## 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/84jakekim/naver-blog-crawler.git
cd naver-blog-crawler
```

2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

3. 네이버 API 키 설정
`.streamlit/secrets.toml` 파일을 생성하고 다음 내용을 추가:
```toml
NAVER_CLIENT_ID = "your_client_id"
NAVER_CLIENT_SECRET = "your_client_secret"
```

4. 앱 실행
```bash
streamlit run blog_crawler.py
```

## 배포 정보

이 앱은 Streamlit Community Cloud를 통해 배포되었습니다.
방문하기: [앱 링크]

## 제작자 정보

- 제작자: k.JAVIS
- 연락처: [Threads @k.javis_____](https://www.threads.net/@k.javis_____)
