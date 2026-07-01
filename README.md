# A股财务数据筛选与可视化工具

基于 Python 的 A 股全市场价值投资筛选工具，一键拉取 5000+ 只股票实时数据，按 PE、PB、市值等条件筛选低估值标的，并生成可视化图表和 Excel 报告。

## 功能

- 📊 秒级获取 A 股全市场实时行情与估值数据（efinance）
- 🔍 按 PE（市盈率）、PB（市净率）、市值三维条件筛选
- 📈 生成 PE-PB 散点气泡图 + 低市盈率排名柱状图
- 📋 导出 Excel 筛选结果

## 快速开始

### 环境要求

- Python 3.8+
- Windows / macOS / Linux

### 安装依赖

```bash
pip install efinance pandas matplotlib openpyxl
```

### 运行

```bash
python main.py
```

### 输出文件

| 文件 | 说明 |
|------|------|
| `screening_result.xlsx` | 筛选结果 Excel 表格 |
| `chart_scatter.png` | PE-PB 散点气泡图 |
| `chart_bar.png` | 低市盈率排名柱状图 |

## 项目结构

```
stock-screener/
├── main.py           # 主程序入口
├── data_fetcher.py   # 数据获取（efinance）
├── screener.py       # 筛选逻辑
├── visualizer.py     # 可视化
├── diagnose.py       # 诊断脚本（排查环境问题）
└── README.md
```

## 筛选逻辑

默认条件：**PE ≤ 25、市值 ≥ 100 亿**（可自行在 `main.py` 中修改参数）

筛选出的股票按 PE 从低到高排列，典型结果为银行股等低估值蓝筹。

## 常见问题

- **数据获取失败**：efinance 依赖东方财富接口，如果网络不通请检查代理/防火墙设置
- **图表中文乱码**：已自动适配 Windows/macOS/Linux 中文字体
- **缺少 PB 字段**：efinance 当前版本不提供 PB，筛选时自动跳过

## 作者

罗展澎 — 山东大学物理学专业

## 协议

MIT License
