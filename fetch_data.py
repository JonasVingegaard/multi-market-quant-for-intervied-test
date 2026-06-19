"""
数据获取：用 yfinance 获取近 10 年三类资产日度收盘价
标普500 (^GSPC)、恒生指数 (^HSI)、比特币 (BTC-USD)
保存为 3 个独立的 CSV 文件
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

TICKERS = {
    "^GSPC": "sp500",
    "^HSI": "hsi",
    "BTC-USD": "btc",
}

START_DATE = (datetime.now() - timedelta(days=365 * 10)).strftime("%Y-%m-%d")
END_DATE = datetime.now().strftime("%Y-%m-%d")

OUTPUT_DIR = "raw_data"


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for ticker, name in TICKERS.items():
        print(f"正在下载 {ticker} 近 10 年数据...")

        df = yf.download(
            ticker,
            start=START_DATE,
            end=END_DATE,
            auto_adjust=True,
            progress=False,
        )

        if df.empty:
            print(f"  警告: {ticker} 未获取到数据，跳过")
            continue

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(-1)

        csv_path = os.path.join(OUTPUT_DIR, f"{name}.csv")
        df.to_csv(csv_path)
        print(f"  已保存 {csv_path}, 共 {len(df)} 行")


if __name__ == "__main__":
    main()