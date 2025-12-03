# src/data_processing.py

import pandas as pd
import numpy as np


def load_and_prepare_data(args):
    """
    CSV를 읽고, 시간 파싱 + 기간 필터 + 단위 변환 + 피벗까지 처리.
    반환:
      - pivot: index=시간, columns=entity, values=value 형태의 DataFrame
      - period_fmt: bar_chart_race에서 쓸 기간 포맷 문자열 (또는 None)
    """
    df = pd.read_csv(args.input)

    time_col = args.time_col

    # 1) 시간 컬럼 파싱
    if args.time_format:
        df[time_col] = pd.to_datetime(df[time_col], format=args.time_format)
    else:
        try:
            df[time_col] = pd.to_datetime(df[time_col], errors="raise")
        except Exception:
            print(
                "[경고] 시간 컬럼을 datetime으로 변환하지 못했습니다. "
                "raw 문자열/숫자 그대로 사용합니다."
            )

    is_datetime = np.issubdtype(df[time_col].dtype, np.datetime64)

    # 2) 기간 필터
    if is_datetime and args.start_time is not None:
        start = pd.to_datetime(args.start_time)
        df = df[df[time_col] >= start]

    if is_datetime and args.end_time is not None:
        end = pd.to_datetime(args.end_time)
        df = df[df[time_col] <= end]

    # 3) 시간 단위 변환
    if is_datetime:
        if args.time_unit == "day":
            # 일 단위: 시간 정보 제거
            df[time_col] = df[time_col].dt.normalize()

        elif args.time_unit == "month":
            # 월 단위: 각 entity별 월말 값(last) 사용
            df = (
                df.set_index(time_col)
                .groupby(args.entity_col)[args.value_col]
                .resample("M")
                .last()
                .reset_index()
            )
    else:
        if args.time_unit in ["day", "month"]:
            print(
                "[경고] time_unit이 day/month로 설정됐지만 시간 컬럼이 datetime이 아니어서 "
                "단위 변환을 생략합니다. 원본 값(raw) 그대로 사용합니다."
            )

    # 4) 정렬
    df = df.sort_values([time_col, args.entity_col])

    # 5) 피벗: index=시간, columns=entity, values=값
    pivot = df.pivot(index=time_col, columns=args.entity_col, values=args.value_col)

    # 6) 시간 순 정렬 + 결측값 처리
    pivot = pivot.sort_index().fillna(0)

    # 7) period_fmt 결정 (bar_chart_race에서 화면에 찍을 형식)
    if np.issubdtype(pivot.index.dtype, np.datetime64):
        if args.time_unit == "month":
            period_fmt = "%Y-%m"
        elif args.time_unit == "day":
            period_fmt = "%Y-%m-%d"
        else:
            period_fmt = "%Y-%m-%d"
    else:
        period_fmt = None

    print("데이터 크기:", pivot.shape)
    if len(pivot.index) > 0:
        print("시간 범위:", pivot.index.min(), "~", pivot.index.max())

    return pivot, period_fmt
