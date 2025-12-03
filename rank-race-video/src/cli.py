# src/cli.py

import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="시계열 순위 변화 Bar Chart Race 영상 생성기 (일/월 단위 선택 가능)"
    )

    # 기본 입출력
    parser.add_argument("--input", required=True, help="입력 CSV 경로")
    parser.add_argument(
        "--output",
        default="rank_race.mp4",
        help="출력 영상 파일 이름 (mp4)",
    )

    # 컬럼 이름
    parser.add_argument(
        "--time_col",
        default="time",
        help="시간 컬럼 이름 (예: time, date, year...)",
    )
    parser.add_argument(
        "--entity_col",
        default="entity",
        help="대상/이름 컬럼 이름 (예: name, country, company...)",
    )
    parser.add_argument(
        "--value_col",
        default="value",
        help="값 컬럼 이름 (예: value, market_cap, population...)",
    )

    # 시간 파싱
    parser.add_argument(
        "--time_format",
        default=None,
        help=(
            "시간 파싱 포맷 (예: %%Y-%%m-%%d, %%Y-%%m, %%Y). "
            "없으면 pandas가 자동 추론 시도"
        ),
    )

    # 단위 선택: raw / day / month
    parser.add_argument(
        "--time_unit",
        choices=["raw", "day", "month"],
        default="raw",
        help="시간 단위: raw(원본 그대로), day(일 단위), month(월말 기준)",
    )

    # 기간 필터
    parser.add_argument(
        "--start_time",
        default=None,
        help="이 시간(포함) 이후만 사용 (예: 1980-01-01)",
    )
    parser.add_argument(
        "--end_time",
        default=None,
        help="이 시간(포함) 이전만 사용 (예: 2025-11-30)",
    )

    # 시각화 옵션
    parser.add_argument(
        "--top_n",
        type=int,
        default=15,
        help="화면에 보여줄 상위 개수 (기본 15개)",
    )
    parser.add_argument(
        "--title",
        default="Rank Race",
        help="영상 상단 제목",
    )
    parser.add_argument(
        "--steps_per_period",
        type=int,
        default=8,
        help="시간 구간 사이를 몇 단계로 보간할지 (값이 클수록 더 부드러움)",
    )
    parser.add_argument(
        "--period_length",
        type=int,
        default=500,
        help="각 기간 보여주는 시간 (ms). 500이면 0.5초",
    )
    
    # 스타일 선택
    parser.add_argument(
        "--style",
        choices=["pastel_wood", "deep_navy", "minimal_white"],
        default="pastel_wood",
        help="시각화 스타일 프리셋 선택 (기본: pastel_wood)",
    )

    return parser.parse_args()
