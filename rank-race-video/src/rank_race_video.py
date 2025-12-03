import argparse
import os
import pandas as pd
import numpy as np
import bar_chart_race as bcr
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager

# ---- 다크 스타일 + 한글 폰트 ----
plt.style.use("dark_background")
matplotlib.rcParams["axes.facecolor"] = "#020617"   # 아주 진한 남색 톤
matplotlib.rcParams["figure.facecolor"] = "#020617"

# 레포 내 fonts/NanumGothic.ttf를 쓰는 경우 (있으면)
FONT_PATH = os.path.join(os.path.dirname(__file__), "..", "fonts", "NanumGothic.ttf")

if os.path.exists(FONT_PATH):
    font_manager.fontManager.addfont(FONT_PATH)
    prop = font_manager.FontProperties(fname=FONT_PATH)
    font_name = prop.get_name()
    matplotlib.rcParams["font.family"] = font_name
else:
    # 시스템에 설치된 NanumGothic이 있으면 그걸 시도
    matplotlib.rcParams["font.family"] = "NanumGothic"

matplotlib.rcParams["axes.unicode_minus"] = False

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

    return parser.parse_args()


def main():
    args = parse_args()

    # 1) CSV 로드
    df = pd.read_csv(args.input)

    time_col = args.time_col

    # 2) 시간 컬럼 파싱 시도
    if args.time_format:
        df[time_col] = pd.to_datetime(df[time_col], format=args.time_format)
    else:
        try:
            df[time_col] = pd.to_datetime(df[time_col], errors="raise")
        except Exception:
            # datetime으로 변환 실패하면 경고만 띄우고 raw 값 사용
            print(
                "[경고] 시간 컬럼을 datetime으로 변환하지 못했습니다. "
                "raw 문자열/숫자 그대로 사용합니다."
            )

    # datetime 타입인지 확인
    is_datetime = np.issubdtype(df[time_col].dtype, np.datetime64)

    # 3) 기간 필터 (datetime일 때만 적용)
    if is_datetime and args.start_time is not None:
        start = pd.to_datetime(args.start_time)
        df = df[df[time_col] >= start]

    if is_datetime and args.end_time is not None:
        end = pd.to_datetime(args.end_time)
        df = df[df[time_col] <= end]

    # 4) 시간 단위 변환
    if is_datetime:
        if args.time_unit == "day":
            # 시간 → 날짜(자정)로 normalize (일 단위)
            df[time_col] = df[time_col].dt.normalize()

        elif args.time_unit == "month":
            # 각 entity별로 월말(last) 값 사용
            df = (
                df.set_index(time_col)
                .groupby(args.entity_col)[args.value_col]
                .resample("M")  # 월말
                .last()  # 마지막 값 사용
                .reset_index()
            )
    else:
        if args.time_unit in ["day", "month"]:
            print(
                "[경고] time_unit이 day/month로 설정됐지만 시간 컬럼이 datetime이 아니어서 "
                "단위 변환을 생략합니다. 원본 값(raw) 그대로 사용합니다."
            )

    # 5) 정렬
    df = df.sort_values([time_col, args.entity_col])

    # 6) 피벗: index=시간, columns=entity, values=값
    pivot = df.pivot(
        index=time_col, columns=args.entity_col, values=args.value_col
    )

    # 7) 시간 순으로 정렬
    pivot = pivot.sort_index()

    # 8) 결측값 처리
    pivot = pivot.fillna(0)

    # 9) period_fmt 설정
    if np.issubdtype(pivot.index.dtype, np.datetime64):
        if args.time_unit == "month":
            period_fmt = "%Y-%m"
        elif args.time_unit == "day":
            period_fmt = "%Y-%m-%d"
        else:  # raw지만 datetime인 경우
            period_fmt = "%Y-%m-%d"
    else:
        # datetime이 아니면 index 그대로 사용
        period_fmt = None

    print("데이터 크기:", pivot.shape)
    if len(pivot.index) > 0:
        print("시간 범위:", pivot.index.min(), "~", pivot.index.max())
    print("영상 생성 중...")

    # 10) Bar Chart Race 생성
    shared_fontdict = {"family": matplotlib.rcParams["font.family"]}

    bcr.bar_chart_race(
        df=pivot,
        filename=args.output,
        n_bars=args.top_n,

        # 제목 크게 + 단위는 제목에서만 표현
        title=args.title,   # 예: "국내 시가총액 순위 변화 (월별, 단위: 조 원)"
        title_size=34,

        # 연도(기간) 라벨 크게, 화면 오른쪽 아래 쪽에 띄우기
        period_fmt=period_fmt,
        period_label={
            "x": 0.95,      # 오른쪽 끝
            "y": 0.12,      # 아래쪽으로 조금
            "ha": "right",
            "va": "center",
            "size": 32,
            "weight": "bold",
        },

        steps_per_period=args.steps_per_period,
        period_length=args.period_length,
        interpolate_period=True,

        figsize=(16, 9),
        dpi=160,

        # 글씨 크기 튜닝
        bar_label_size=20,      # 바 끝 숫자
        tick_label_size=20,     # 왼쪽 종목명
        shared_fontdict=shared_fontdict,

        # 그래픽 느낌: 바는 꽉 차게, 약간 투명
        fixed_max=True,
        bar_size=0.96,
        bar_kwargs={
            "alpha": 0.9,
            # edgecolor는 살짝만 줄 수도 있음 (너무 보고서 느낌 나면 빼도 됨)
            # "edgecolor": "#0f172a",
        },
    )

    print("생성 완료:", args.output)

if __name__ == "__main__":
    main()
