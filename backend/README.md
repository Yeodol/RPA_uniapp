# RPA后端API服务

这是为RPA_uniapp项目提供数据服务的Flask后端API。

## 功能

- 提供数据记录查询API
- 提供数据记录删除API
- 提供API状态检查

## 安装

1. 安装Python 3.6+
2. 安装依赖包：

```bash
pip install -r requirements.txt
```

## 配置

### 配置文件

系统支持两种配置方式：配置文件和环境变量。配置文件优先级高于环境变量。

#### 配置文件 (config.json)

默认配置文件为项目根目录下的`config.json`，可以通过环境变量`CONFIG_PATH`修改路径。

```json
{
  "db_host": "localhost",  // 数据库主机地址
  "port": 5000,            // API服务端口
  "debug": false,          // 是否启用调试模式
  "allowed_origins": ["*"] // 允许的跨域来源
}
```

#### 环境变量

可以创建`.env`文件或直接在系统中设置以下环境变量：

- `DB_HOST`：数据库主机地址（默认：localhost）
- `PORT`：API服务端口（默认：5000）
- `DEBUG`：是否启用调试模式（默认：False）
- `API_VERSION`：API版本号（默认：1.0.0）
- `CONFIG_PATH`：配置文件路径（默认：config.json）

### 数据库表结构

默认表结构（data表）：

```sql
CREATE TABLE `data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `data_name` varchar(255) NOT NULL,
  `data_update` datetime NOT NULL,
  `data_content` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 运行

### 开发环境

```bash
python app.py
```

### 生产环境

推荐使用Gunicorn或uWSGI作为WSGI服务器：

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API文档

### 获取数据记录

**请求**：
- URL: `/api/data`
- 方法: `POST`
- 内容类型: `application/json`
- 请求体:
  ```json
  {
    "username": "数据库用户名",
    "password": "数据库密码",
    "database": "数据库名",
    "table": "表名（可选，默认为data）"
  }
  ```

**响应**：
- 成功: 记录数组
- 失败: 错误信息

### 删除数据记录

**请求**：
- URL: `/api/data/delete`
- 方法: `POST`
- 内容类型: `application/json`
- 请求体:
  ```json
  {
    "username": "数据库用户名",
    "password": "数据库密码",
    "database": "数据库名",
    "table": "表名（可选，默认为data）",
    "id": "要删除的记录ID"
  }
  ```

**响应**：
- 成功: `{"success": true, "message": "记录删除成功"}`
- 失败: 错误信息

### API状态检查

**请求**：
- URL: `/api/status`
- 方法: `GET`

**响应**：
```json
{
  "status": "running",
  "version": "1.0.0"
}
``` 