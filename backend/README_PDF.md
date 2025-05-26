# PDF渲染功能集成说明

本文档说明如何在RPA_uniapp项目中使用PDF渲染功能。

## 功能概述

PDF渲染功能已直接集成到后端应用程序中，无需运行单独的服务。主要功能包括：

1. 检查服务器是否支持PDF渲染
2. 获取PDF文件的元数据（页数、作者等）
3. 将PDF页面渲染为高质量图片
4. 支持缩放和页面选择
5. 提供示例PDF图片用于测试

## 安装依赖

确保已安装必要的Python依赖：

```bash
pip install -r requirements.txt
```

主要依赖包括：
- pymupdf：用于PDF处理和渲染
- pillow：图像处理库
- requests：HTTP请求库

## API接口

### 1. 检查渲染支持

```
GET /api/reports/check-rendering
```

返回服务器是否支持PDF渲染的信息。

### 2. 获取PDF元数据

```
GET /api/reports/pdf-metadata?url={pdf_url}
```

返回PDF文件的基本信息，包括页数、标题、作者等。

### 3. 渲染PDF页面

```
GET /api/reports/render-page?url={pdf_url}&page={page_number}&scale={scale_factor}
```

将指定的PDF页面渲染为图片并返回。

- `url`: PDF文件的URL
- `page`: 页码，从1开始（默认：1）
- `scale`: 缩放比例（默认：2.0）

### 4. 渲染PDF页面为Base64

```
GET /api/reports/render-page-base64?url={pdf_url}&page={page_number}&scale={scale_factor}
```

将指定的PDF页面渲染为Base64编码的图片，适用于直接在前端显示。

### 5. 获取示例图片

```
GET /api/common/sample-pdf-image
```

返回一个示例PDF图片，用于前端测试。

### 6. 增强的报告查看

现有的报告查看接口已经增强，支持将PDF渲染为图片：

```
GET /api/reports/view/{filename}?render=true&page={page_number}&scale={scale_factor}
```

- `render`: 设置为true时，返回渲染后的图片而不是PDF内容
- `page`: 页码，从1开始（默认：1）
- `scale`: 缩放比例（默认：2.0）

## 与前端集成

前端PDF查看器组件可以使用这些API端点进行集成：

```javascript
// 在pdf-viewer.vue中检查服务器是否支持渲染
const apiUrl = `${baseUrl}/api/reports/check-rendering`;

// 渲染PDF页面为图片
const renderUrl = `${baseUrl}/api/reports/render-page?url=${encodeURIComponent(pdfUrl)}&page=${currentPage}&scale=${scale}`;

// 或者使用Base64方式（适用于跨域情况）
const renderBase64Url = `${baseUrl}/api/reports/render-page-base64?url=${encodeURIComponent(pdfUrl)}&page=${currentPage}&scale=${scale}`;
```

## 性能考虑

- PDF渲染是CPU密集型操作，大型PDF文件可能需要更多资源
- 考虑添加缓存机制，避免重复渲染相同的页面
- 临时文件会保存在系统临时目录，服务不会自动清理这些文件 