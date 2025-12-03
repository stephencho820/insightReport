# src/chart.py

import matplotlib
import matplotlib.pyplot as plt
import bar_chart_race as bcr

from styles import apply_style
from utils.top_n_filter import filter_top_n_per_time


def render_rank_race_video(pivot, period_fmt, args):
    pivot = pivot.sort_index()
    pivot = filter_top_n_per_time(pivot, args.top_n)

    # 🔥 영상에서는 값만 '백만' 단위로 축소해서 사용 (원본 CSV는 그대로 유지)
    pivot = pivot / 1_000_000  

    style_cfg = apply_style(getattr(args, "style", "pastel_wood"))
    fig, ax = plt.subplots(figsize=(16, 9), dpi=160)

    # ── 레이아웃 (여백) ──
    fig.subplots_adjust(
        left=style_cfg.get("subplot_left", 0.22),
        right=style_cfg.get("subplot_right", 0.97),
        top=style_cfg.get("subplot_top", 0.80),
        bottom=style_cfg.get("subplot_bottom", 0.12),
    )

    # x축(가로축) 눈금은 label만 숨기고, 얇은 그리드만 남김 → 고급 리포트 느낌
    ax.tick_params(axis="x", which="both", bottom=False, labelbottom=False)
    ax.xaxis.grid(True)

    # y축 스파인(테두리)만 아주 연하게 남기거나, 완전 숨기고 싶으면 False
    for spine in ["top", "right", "bottom"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_linewidth(0.7)

    # 🔥 제목은 fig.suptitle로 (항상 보이게)
    fig.suptitle(
        args.title,
        fontsize=style_cfg.get("title_size", 34),
        fontweight="bold",
        y=0.92,
        ha="center",
        color=style_cfg.get("title_color", "#3B3A36"),  # pastel_wood 기준
        fontfamily=matplotlib.rcParams["font.family"],
    )

    shared_fontdict = {"family": matplotlib.rcParams["font.family"]}

    bcr.bar_chart_race(
        df=pivot,
        filename=args.output,
        n_bars=args.top_n,

        title=None,  # suptitle로 대체

        period_fmt=period_fmt,
        period_label={
            "x": 0.95,
            "y": style_cfg.get("period_label_y", 0.13),
            "ha": "right",
            "va": "center",
            "size": style_cfg.get("period_label_size", 28),
            "weight": "bold",
        },

        steps_per_period=args.steps_per_period,
        period_length=args.period_length,
        interpolate_period=True,

        fig=fig,
        dpi=160,

        bar_label_size=style_cfg.get("bar_label_size", 18),
        tick_label_size=style_cfg.get("tick_label_size", 18),
        shared_fontdict=shared_fontdict,

        # 🔥 숫자 라벨 포맷: 쉼표 + 소수점 없음 (ex. 123,456)
        bar_label_fmt="{:,.0f}",

        fixed_max=True,
        bar_size=style_cfg.get("bar_size", 0.78),
        bar_kwargs={"alpha": 0.94},
        cmap=style_cfg.get("cmap", "Pastel1"),
    )

    print("생성 완료:", args.output)