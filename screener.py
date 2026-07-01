"""
筛选模块：基于 PE / PB / 市值筛选符合价值投资标准的股票
"""
import pandas as pd


def screen_stocks(df: pd.DataFrame,
                  pe_min: float = 0,
                  pe_max: float = 25,
                  pb_max: float = 2.5,
                  market_cap_min: float = 100) -> pd.DataFrame:
    """
    价值投资风格筛选：
    - PE 在 pe_min ~ pe_max 之间
    - PB ≤ pb_max（当数据源无 PB 时自动跳过）
    - 总市值 ≥ market_cap_min 亿元
    """
    print("[2/3] 正在按条件筛选...")

    cond = (
        (df["pe"] >= pe_min) &
        (df["pe"] <= pe_max)
    )

    # 检测 PB 是否为占位值（all ~1.0 说明数据源无 PB）
    has_real_pb = not (df["pb"].nunique() <= 2 and df["pb"].iloc[0] == 1.0)
    if has_real_pb:
        cond = cond & (df["pb"] <= pb_max)
        pb_str = f"PB ≤ {pb_max}"
    else:
        pb_str = "PB 跳过（数据源无此字段）"

    cond = cond & (df["market_cap"] >= market_cap_min)

    result = df[cond].copy()
    result = result.sort_values("pe")

    print(f"      筛选条件：0 < PE ≤ {pe_max}   |   {pb_str}   |   市值 ≥ {market_cap_min} 亿")
    print(f"      筛选结果：{len(result)} 只股票符合条件")

    return result


def show_top_stocks(result: pd.DataFrame, n: int = 20):
    """
    打印 Top N 结果摘要
    """
    cols = ["code", "name", "pe", "pb", "price", "market_cap"]
    has_real_pb = "pb" in result.columns and result["pb"].nunique() > 2

    display = result[cols].head(n).copy()
    for c in ["pe", "pb", "market_cap"]:
        display[c] = display[c].round(2)

    print("\n" + "=" * 75)
    header = f"  {'代码':<10} {'名称':<8} {'PE':>7} {'PB':>6} {'最新价':>7} {'市值(亿)':>10}"
    print(header)
    print("-" * 75)

    for _, row in display.iterrows():
        pb_display = f"{row['pb']:>6.2f}" if has_real_pb else "  N/A"
        print(f"  {row['code']:<10} {row['name']:<8} {row['pe']:>7.2f} {pb_display} "
              f"{row['price']:>7.2f} {row['market_cap']:>9.0f}")
    print("=" * 75)
