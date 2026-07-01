"""
数据获取模块：通过 efinance 接口拉取A股实时行情与估值指标
efinance 完全免费，无需注册，秒级出全市场数据
"""
import efinance as ef
import pandas as pd


def fetch_stock_data() -> pd.DataFrame:
    """
    获取A股全市场数据（含PE、市值、涨跌幅等）
    注意：efinance 不提供 PB（市净率），筛选时自动跳过 PB 条件
    """
    print("[1/3] 正在获取 A 股全市场实时数据...")
    df = ef.stock.get_realtime_quotes()

    if df is None or df.empty:
        raise RuntimeError("efinance 数据为空，请检查网络")

    print(f"      获取到 {len(df)} 只股票")

    # ---- 自动识别列名（efinance 版本不同列名可能微调） ----
    col_map = {}
    for col in df.columns:
        if col in ("股票代码", "代码"):
            col_map[col] = "code"
        elif col in ("股票名称", "名称"):
            col_map[col] = "name"
        elif col == "最新价":
            col_map[col] = "price"
        elif col == "涨跌幅":
            col_map[col] = "change_pct"
        elif "市盈率" in col:      # 匹配 "动态市盈率" / "市盈率(动态)" 等
            col_map[col] = "pe"
        elif "市净率" in col:
            col_map[col] = "pb"
        elif col == "总市值":
            col_map[col] = "market_cap"
        elif col == "换手率":
            col_map[col] = "turnover"

    df = df[list(col_map.keys())].copy()
    df.rename(columns=col_map, inplace=True)

    # 类型转换
    for col in ["price", "pe", "change_pct", "market_cap", "turnover"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 如果 efinance 有 PB 就用，没有则占位
    if "pb" not in df.columns:
        print("      注意：efinance 不含 PB 字段，将跳过 PB 筛选条件")
        df["pb"] = 1.0  # 占位值，确保代码不报错

    df["pb"] = pd.to_numeric(df["pb"], errors="coerce")
    df["market_cap"] = df["market_cap"] / 1e8  # 元 → 亿元

    # 清洗
    df = df.dropna(subset=["pe"])
    df = df[df["pe"] > 0]
    df = df[df["pb"] > 0]

    print(f"      有效数据：{len(df)} 只股票")
    return df
