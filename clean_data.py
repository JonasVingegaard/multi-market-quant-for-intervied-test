"""
数据清洗：Pandas 完成核心操作
- 去重
- 缺失值填充（前向填充）
- 时间索引标准化
- 剔除无效价格（≤0）
- 输出对齐后的宽表
"""
import pandas as pd
import os

RAW_DIR = "raw_data"
OUTPUT_DIR = "cleaned_data"
OUTPUT_FILE = "aligned_prices.csv"

TICKER_FILES = {
    "sp500": "^GSPC",
    "hsi": "^HSI",
    "btc": "BTC-USD",
}



def load_and_clean(filepath, col_name):
    df = pd.read_csv(filepath, index_col=0, parse_dates=True)

    df = df.copy()

    if "Close" in df.columns:
        df = df[["Close"]].rename(columns={"Close": col_name})
    elif "Adj Close" in df.columns:
        df = df[["Adj Close"]].rename(columns={"Adj Close": col_name})
    else:
        raise KeyError(f"文件 {filepath} 中未找到 Close 或 Adj Close 列")

    df.index = pd.to_datetime(df.index)
    df.index.name = "Date"

    df = df[~df.index.duplicated(keep="first")]

    df = df.sort_index()

    df = df.asfreq("B")

    df[col_name] = df[col_name].ffill()

    df = df[df[col_name] > 0]

    return df


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    dfs = []
    for file_key, col_name in TICKER_FILES.items():
        filepath = os.path.join(RAW_DIR, f"{file_key}.csv")
        if not os.path.exists(filepath):
            print(f"警告: {filepath} 不存在，跳过")
            continue

        print(f"正在清洗 {filepath} ...")
        df_clean = load_and_clean(filepath, col_name)
        print(f"  清洗后: {len(df_clean)} 行")
        dfs.append(df_clean)

    if not dfs:
        print("没有可清洗的数据文件，请先运行 fetch_data.py")
        return

    merged = dfs[0]
    for df in dfs[1:]:
        merged = merged.join(df, how="inner")

    merged = merged.dropna()

    print(f"\n对齐后宽表: {len(merged)} 行, {len(merged.columns)} 列")
    print(f"日期范围: {merged.index.min().date()} ~ {merged.index.max().date()}")
    print(f"列名: {list(merged.columns)}")

    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    merged.to_csv(output_path)
    print(f"\n已保存清洗后宽表至: {output_path}")

    print("\n数据预览:")
    print(merged.head(10))


if __name__ == "__main__":
    main()