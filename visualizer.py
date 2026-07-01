"""
可视化模块：生成散点图、柱状图，直观展示筛选结果
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import platform
import traceback

# ======================== 中文字体（跨平台自适应）========================
import matplotlib.font_manager as fm

_candidate_fonts = []
_system = platform.system()
print(f"  [诊断] 当前系统：{_system}")

if _system == "Linux":
    _candidate_fonts = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    ]
elif _system == "Darwin":
    _candidate_fonts = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
    ]
elif _system == "Windows":
    _candidate_fonts = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
    ]

_font_loaded = False
for _fp in _candidate_fonts:
    print(f"  [诊断] 尝试字体：{_fp} ... ", end="")
    if os.path.exists(_fp):
        try:
            fm.fontManager.addfont(_fp)
            _font_name = fm.FontProperties(fname=_fp).get_name()
            plt.rcParams["font.family"] = _font_name
            _font_loaded = True
            print(f"✓ 已加载（{_font_name}）")
            break
        except Exception as e:
            print(f"✗ 加载失败：{e}")
    else:
        print("✗ 文件不存在")

if not _font_loaded:
    print("  [诊断] 未找到系统中文字体，使用 matplotlib 回退方案")
    plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]

plt.rcParams["axes.unicode_minus"] = False


def _get_save_path(filename: str) -> str:
    """保存到脚本所在目录（而非终端当前目录）"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, filename)


def plot_pe_pb_scatter(result: pd.DataFrame, top_n: int = 30, save_path: str = None):
    """散点图：PE vs PB，气泡大小反映市值"""
    data = result.head(top_n).copy()
    if data.empty:
        print("  [跳过] 筛选结果为空，不生成散点图")
        return

    try:
        fig, ax = plt.subplots(figsize=(11, 7))

        size = np.clip(data["market_cap"].values / 5, 30, 500)
        color = data["turnover"].fillna(0).values

        ax.scatter(
            data["pe"], data["pb"],
            s=size, c=color, cmap="Blues", alpha=0.7, edgecolors="#333", linewidth=0.5
        )

        for _, row in data.iterrows():
            ax.annotate(row["name"], (row["pe"], row["pb"]),
                        fontsize=7, ha="center", va="bottom",
                        textcoords="offset points", xytext=(0, 4))

        cbar = plt.colorbar(ax.collections[0], ax=ax)
        cbar.set_label("换手率 (%)", fontsize=11)

        ax.set_xlabel("市盈率 (PE)", fontsize=13)
        ax.set_ylabel("市净率 (PB)", fontsize=13)
        ax.set_title(f"A股低估值筛选 - PE vs PB 散点图 (Top {top_n})\n气泡大小 ∝ 市值，颜色 ∝ 换手率",
                     fontsize=14, fontweight="bold")
        ax.grid(True, alpha=0.25)

        if save_path is None:
            save_path = _get_save_path("chart_scatter.png")
        fig.tight_layout()
        fig.savefig(save_path, dpi=150)
        print(f"  ✓ 散点图已保存：{save_path}")
        plt.close(fig)
    except Exception:
        print(f"  ✗ 散点图生成失败：")
        traceback.print_exc()
        plt.close("all")


def plot_top_pe_bar(result: pd.DataFrame, top_n: int = 15, save_path: str = None):
    """柱状图：PE 最低的 N 只股票"""
    data = result.head(top_n).copy()
    if data.empty:
        print("  [跳过] 筛选结果为空，不生成柱状图")
        return

    try:
        names = data["name"].tolist()[::-1]
        pe_vals = data["pe"].tolist()[::-1]
        pb_vals = data["pb"].tolist()[::-1]

        fig, ax = plt.subplots(figsize=(11, 6))

        colors = ["#27ae60" if pb < 1.0 else "#3498db" if pb < 2.0 else "#95a5a6"
                  for pb in pb_vals]

        bars = ax.barh(names, pe_vals, color=colors, edgecolor="white", height=0.7)

        for bar, pe, pb in zip(bars, pe_vals, pb_vals):
            ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                    f"PE {pe:.1f}  PB {pb:.2f}", va="center", fontsize=8)

        ax.set_xlabel("市盈率 (PE)", fontsize=13)
        ax.set_title(f"低市盈率 Top {top_n}（绿=破净 PB<1  蓝=低PB<2  灰=其他）",
                     fontsize=14, fontweight="bold")
        ax.grid(axis="x", alpha=0.3)

        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor="#27ae60", label="破净 (PB < 1)"),
            Patch(facecolor="#3498db", label="低PB (1 ≤ PB < 2)"),
            Patch(facecolor="#95a5a6", label="PB ≥ 2"),
        ]
        ax.legend(handles=legend_elements, loc="lower right", fontsize=9)

        if save_path is None:
            save_path = _get_save_path("chart_bar.png")
        fig.tight_layout()
        fig.savefig(save_path, dpi=150)
        print(f"  ✓ 柱状图已保存：{save_path}")
        plt.close(fig)
    except Exception:
        print(f"  ✗ 柱状图生成失败：")
        traceback.print_exc()
        plt.close("all")


def generate_all_charts(result: pd.DataFrame):
    """生成全部图表"""
    print("[3/3] 正在生成可视化图表...")
    if result is None or result.empty:
        print("  [跳过] 没有数据可生成图表（请检查筛选条件是否过严）")
        return
    plot_pe_pb_scatter(result, top_n=30)
    plot_top_pe_bar(result, top_n=15)
    print("      所有图表生成完毕！")
