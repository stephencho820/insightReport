# src/collect_korea_market_cap_monthly.py

import argparse
from datetime import datetime, timedelta

import pandas as pd
from pykrx import stock

def parse_args():
    parser = argparse.ArgumentParser(
        description="국내 시가총액 월말 데이터 수집 (KOSPI 상위 20)"
    )
    parser.add_argument(
        "--start",
        default="1995-01-01",
        help="시작 날짜 (YYYY-MM-DD), 기본: 1995-01-01",
    )
    parser.add_argument(
        "--end",
        default=None,
        help="끝 날짜 (YYYY-MM-DD), 기본: 오늘",
    )
    parser.add_argument(
        "--output",
        default="data/korea_market_cap_monthly.csv",
        help="저장할 CSV 경로 (기본: data/korea_market_cap_monthly.csv)",
    )
    return parser.parse_args()


def collect_for_market(date_str: str, market: str) -> pd.DataFrame:
    """
    특정 날짜(date_str, 'YYYYMMDD')와 시장(KOSPI/KOSDAQ)에 대해
    티커별 시가총액을 가져와서 표준 컬럼으로 변환.
    과거 일부 날짜에서 '종목명' 컬럼이 없을 수 있으므로 방어적으로 처리.
    """
    df = stock.get_market_cap_by_ticker(date_str, market=market)
    # index: 티커, columns: 시가총액, 상장주식수, 종가 ...
    df = df.reset_index()  # index → '티커' 컬럼이 생김

    # 현재 df.columns 예시:
    # Index(['티커', '시가총액', '상장주식수', '종가', ...], dtype='object')
    # 또는 ['티커', '종목명', '시가총액', ...] 등

    cols = df.columns.tolist()

    # 1) 티커 컬럼명은 '티커'로 고정
    ticker_col = "티커"
    if ticker_col not in cols:
        # 이 경우는 거의 없겠지만, 혹시라도 대비
        raise RuntimeError(f"'티커' 컬럼이 없습니다. columns={cols}")

    # 2) 시가총액 컬럼명 찾기
    # pykrx 기준으로는 보통 '시가총액'이지만, 혹시 다르면 여기서 매핑
    if "시가총액" in cols:
        mcap_col = "시가총액"
    else:
        # 다른 이름으로 오는 경우가 있다면 여기서 추가로 처리
        # 예: '시가총액(원)' 이런 식이면 startswith로 찾을 수도 있음
        cand = [c for c in cols if "시가" in c and "총액" in c]
        if cand:
            mcap_col = cand[0]
        else:
            raise RuntimeError(f"'시가총액' 컬럼을 찾을 수 없습니다. columns={cols}")

    # 3) 종목명 컬럼이 있으면 사용, 없으면 나중에 pykrx에 다시 물어봐서 채움
    has_name = "종목명" in cols

    if has_name:
        df = df[[ticker_col, "종목명", mcap_col]]
        df.columns = ["ticker", "name", "market_cap"]
    else:
        # 일단 티커, 시가총액만
        df = df[[ticker_col, mcap_col]]
        df.columns = ["ticker", "market_cap"]

        # 종목명 보강 시도
        names = []
        for t in df["ticker"]:
            try:
                nm = stock.get_market_ticker_name(t)
            except Exception:
                nm = t  # 실패하면 그냥 티커 그대로
            names.append(nm)
        df["name"] = names

        # 컬럼 순서 맞추기
        df = df[["ticker", "name", "market_cap"]]

    # 날짜/시장 정보 추가
    df["date"] = datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d")
    df["market"] = market  # "KOSPI" / "KOSDAQ"

    return df


def main():
    args = parse_args()

    market = "kospi"
    top_n = 20

    start = pd.to_datetime(args.start)
    end = pd.to_datetime(args.end) if args.end else datetime.today()

    # 월말 기준 날짜 생성
    dates = pd.date_range(start=start, end=end, freq="M")

    records = []

    print(f"📅 기간: {dates[0].strftime('%Y-%m-%d')} ~ {dates[-1].strftime('%Y-%m-%d')}")
    print("📈 시장: KOSPI (상위 20 종목만 수집)")

    for dt in dates:
        date_str = dt.strftime("%Y%m%d")
        pretty = dt.strftime("%Y-%m-%d")
        print(f"  → {pretty} 수집 중...")

        fallback_date = dt
        fallback_used = False

        for _ in range(31):
            date_str = fallback_date.strftime("%Y%m%d")

            try:
                month_df = collect_for_market(date_str, market.upper())

                if month_df.empty:
                    raise RuntimeError("수집된 데이터가 없습니다.")

                month_df = month_df.nlargest(top_n, "market_cap")

                if fallback_used:
                    used_date = fallback_date.strftime("%Y-%m-%d")
                    print(
                        f"    • {pretty} 데이터 없음 → {used_date} (이전 영업일)로 대체"
                    )

                records.append(month_df)
                break

            except Exception as e:
                fallback_date -= timedelta(days=1)
                fallback_used = True
        else:
            print(f"    ! {pretty} 수집 실패: 직전 31일 내 데이터 없음")
            continue

    if not records:
        print("❌ 수집된 데이터가 없습니다.")
        return

    full = pd.concat(records, ignore_index=True)

    # 정렬: 날짜 ↑, 시가총액 ↓
    full = full.sort_values(["date", "market_cap"], ascending=[True, False])

    # CSV 저장
    output_path = args.output
    # data/ 폴더가 없을 수도 있으니 알아서 만들어주면 더 좋지만,
    # 여기선 사용자가 미리 폴더를 만들어둔다고 가정.
    full.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"\n✅ 저장 완료: {output_path}")
    print(f"   총 {len(full):,} rows")


if __name__ == "__main__":
    main()
