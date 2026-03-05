# Job Lead Collector

사람인 검색 결과를 기반으로 채용 공고를 수집하고, 키워드 필터/점수화 후 엑셀 리드 파일을 생성하는 Python 프로그램입니다.

## 기능
- 사람인 공고 수집(API 키 사용 가능 시 API 우선, 없으면 검색 결과 HTML 파싱)
- 키워드 기반 포함/제외 필터링
- 점수 계산(`score >= 5` 저장)
- `out/leads.xlsx` 엑셀 출력
- 실행 로그 `out/run.log` 기록

## 프로젝트 구조
```text
job-lead-collector/
  main.py
  requirements.txt
  app/
    main.py
    collector.py
    filter.py
    scoring.py
    exporter.py
  out/
```

## 실행 환경
- Python 3.10+
- Windows / macOS / Linux

## 설치
```bash
pip install -r requirements.txt
```

## 실행 방법
```bash
python main.py
```

실행이 완료되면 아래 파일이 생성됩니다.
- `out/leads.xlsx`
- `out/run.log`

## 환경 변수(선택)
- `SARAMIN_API_KEY`
  - 설정 시 사람인 Open API를 먼저 시도합니다.
  - 없거나 실패하면 검색 결과 페이지 파싱으로 자동 전환됩니다.

예시(PowerShell):
```powershell
$env:SARAMIN_API_KEY="your_api_key"
python main.py
```

## 동작 규칙
- 수집 필드: `company`, `title`, `location`, `url`, `description`
- 상세 페이지 대량 호출 없이 검색 결과 리스트 기준으로 수집
- 요청 옵션: Session 사용, timeout 15초, 재시도 3회(1/2/4초 백오프)
- 페이지네이션: 최대 3페이지

## 출력 엑셀 컬럼
- `score`
- `company`
- `title`
- `location`
- `summary`
- `url`

## 문제 해결
- 수집 결과가 0건이면:
  1. 네트워크/방화벽 제한 확인
  2. `out/run.log`에서 요청 실패 로그 확인
  3. 키워드/셀렉터 변경 또는 API 키 사용 검토

## 라이선스
사내/개인 용도로 자유롭게 수정해 사용하세요.