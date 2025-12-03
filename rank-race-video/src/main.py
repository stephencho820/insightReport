# src/main.py

from cli import parse_args
from data_processing import load_and_prepare_data
from chart import render_rank_race_video

def main():
    # 1) CLI 인자 파싱
    args = parse_args()

    # 2) 데이터 로드 & 전처리 (pivot + period_fmt)
    pivot, period_fmt = load_and_prepare_data(args)

    # 3) 차트 렌더링 & 영상 생성
    render_rank_race_video(pivot, period_fmt, args)

if __name__ == "__main__":
    main()