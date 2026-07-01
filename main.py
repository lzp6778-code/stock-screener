"""
A股财务数据筛选与可视化工具
===========================
功能：通过 efinance 拉取A股全市场估值与行情数据，按价值投资条件
      （低PE、低PB、合理市值）筛选优质标的，输出排名、图表和 Excel。

使用：
    python main.py

依赖：
    pip install efinance pandas matplotlib openpyxl

作者：罗展澎
日期：2026-07
"""

import os
import sys

# 确保所有输出文件保存到脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
from data_fetcher import fetch_stock_data
from screener import screen_stocks, show_top_stocks
from visualizer import generate_all_charts


def main():
    print("=" * 60)
    print("   A 股财务数据筛选与可视化工具 v2.1")
    print("   Stock Screener & Visualizer (efinance)")
    print("=" * 60)

    # ---- 1. 获取 & 清洗数据 ----
    df = fetch_stock_data()

    # ---- 2. 按价值条件筛选 ----
    # efinance 有市值数据，恢复完整的 PE + PB + 市值三维筛选
    result = screen_stocks(
        df,
        pe_min=0,           # PE > 0（排除亏损股）
        pe_max=25,          # PE ≤ 25
        pb_max=2.5,         # PB ≤ 2.5（efinance 无 PB 时自动跳过）
        market_cap_min=100  # 市值 ≥ 100 亿
    )

    # ---- 3. 打印排名 ----
    show_top_stocks(result, n=20)

    # ---- 4. 生成图表 ----
    generate_all_charts(result)

    # ---- 5. 导出 Excel ----
    excel_path = os.path.join(os.getcwd(), "screening_result.xlsx")
    export_cols = ["code", "name", "pe", "pb", "market_cap", "price",
                   "change_pct", "turnover"]
    result[export_cols].to_excel(excel_path, index=False, engine="openpyxl")
    print(f"\n✅ 筛选结果已导出至：screening_result.xlsx")
    print(f"   共 {len(result)} 只股票符合条件")
    print("=" * 60)


if __name__ == "__main__":
    main()
