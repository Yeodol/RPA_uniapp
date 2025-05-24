<template>
  <view class="container">
    <view class="header">
      <text class="title">PDF报告查看器</text>
      <text class="subtitle">{{ filename }}</text>
    </view>
    
    <view class="pdf-container" v-if="pdfUrl && !showAlternative">
      <!-- 使用web-view组件加载PDF -->
      <web-view :src="pdfUrl" @error="handleWebViewError" @message="handleWebViewMessage"></web-view>
    </view>
    
    <!-- 备选PDF查看方式 -->
    <view class="alternative-container" v-if="showAlternative">
      <text class="alternative-title">无法直接显示PDF</text>
      <text class="alternative-text">您的设备可能不支持直接查看PDF，请尝试以下方式：</text>
      
      <view class="alternative-actions">
        <button class="action-button primary-button" @tap="downloadPdf">下载PDF文件</button>
        <button class="action-button" @tap="tryAlternativeViewer" v-if="!triedAlternative">尝试备选查看方式</button>
      </view>
      
      <text class="diagnostic-info">诊断信息：</text>
      <text class="diagnostic-detail">PDF大小: {{pdfSize}} KB</text>
      <text class="diagnostic-detail">设备: {{deviceInfo}}</text>
    </view>
    
    <view class="error-container" v-if="errorMessage">
      <text class="error-text">{{ errorMessage }}</text>
      <button class="action-button" @tap="downloadPdf">下载PDF</button>
    </view>
    
    <view class="loading-container" v-if="loading">
      <text class="loading-text">正在加载PDF...</text>
    </view>
    
    <view class="button-section">
      <button class="action-button primary-button" @tap="downloadPdf" v-if="!loading">下载PDF</button>
      <button class="back-button" @tap="goBack">返回列表</button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      filename: '',
      pdfUrl: '',
      pdfBase64: '',
      errorMessage: '',
      loading: true,
      showAlternative: false,
      triedAlternative: false,
      deviceInfo: '',
      pdfSize: 0,
      downloadUrl: ''
    }
  },
  
  onLoad(options) {
    if (options.pdf && options.filename) {
      try {
        // 获取设备信息
        const systemInfo = uni.getSystemInfoSync();
        this.deviceInfo = `${systemInfo.platform} ${systemInfo.system}`;
        
        this.filename = decodeURIComponent(options.filename);
        this.pdfBase64 = decodeURIComponent(options.pdf);
        this.pdfSize = Math.round(this.pdfBase64.length / 1024);
        
        // 如果传入了下载链接
        if (options.downloadUrl) {
          this.downloadUrl = decodeURIComponent(options.downloadUrl);
          console.log('获取到下载链接:', this.downloadUrl);
        }
        
        console.log(`PDF文件大小：${this.pdfSize}KB，设备信息：${this.deviceInfo}`);
        
        // 使用HTML包装PDF内容，增加兼容性
        const htmlContent = `
        <!DOCTYPE html>
        <html>
        <head>
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>${this.filename}</title>
          <style>
            body, html {
              margin: 0;
              padding: 0;
              height: 100%;
              width: 100%;
              overflow: hidden;
            }
            #pdf-container {
              width: 100%;
              height: 100%;
            }
            embed, object, iframe {
              width: 100%;
              height: 100%;
              border: none;
            }
          </style>
        </head>
        <body>
          <div id="pdf-container">
            <!-- 尝试多种方式嵌入PDF -->
            <object data="data:application/pdf;base64,${this.pdfBase64}" type="application/pdf" width="100%" height="100%">
              <embed src="data:application/pdf;base64,${this.pdfBase64}" type="application/pdf" width="100%" height="100%">
                <p>您的浏览器不支持PDF查看，<a href="#" id="download-link">点击下载</a></p>
                <script>
                  document.getElementById('download-link').addEventListener('click', function() {
                    // 通知应用下载PDF
                    window.parent.postMessage({action: 'download'}, '*');
                  });
                  
                  // 通知应用PDF已加载
                  window.parent.postMessage({action: 'loaded'}, '*');
                  
                  // 30秒后检查是否显示成功
                  setTimeout(function() {
                    window.parent.postMessage({action: 'checkDisplay'}, '*');
                  }, 30000);
                </script>
              </embed>
            </object>
          </div>
        </body>
        </html>
        `;
        
        // 创建HTML内容的Data URL
        this.pdfUrl = `data:text/html;charset=utf-8,${encodeURIComponent(htmlContent)}`;
        console.log('HTML包装的PDF URL创建成功');
        
        // 6秒后如果仍在加载，显示备选方案
        setTimeout(() => {
          if (this.loading) {
            console.log('PDF加载超时，显示备选方案');
            this.loading = false;
            this.showAlternative = true;
          }
        }, 6000);
      } catch (error) {
        console.error('处理PDF数据时出错:', error);
        this.errorMessage = '无法处理PDF数据: ' + error.message;
        this.loading = false;
        this.showAlternative = true;
      }
    } else {
      this.errorMessage = '未提供PDF数据或文件名';
      this.loading = false;
      this.showAlternative = true;
    }
  },
  
  methods: {
    handleWebViewError(error) {
      console.error('Web视图加载错误:', error);
      this.errorMessage = '加载PDF失败，请尝试下载查看';
      this.loading = false;
      this.showAlternative = true;
    },
    
    handleWebViewMessage(event) {
      console.log('收到Web视图消息:', event.detail.data);
      try {
        const message = event.detail.data;
        if (message.action === 'loaded') {
          console.log('PDF已在Web视图中加载');
          this.loading = false;
        } else if (message.action === 'download') {
          this.downloadPdf();
        } else if (message.action === 'checkDisplay') {
          // 检查是否需要显示备选方案
          if (this.loading) {
            console.log('PDF可能未正确显示，提供备选方案');
            this.loading = false;
            this.showAlternative = true;
          }
        }
      } catch (e) {
        console.error('处理Web视图消息错误:', e);
      }
    },
    
    tryAlternativeViewer() {
      this.triedAlternative = true;
      this.showAlternative = false;
      
      // 使用简单的iframe方式
      const simpleHtml = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${this.filename}</title>
        <style>
          body, html { margin: 0; padding: 0; height: 100%; width: 100%; }
          iframe { width: 100%; height: 100%; border: none; }
        </style>
      </head>
      <body>
        <iframe src="data:application/pdf;base64,${this.pdfBase64}" type="application/pdf" width="100%" height="100%"></iframe>
      </body>
      </html>
      `;
      
      this.pdfUrl = `data:text/html;charset=utf-8,${encodeURIComponent(simpleHtml)}`;
      console.log('尝试备选PDF查看方式');
      
      // 5秒后再次检查
      setTimeout(() => {
        if (!this.showAlternative) {
          this.showAlternative = true;
        }
      }, 5000);
    },
    
    downloadPdf() {
      if (!this.pdfBase64 && !this.downloadUrl) {
        uni.showToast({
          title: '没有可下载的PDF数据',
          icon: 'none'
        });
        return;
      }
      
      console.log('准备下载PDF文件');
      
      // 检查平台类型
      const systemInfo = uni.getSystemInfoSync();
      
      // 如果有下载链接且不是小程序环境，优先使用直接下载
      if (this.downloadUrl && systemInfo.platform !== 'mp-weixin' && systemInfo.platform !== 'mp-alipay') {
        console.log('使用直接下载链接:', this.downloadUrl);
        
        // 构建完整URL（需要添加域名前缀）
        const baseUrl = this.downloadUrl.startsWith('http') ? '' : import.meta.env.VITE_API_BASE_URL || 'http://1.95.90.167:5032';
        const fullUrl = this.downloadUrl.startsWith('http') ? this.downloadUrl : `${baseUrl}${this.downloadUrl}`;
        
        if (systemInfo.platform === 'android' || systemInfo.platform === 'ios') {
          // 移动端 - 使用系统下载能力
          plus.runtime.openURL(fullUrl);
        } else {
          // H5端 - 创建隐藏的a标签下载
          const link = document.createElement('a');
          link.href = fullUrl;
          link.target = '_blank';
          link.download = this.filename;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        }
        
        uni.showToast({
          title: '文件下载中',
          icon: 'success'
        });
        return;
      }
      
      // 以下是原有代码，当没有直接下载链接时使用
      
      if (!this.pdfBase64) {
        uni.showToast({
          title: '没有可下载的PDF数据',
          icon: 'none'
        });
        return;
      }
      
      console.log('准备下载PDF文件');
      
      // 检查平台类型
      const systemInfo = uni.getSystemInfoSync();
      
      if (systemInfo.platform === 'android' || systemInfo.platform === 'ios') {
        // 移动端处理
        // 转换base64为ArrayBuffer
        try {
          const binary = atob(this.pdfBase64);
          const array = new Uint8Array(binary.length);
          for (let i = 0; i < binary.length; i++) {
            array[i] = binary.charCodeAt(i);
          }
          
          // 保存文件到本地
          const filePath = `${uni.env.USER_DATA_PATH}/${this.filename}`;
          
          // 写入文件
          uni.getFileSystemManager().writeFile({
            filePath: filePath,
            data: array.buffer,
            success: () => {
              console.log('文件写入成功:', filePath);
              
              // 打开文件
              uni.openDocument({
                filePath: filePath,
                showMenu: true,
                success: () => {
                  console.log('打开文档成功');
                  uni.showToast({
                    title: '打开文档成功',
                    icon: 'success'
                  });
                },
                fail: (err) => {
                  console.error('打开文档失败:', err);
                  uni.showToast({
                    title: '打开文档失败，请使用其他应用查看',
                    icon: 'none'
                  });
                }
              });
            },
            fail: (err) => {
              console.error('文件写入失败:', err);
              uni.showToast({
                title: '保存文件失败',
                icon: 'none'
              });
            }
          });
        } catch (e) {
          console.error('处理PDF数据出错:', e);
          uni.showToast({
            title: '处理PDF数据失败',
            icon: 'none'
          });
        }
      } else {
        // 网页端处理
        try {
          // 转换base64为二进制数据
          const binary = atob(this.pdfBase64);
          const array = new Uint8Array(binary.length);
          for (let i = 0; i < binary.length; i++) {
            array[i] = binary.charCodeAt(i);
          }
          
          // 创建Blob对象
          const blob = new Blob([array], { type: 'application/pdf' });
          
          // 创建下载链接
          const link = document.createElement('a');
          link.href = URL.createObjectURL(blob);
          link.download = this.filename;
          link.click();
          
          // 释放URL对象
          URL.revokeObjectURL(link.href);
          
          uni.showToast({
            title: '文件下载中',
            icon: 'success'
          });
        } catch (e) {
          console.error('下载文件失败:', e);
          uni.showToast({
            title: '下载失败',
            icon: 'none'
          });
        }
      }
    },
    
    goBack() {
      uni.navigateBack();
    }
  }
}
</script>

<style>
.container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f5f5;
}

.header {
  padding: 20rpx;
  background-color: #ffffff;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.1);
  z-index: 10;
}

.title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  display: block;
  text-align: center;
}

.subtitle {
  font-size: 28rpx;
  color: #666;
  margin-top: 10rpx;
  display: block;
  text-align: center;
}

.pdf-container {
  flex: 1;
  width: 100%;
  height: calc(100vh - 180rpx);
}

.error-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40rpx;
}

.error-text {
  font-size: 28rpx;
  color: #ff4d4f;
  text-align: center;
  margin-bottom: 30rpx;
}

.loading-container {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255,255,255,0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
}

.loading-text {
  font-size: 32rpx;
  color: #333;
}

.button-section {
  padding: 20rpx;
  background-color: #ffffff;
  box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.1);
}

.back-button {
  background-color: #2871FA;
  color: #fff;
  border: none;
  border-radius: 8rpx;
  padding: 0;
  font-size: 28rpx;
  height: 80rpx;
  line-height: 80rpx;
  display: flex;
  justify-content: center;
  align-items: center;
}

.action-button {
  background-color: #1890FF;
  color: #fff;
  border: none;
  border-radius: 8rpx;
  font-size: 28rpx;
  height: 80rpx;
  line-height: 80rpx;
  padding: 0 30rpx;
  margin: 20rpx 0;
}

.alternative-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40rpx;
  background-color: #f9f9f9;
  border-radius: 10rpx;
  margin: 20rpx;
}

.alternative-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
}

.alternative-text {
  font-size: 28rpx;
  color: #666;
  margin-bottom: 30rpx;
  text-align: center;
}

.alternative-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 30rpx;
}

.primary-button {
  background-color: #2871FA;
  color: #fff;
  border: none;
  border-radius: 8rpx;
  padding: 0;
  font-size: 28rpx;
  height: 80rpx;
  line-height: 80rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 20rpx;
}

.diagnostic-info {
  font-size: 28rpx;
  color: #666;
  margin-top: 20rpx;
  margin-bottom: 10rpx;
  align-self: flex-start;
}

.diagnostic-detail {
  font-size: 24rpx;
  color: #999;
  margin-bottom: 5rpx;
  align-self: flex-start;
  padding-left: 20rpx;
}
</style> 