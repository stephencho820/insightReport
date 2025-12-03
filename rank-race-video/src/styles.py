# src/styles.py
"""
그래프 전체 무드를 바꾸는 스타일 프리셋 모듈.

사용 예:
    from styles import apply_style

    style_cfg = apply_style("pastel_wood")
"""

import os
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager


def _setup_font():
    """한글 폰트 세팅 (레포 내 NanumGothic.ttf 우선)."""
    FONT_PATH = os.path.join(
        os.path.dirname(__file__), "..", "fonts", "NanumGothic.ttf"
    )

    if os.path.exists(FONT_PATH):
        font_manager.fontManager.addfont(FONT_PATH)
        prop = font_manager.FontProperties(fname=FONT_PATH)
        matplotlib.rcParams["font.family"] = prop.get_name()
    else:
        # 시스템에 설치된 나눔고딕 시도
        matplotlib.rcParams["font.family"] = "NanumGothic"

    matplotlib.rcParams["axes.unicode_minus"] = False


# 스타일별 설정값 (배경/텍스트 색 + bar 크기/폰트 사이즈/레이아웃 등)
_STYLE_CONFIGS = {
    "pastel_wood": {
        # 전체 색감 & 기본 스타일
        "rc": {
            "figure.facecolor": "#F6F1E9",   # 조금 더 밝은 베이지
            "axes.facecolor":   "#F6F1E9",
            "axes.edgecolor":   "#E0D8CC",

            "axes.grid": True,
            "grid.color": "#D7CABB",        # 아주 연한 우드톤 그리드
            "grid.alpha": 0.25,
            "grid.linestyle": "-",

            "text.color": "#3B3A36",        # 다크브라운 계열
            "xtick.color": "#6B6157",
            "ytick.color": "#3B3A36",
            "ytick.major.pad": 14,          # y축 레이블과 바 사이 여유

            # 폰트는 _setup_font()에서 Nanum으로 세팅됨
        },

        # 레이아웃: 제목/차트/기간 라벨 간 여백
        "subplot_left":   0.10,   # 왼쪽 여백 살짝 좁혀서 화면 활용
        "subplot_right":  0.97,
        "subplot_top":    0.80,   # 위에 제목 들어갈 자리 확보
        "subplot_bottom": 0.12,

        # 폰트 크기들
        "title_size":         34,   # 메인 타이틀
        "period_label_size":  28,   # 우측 하단 날짜
        "period_label_y":     0.13, # 날짜 위치 (조금 위로)

        "bar_label_size": 18,       # 바 끝 숫자
        "tick_label_size": 18,      # 종목명

        # 막대 설정
        "bar_size": 0.78,           # 0.85 → 0.78 로 줄여서 바 사이 여백 늘리기

        # 파스텔 컬러 팔레트
        "cmap": "Pastel1",
        # 필요하면 나중에 직접 컬러 리스트로 바꾸자 (ex. ['#f5a3a3', '#f6c38b', ...])
    },

    # deep_navy, minimal_white 등은 기존 그대로 두면 됨
    "deep_navy": {
        "rc": {
            "figure.facecolor": "#020617",
            "axes.facecolor": "#020617",
            "axes.edgecolor": "#020617",
            "axes.grid": False,
            "text.color": "#E5E7EB",
            "xtick.color": "#E5E7EB",
            "ytick.color": "#E5E7EB",
            "ytick.major.pad": 10,
        },
        "subplot": {"left": 0.26, "right": 0.97, "top": 0.82, "bottom": 0.12},
        "title_size": 32,
        "period_label_size": 30,
        "period_label_y": 0.13,
        "bar_label_size": 18,
        "tick_label_size": 18,
        "bar_size": 0.90,
        "cmap": "tab20c",
    },
    "minimal_white": {
        "rc": {
            "figure.facecolor": "#F9FAFB",
            "axes.facecolor": "#F9FAFB",
            "axes.edgecolor": "#F9FAFB",
            "axes.grid": False,
            "text.color": "#111827",
            "xtick.color": "#6B7280",
            "ytick.color": "#111827",
            "ytick.major.pad": 10,
        },
        "subplot": {"left": 0.24, "right": 0.96, "top": 0.80, "bottom": 0.12},
        "title_size": 32,
        "period_label_size": 28,
        "period_label_y": 0.14,
        "bar_label_size": 18,
        "tick_label_size": 18,
        "bar_size": 0.88,
        "cmap": "Set2",
    },
}


def apply_style(style_name: str):
    """
    스타일 이름에 맞게 rcParams를 설정하고,
    chart.py에서 사용할 추가 설정값 dict를 반환.

    반환 예:
        {
            "subplot": {...},
            "title_size": ...,
            "period_label_size": ...,
            ...
        }
    """
    if style_name not in _STYLE_CONFIGS:
        style_name = "pastel_wood"

    # 기본 스타일 리셋 후 우리 스타일 적용
    plt.style.use("default")
    _setup_font()

    cfg = _STYLE_CONFIGS[style_name]

    # rcParams 적용
    matplotlib.rcParams.update(cfg["rc"])

    return cfg
# End of styles.py