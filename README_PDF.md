# PDF渲染服务集成说明

## 功能概述

PDF渲染功能已从独立服务迁移到主后端服务中。现在所有PDF相关的API都通过主后端服务提供，不再需要单独运行PDF渲染服务。

## 配置变更

所有PDF查看器组件已更新，现在统一使用`config/config.js`中配置的API地址：

```js
apiBaseUrl: 'http://1.95.90.167:5032'
```

## API端点

PDF渲染相关的API端点包括：

- `/api/reports/check-rendering` - 检查PDF渲染服务状态
- `/api/reports/pdf-metadata` - 获取PDF元数据（页数等）
- `/api/reports/render-page` - 渲染指定页面为图片
- `/api/common/sample-pdf-image` - 获取示例PDF图片

## 注意事项

1. 不再需要启动独立的PDF渲染服务
2. PDF查看器组件将自动使用全局配置的API地址
3. 如需更改API地址，只需修改`config/config.js`中的`apiBaseUrl` 