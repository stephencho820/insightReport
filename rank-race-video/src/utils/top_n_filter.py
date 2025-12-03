import pandas as pd

def filter_top_n_per_time(pivot: pd.DataFrame, n: int) -> pd.DataFrame:
    """
    pivot(index=time, columns=entity, values=value) 형태의 DF에서
    각 시점별로 Top N만 남기고 나머지 column은 제거하는 함수.
    bar_chart_race의 N+1 bug를 방지하기 위한 전처리용.

    Parameters
    ----------
    pivot : pd.DataFrame
        시간(time index) × 엔티티(columns) 값
    n : int
        유지할 상위 종목 개수

    Returns
    -------
    pd.DataFrame
        모든 시점에서 Top N만 존재하는 pivot
    """

    filtered_frames = []

    for timestamp, row in pivot.iterrows():
        # 값이 큰 순으로 N개 entity 추출
        top_entities = row.sort_values(ascending=False).head(n).index

        # 전체 column 중 top_entities만 남김
        filtered_row = row[top_entities].to_frame().T

        # index 복구
        filtered_row.index = [timestamp]

        filtered_frames.append(filtered_row)

    # 다시 하나로 합침
    filtered_pivot = pd.concat(filtered_frames)

    # 전체 시점에서 등장한 TopN 종목들만 column으로 사용
    # (시간마다 종목 구성이 조금씩 달라도 OK)
    filtered_pivot = filtered_pivot.reindex(
        columns=sorted({col for df in filtered_frames for col in df.columns})
    )

    # NaN → 0
    return filtered_pivot.fillna(0)
# End of top_n_filter.py   