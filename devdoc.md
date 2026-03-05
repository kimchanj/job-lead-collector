# Job Lead Collector - devdoc

## Project Purpose

Collect job postings related to Excel / order management / reports from
job sites and generate a sales lead list automatically.

Output file: leads.xlsx

## Program Flow

1.  Search jobs
2.  Filter jobs
3.  Calculate score
4.  Select qualified leads
5.  Export Excel

## Target Keywords

엑셀 주문관리 쇼핑몰 스마트스토어 상품관리 재고관리 매출관리 리포트
데이터

## Excluded Keywords

카페 식당 주방 서빙 미용 운전 생산직

## Score Rules

### Shopping keywords

쇼핑몰 스마트스토어 쿠팡 +5

### Order related

주문관리 출고관리 발주관리 +4

### Automation related

엑셀 리포트 정산 데이터 +3

## Save Condition

score \>= 5

## Excel Columns

score company title location summary url

## Summary Rule

Create summary based on job title.

Example

Title: 쇼핑몰 주문관리 사무직 (엑셀)

Summary: 쇼핑몰 주문관리 / 엑셀 정리

## Project Structure

app/ main.py collector.py filter.py scoring.py exporter.py

## Tech Stack

Python 3

Libraries requests pandas beautifulsoup4

## Program Execution

python main.py

Output leads.xlsx

## Success Criteria

1.  Job collection works
2.  Filtering works
3.  Score calculation works
4.  Excel file generated
