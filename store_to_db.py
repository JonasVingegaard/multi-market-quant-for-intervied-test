"""
数据库存储：将清洗后数据存入 PostgreSQL
"""
import pandas as pd
from sqlalchemy import create_engine
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DB_CONFIG = {
    "host": os.getenv("PG_HOST", "localhost"),
    "port": int(os.getenv("PG_PORT", "5432")),
    "database": os.getenv("PG_DATABASE", "fin_data"),
    "user": os.getenv("PG_USER", "gunter"),
    "password": os.getenv("PG_PASSWORD", ""),
}

TABLE_NAME = "aligned_prices"
CLEANED_FILE = os.path.join("cleaned_data", "aligned_prices.csv")


def get_engine():
    url = (
        f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )
    return create_engine(url)


def main():
    if not os.path.exists(CLEANED_FILE):
        print(f"错误: {CLEANED_FILE} 不存在，请先运行 clean_data.py")
        return

    print(f"正在读取 {CLEANED_FILE} ...")
    df = pd.read_csv(CLEANED_FILE, index_col=0, parse_dates=True)
    df.index.name = "Date"
    print(f"读取到 {len(df)} 行, {len(df.columns)} 列")

    print("正在连接 PostgreSQL ...")
    try:
        engine = get_engine()
        with engine.connect() as conn:
            print("数据库连接成功！")
    except Exception as e:
        print(f"数据库连接失败: {e}")
        print("\n请确保:")
        print("  1. PostgreSQL 已启动: sudo systemctl start postgresql")
        print("  2. 数据库和用户已创建")
        print("  3. store_to_db.py 中的 DB_CONFIG 密码正确")
        return

    print(f"正在写入表 {TABLE_NAME} ...")
    df.to_sql(
        TABLE_NAME,
        engine,
        if_exists="replace",
        index=True,
        index_label="Date",
    )
    print(f"写入完成！共 {len(df)} 行数据已存入表 {TABLE_NAME}")

    print("\n验证读取:")
    verify_df = pd.read_sql(f"SELECT * FROM {TABLE_NAME} LIMIT 5", engine)
    print(verify_df)


if __name__ == "__main__":
    main()