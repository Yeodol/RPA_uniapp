import mysql.connector
import os
from datetime import datetime
import argparse

# 解析命令行参数
parser = argparse.ArgumentParser(description='初始化RPA应用的数据库')
parser.add_argument('--host', default='localhost', help='数据库主机地址')
parser.add_argument('--user', required=True, help='数据库用户名')
parser.add_argument('--password', required=True, help='数据库密码')
parser.add_argument('--database', required=True, help='要创建的数据库名')
args = parser.parse_args()

# 连接到MySQL（不指定数据库）
conn = mysql.connector.connect(
    host=args.host,
    user=args.user,
    password=args.password
)

cursor = conn.cursor()

# 创建数据库（如果不存在）
print(f"创建数据库 {args.database}...")
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {args.database} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")

# 使用新创建的数据库
cursor.execute(f"USE {args.database}")

# 创建数据表
print("创建数据表...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS `data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `data_name` varchar(255) NOT NULL,
  `data_update` datetime NOT NULL,
  `data_content` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

# 插入示例数据
print("插入示例数据...")
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
example_data = [
    ('样品1分析结果', current_time, '样品1的详细数据内容...'),
    ('样品2分析结果', current_time, '样品2的详细数据内容...'),
    ('设备校准数据', current_time, '设备校准的详细参数数据...')
]

cursor.executemany(
    "INSERT INTO data (data_name, data_update, data_content) VALUES (%s, %s, %s)",
    example_data
)

# 提交更改
conn.commit()

print("数据库初始化完成！")

# 关闭连接
cursor.close()
conn.close() 