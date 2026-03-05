# Codex Development Sprint

Before development read devdoc.md and understand requirements.

Develop the project following the sprint order below.

------------------------------------------------------------------------

# Sprint 1

Goal Create project base structure

Tasks

Create folder app

Create files

main.py collector.py filter.py scoring.py exporter.py

Implement main() entry

Create dummy data (5 rows) and export leads.xlsx

Completion check

python main.py

leads.xlsx should be generated

------------------------------------------------------------------------

# Sprint 2

Goal Implement job collection

Tasks

collector.py

Use requests to fetch job search results

Use BeautifulSoup to parse data

Extract

company title location url

Return jobs list

Completion jobs list created

------------------------------------------------------------------------

# Sprint 3

Goal Filter job postings

Tasks

Implement filter.py

Allow only postings containing keywords

엑셀 주문관리 쇼핑몰 리포트 데이터

Exclude

카페 식당 주방 서빙 미용 운전 생산직

Function

filter_jobs(jobs)

Completion filtered_jobs created

------------------------------------------------------------------------

# Sprint 4

Goal Score calculation

Implement scoring.py

Score rules

쇼핑몰 +5 주문관리 +4 엑셀 리포트 +3

Function

calculate_score(job)

Keep jobs with score \>= 5

Completion qualified_jobs created

------------------------------------------------------------------------

# Sprint 5

Goal Export Excel

Use pandas

Columns

score company title location summary url

Create summary from title

Output leads.xlsx

------------------------------------------------------------------------

# Sprint 6

Goal Finalize program

Tasks

Remove duplicate jobs Add error handling Add logging

Completion

Program execution should:

collect jobs filter jobs calculate score export Excel

------------------------------------------------------------------------

# Test

Run

python main.py

Check

1 leads.xlsx exists 2 At least 5 rows saved 3 No errors
