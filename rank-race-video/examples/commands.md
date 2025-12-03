# 예시 실행 커맨드 모음

## 1. 월 단위 시가총액 순위 변화 (샘플 데이터)

```bash
python src/rank_race_video.py \
  --input examples/korea_market_cap_sample.csv \
  --time_col date \
  --entity_col name \
  --value_col market_cap \
  --time_format "%Y-%m-%d" \
  --time_unit month \
  --top_n 3 \
  --title "국내 시가총액 순위 변화 (월별, 샘플)" \
  --output outputs/korea_market_cap_monthly_sample.mp4
