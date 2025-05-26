<template>
  <view class="container">
    <view class="header">
      <text class="title">检测报告查看</text>
      <view class="subtitle-container">
        <text class="subtitle-label">当前文件：</text>
        <text class="subtitle">{{ filename }}</text>
      </view>
    </view>
    
    <!-- PDF图片查看区域 -->
    <view class="pdf-image-container" v-if="!loading && !errorMessage && !showAlternative">
      <view class="page-controls">
        <button class="page-button zoom-button" @tap="fitScreen">适配屏幕</button>
        <text class="page-info">共{{ totalPages }}页</text>
        <button class="page-button zoom-button" @tap="originalSize">原始文件</button>
      </view>
      
      <scroll-view class="image-scroll" scroll-y="true" scroll-x="true" :style="{ height: scrollHeight + 'px' }">
        <!-- 显示所有页面 -->
        <view class="all-pages-container">
          <view v-for="(pageUrl, index) in allPagesImageUrls" :key="index" class="page-wrapper">
            <image 
              :src="pageUrl" 
              class="pdf-image" 
              :style="imageStyle"
              @load="handleImageLoaded"
              @error="handleImageError"
              mode="widthFix"
            ></image>
            <view class="page-separator" v-if="index < allPagesImageUrls.length - 1"></view>
          </view>
          
          <view v-if="allPagesImageUrls.length === 0" class="image-placeholder">
            <text>加载页面中...</text>
          </view>
        </view>
      </scroll-view>
    </view>
    
    <!-- 备选方案 -->
    <view class="alternative-container" v-if="showAlternative">
      <text class="alternative-title">无法渲染PDF</text>
      <text class="alternative-text">请选择以下方式查看文件：</text>
      
      <view class="alternative-actions">
        <view class="button-wrapper">
          <button class="action-button primary-button" @tap="downloadPdf">
            <text class="button-icon">📥</text>
            <text class="button-text">下载PDF</text>
          </button>
        </view>
        
        <view class="button-wrapper" v-if="downloadUrl">
          <button class="action-button browser-button" @tap="openInSystemBrowser">
            <text class="button-icon">🌐</text>
            <text class="button-text">浏览器打开</text>
          </button>
        </view>
        
        <view class="button-wrapper" v-if="downloadUrl">
          <button class="action-button share-button" @tap="openWithThirdParty">
            <text class="button-icon">🔄</text>
            <text class="button-text">分享到应用</text>
          </button>
        </view>
        
        <view class="button-wrapper" v-if="canRetry">
          <button class="action-button retry-button" @tap="retryLoad">
            <text class="button-icon">🔄</text>
            <text class="button-text">重试加载</text>
          </button>
        </view>
      </view>
      
      <view class="divider"></view>
      
      <view class="diagnostic-section" @tap="toggleDiagnostic">
        <text class="diagnostic-title">诊断信息 {{ showDiagnostic ? '▼' : '▶' }}</text>
        <view class="diagnostic-details" v-if="showDiagnostic">
          <text class="diagnostic-item">PDF大小: {{pdfSize}} KB</text>
          <text class="diagnostic-item">设备: {{deviceInfo}}</text>
          <text class="diagnostic-item">错误: {{errorMessage || '未知错误'}}</text>
        </view>
      </view>
    </view>
    
    <!-- 错误提示区域 -->
    <view class="error-container" v-if="errorMessage && !showAlternative">
      <text class="error-text">{{ errorMessage }}</text>
      <button class="action-button" @tap="downloadPdf">下载PDF</button>
      <button class="action-button" @tap="showAlternativeOptions">查看其他选项</button>
    </view>
    
    <!-- 加载状态显示 -->
    <view class="loading-container" v-if="loading">
      <view class="loader"></view>
      <text class="loading-text">正在加载PDF...</text>
    </view>
    
    <!-- 底部按钮区域 -->
    <view class="button-section">
      <view class="button-row">
        <button class="action-button primary-button" @tap="downloadPdf" v-if="!loading">下载</button>
        <button class="action-button delete-button" @tap="showDeleteConfirm" v-if="!loading">删除</button>
      </view>
      <button class="back-button" @tap="goBack">返回列表</button>
    </view>
    
    <!-- 删除确认弹窗 -->
    <view class="modal-overlay" v-if="showDeleteModal" @tap="cancelDelete">
      <view class="modal-content" @tap.stop>
        <view class="modal-header">
          <text class="modal-title">确认删除</text>
        </view>
        <view class="modal-body">
          <text class="modal-text">确定要删除此报告吗？此操作不可恢复。</text>
          <text class="modal-filename">{{ filename }}</text>
        </view>
        <view class="modal-footer">
          <button class="modal-button cancel-button" @tap="cancelDelete">取消</button>
          <button class="modal-button confirm-button" @tap="confirmDelete">确认删除</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import config from '../config/config.js'  // 导入全局配置

export default {
  data() {
    return {
      filename: '',
      pdfBase64: '',
      downloadUrl: '',
      errorMessage: '',
      loading: true,
      showAlternative: false,
      deviceInfo: '',
      pdfSize: 0,
      
      // 图片查看相关
      currentPage: 1,
      totalPages: 0,
      pageImageUrls: [],
      currentPageImageUrl: '',
      allPagesImageUrls: [], // 存储所有页面的图片URL
      scale: 1.0,
      baseImageWidth: 0,
      baseImageHeight: 0,
      imageWidth: 0,
      imageHeight: 0,
      scrollHeight: 0,
      screenWidth: 0, // 添加屏幕宽度属性
      isLoadingAllPages: false,
      isOriginalSize: false, // 控制是否显示原始尺寸
      
      // 其他控制
      canRetry: true,
      retryCount: 0,
      showDiagnostic: false,
      isServerSideRendering: false,
      apiBaseUrl: '', // 存储API基础URL
      
      // 删除相关
      showDeleteModal: false,
      reportId: '', // 存储报告ID，用于删除
      isDeleting: false,
      failedImagesCount: 0,
      loadingTimeout: null
    }
  },
  
  computed: {
    // 计算图片样式，实现自适应
    imageStyle() {
      // 如果是原始尺寸
      if (this.isOriginalSize) {
        // 使用基础尺寸或默认值
        let width = this.baseImageWidth || this.screenWidth;
        let height = 'auto';
        
        return {
          width: width + 'px',
          maxWidth: 'none', // 允许超出屏幕宽度
          height: height
        };
      } else {
        // 计算图片的宽度和高度，适配屏幕
        let width = this.screenWidth * 0.95; // 使用屏幕宽度的95%作为基础宽度
        
        // 如果设置了基础尺寸，则保持宽高比
        let height = 'auto';
        if (this.baseImageWidth && this.baseImageHeight) {
          const ratio = this.baseImageHeight / this.baseImageWidth;
          height = width * ratio + 'px';
        }
        
        return {
          width: width + 'px',
          maxWidth: '100%',
          height: height
        };
      }
    }
  },
  
  onLoad(options) {
    if (options.pdf && options.filename) {
      try {
        // 获取设备信息
        const sysInfo = uni.getSystemInfoSync();
        this.deviceInfo = `${sysInfo.platform} ${sysInfo.system}`;
        
        // 保存屏幕宽度
        this.screenWidth = sysInfo.windowWidth;
        console.log('屏幕宽度:', this.screenWidth);
        
        // 从配置中获取API基础URL
        this.apiBaseUrl = config.apiBaseUrl;
        console.log('从配置获取API地址:', this.apiBaseUrl);
        
        this.filename = decodeURIComponent(options.filename);
        this.pdfBase64 = decodeURIComponent(options.pdf);
        this.pdfSize = Math.round(this.pdfBase64.length / 1024);
        
        // 如果传入了报告ID，保存用于删除操作
        if (options.reportId) {
          this.reportId = decodeURIComponent(options.reportId);
          console.log('获取到报告ID:', this.reportId);
        }
        
        // 设置屏幕高度
        this.scrollHeight = sysInfo.windowHeight - 180; // 减去头部和底部高度
        
        // 如果传入了下载链接
        if (options.downloadUrl) {
          this.downloadUrl = decodeURIComponent(options.downloadUrl);
          console.log('获取到下载链接:', this.downloadUrl);
        }
        
        console.log(`PDF文件大小：${this.pdfSize}KB，设备信息：${this.deviceInfo}`);
        
        // 检查服务器是否支持PDF渲染
        this.checkServerRendering();
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
    // 检查服务器是否支持PDF渲染
    checkServerRendering() {
      if (!this.downloadUrl) {
        // 如果没有下载链接，无法使用服务端渲染
        console.log('没有下载链接，尝试本地渲染PDF');
        this.requestPdfImages();
        return;
      }
      
      // 构建PDF服务API URL - 使用全局配置的API地址
      const apiUrl = `${this.apiBaseUrl}/api/reports/check-rendering`;
      
      console.log('检查PDF渲染服务:', apiUrl);
      
      uni.request({
        url: apiUrl,
        method: 'GET',
        success: (res) => {
          if (res.statusCode === 200 && res.data && res.data.supported) {
            console.log('PDF服务支持渲染，使用服务端渲染');
            this.isServerSideRendering = true;
            this.requestPdfImages();
          } else {
            console.log('PDF服务不支持渲染，尝试本地渲染');
            this.requestPdfImages();
          }
        },
        fail: (err) => {
          console.error('连接PDF服务失败:', err);
          console.log('尝试本地渲染');
          this.requestPdfImages();
        }
      });
    },
    
    // 请求PDF图片
    requestPdfImages() {
      if (this.isServerSideRendering) {
        this.requestServerRenderedImages();
      } else {
        this.fetchPdfMetadata();
      }
    },
    
    // 请求服务器渲染的PDF图片
    requestServerRenderedImages() {
      if (!this.downloadUrl) {
        this.errorMessage = '没有可用的PDF下载链接';
        this.loading = false;
        this.showAlternative = true;
        return;
      }
      
      // 使用全局配置的API地址
      const baseUrl = this.downloadUrl.startsWith('http') ? '' : this.apiBaseUrl;
      const pdfUrl = this.downloadUrl.startsWith('http') ? this.downloadUrl : `${baseUrl}${this.downloadUrl}`;
      const encodedPdfUrl = encodeURIComponent(pdfUrl);
      
      // 获取PDF元数据
      const metadataUrl = `${this.apiBaseUrl}/api/reports/pdf-metadata?url=${encodedPdfUrl}`;
      
      console.log('请求PDF元数据:', metadataUrl);
      
      uni.request({
        url: metadataUrl,
        method: 'GET',
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            this.totalPages = res.data.pageCount || 0;
            console.log(`PDF共${this.totalPages}页`);
            
            if (this.totalPages > 0) {
              // 加载所有页面
              this.loadAllPages(encodedPdfUrl);
            } else {
              this.errorMessage = 'PDF页数为0或无法解析';
              this.loading = false;
              this.showAlternative = true;
            }
          } else {
            console.error('获取PDF元数据失败:', res);
            this.errorMessage = '无法获取PDF元数据';
            this.loading = false;
            this.showAlternative = true;
          }
        },
        fail: (err) => {
          console.error('获取PDF元数据请求失败:', err);
          this.errorMessage = '获取PDF元数据失败';
          this.loading = false;
          this.showAlternative = true;
        }
      });
    },
    
    // 新增方法：加载所有页面，带缩放参数
    loadAllPages(encodedPdfUrl, scaleOverride) {
      this.isLoadingAllPages = true;
      this.allPagesImageUrls = [];
      this.failedImagesCount = 0; // 重置失败计数
      
      console.log(`开始加载所有${this.totalPages}页`);
      
      // 创建一个加载进度提示
      uni.showLoading({
        title: `加载中 (0/${this.totalPages}页)`,
        mask: true
      });
      
      // 设置加载超时保护
      clearTimeout(this.loadingTimeout);
      this.loadingTimeout = setTimeout(() => {
        console.error('加载PDF超时');
        this.loading = false;
        this.isLoadingAllPages = false;
        uni.hideLoading();
        
        // 超时时自动清除缓存重试一次
        if (this.retryCount < 2) {
          this.retryCount++;
          uni.showToast({
            title: '加载超时，自动重试',
            icon: 'none',
            duration: 2000
          });
          
          setTimeout(() => {
            this.clearCache(true);
            this.requestPdfImages();
          }, 1500);
        } else {
          uni.showToast({
            title: '加载超时，请重试',
            icon: 'none',
            duration: 3000
          });
          this.showAlternative = true;
        }
      }, 30000); // 30秒超时
      
      // 使用Promise.all并发加载所有页面
      const maxConcurrent = 2; // 减小并发数，避免头部过大
      
      // 先一次性生成所有图片URL，使用传入的缩放比例或默认的比例
      const scaleToUse = scaleOverride || (this.isOriginalSize ? 2.0 : this.scale * 2);
      const imageUrls = [];
      for (let i = 1; i <= this.totalPages; i++) {
        // 修改URL参数，减少可能的请求头大小
        const imageUrl = `${this.apiBaseUrl}/api/reports/render-page-lite?url=${encodedPdfUrl}&page=${i}&scale=${scaleToUse}`;
        imageUrls.push(imageUrl);
      }
      
      // 使用队列控制并发
      const loadQueue = async () => {
        const loadBatch = async (startIdx) => {
          const endIdx = Math.min(startIdx + maxConcurrent, this.totalPages);
          const batchPromises = [];
          
          for (let i = startIdx; i < endIdx; i++) {
            const pageNum = i + 1;
            batchPromises.push(this.loadPagePromise(imageUrls[i], pageNum));
          }
          
          try {
            // 等待当前批次完成
            const results = await Promise.all(batchPromises);
            
            // 更新加载进度
            results.forEach((result, idx) => {
              if (result.success) {
                this.allPagesImageUrls[startIdx + idx] = result.url;
              }
            });
            
            // 更新加载进度UI
            const loadedCount = Math.min(endIdx, this.totalPages);
            uni.showLoading({
              title: `加载中 (${loadedCount}/${this.totalPages}页)`,
              mask: true
            });
            
            // 如果还有更多页面，继续加载下一批
            if (endIdx < this.totalPages) {
              await loadBatch(endIdx);
            }
          } catch (error) {
            console.error('批次加载失败:', error);
            throw error;
          }
        };
        
        // 开始加载第一批
        await loadBatch(0);
      };
      
      // 执行加载队列
      loadQueue().then(() => {
        console.log('所有页面加载完成');
        this.loading = false;
        this.isLoadingAllPages = false;
        clearTimeout(this.loadingTimeout);
        uni.hideLoading();
      }).catch(error => {
        console.error('加载页面时出错:', error);
        this.errorMessage = '加载页面时出错';
        this.loading = false;
        this.isLoadingAllPages = false;
        clearTimeout(this.loadingTimeout);
        uni.hideLoading();
        
        // 自动重试
        if (this.retryCount < 2) {
          uni.showToast({
            title: '加载失败，自动重试',
            icon: 'none',
            duration: 1500
          });
          
          // 延迟后清除缓存并重试
          setTimeout(() => {
            this.clearCache(true);
            this.retryLoad(true);
          }, 1500);
        } else {
          this.showAlternative = true;
        }
      });
    },
    
    // 加载单个页面的Promise
    loadPagePromise(imageUrl, pageNum) {
      return new Promise((resolve) => {
        console.log(`加载第${pageNum}页:`, imageUrl);
        
        // 直接返回URL，交给图片组件去加载
        resolve({
          success: true,
          url: imageUrl,
          page: pageNum
        });
      });
    },
    
    // 获取PDF元数据（本地渲染时）
    fetchPdfMetadata() {
      if (!this.downloadUrl) {
        this.errorMessage = '没有可用的PDF下载链接';
        this.loading = false;
        this.showAlternative = true;
        return;
      }
      
      // 构建完整URL
      const baseUrl = this.downloadUrl.startsWith('http') ? '' : this.apiBaseUrl;
      const fullUrl = this.downloadUrl.startsWith('http') ? this.downloadUrl : `${baseUrl}${this.downloadUrl}`;
      
      // 使用下载链接获取文件
      uni.downloadFile({
        url: fullUrl,
        success: (res) => {
          if (res.statusCode === 200) {
            // 获取本地临时文件路径
            const filePath = res.tempFilePath;
            console.log('PDF文件下载成功，临时路径:', filePath);
            
            // 这里调用将PDF转换为图片的方法
            this.convertPdfToImages(filePath);
          } else {
            console.error('下载PDF文件失败:', res);
            this.errorMessage = '下载PDF文件失败';
            this.loading = false;
            this.showAlternative = true;
          }
        },
        fail: (err) => {
          console.error('下载PDF文件请求失败:', err);
          this.errorMessage = '下载PDF文件请求失败';
          this.loading = false;
          this.showAlternative = true;
        }
      });
    },
    
    // 将PDF转换为图片（这里需要根据平台实现）
    convertPdfToImages(pdfPath) {
      // 由于前端无法直接将PDF转换为图片，我们使用测试图片替代
      console.log('尝试将PDF转换为图片');
      
      // 设置总页数
      this.totalPages = 1;
      
      // 使用PDF服务的示例图片API
      const testImageUrl = `${this.apiBaseUrl}/api/common/sample-pdf-image`;
      console.log('使用示例图片:', testImageUrl);
      
      // 请求示例图片
      uni.request({
        url: testImageUrl,
        method: 'GET',
        responseType: 'arraybuffer',
        success: (res) => {
          if (res.statusCode === 200) {
            // 转换为Base64
            const base64 = uni.arrayBufferToBase64(res.data);
            this.currentPageImageUrl = `data:image/png;base64,${base64}`;
            this.loading = false;
          } else {
            console.error('获取示例图片失败，使用本地生成图片');
            this.createLocalPlaceholderImage();
          }
        },
        fail: (err) => {
          console.error('请求示例图片失败:', err);
          this.createLocalPlaceholderImage();
        }
      });
    },
    
    // 添加新方法，创建本地占位图片
    createLocalPlaceholderImage() {
      // 创建一个简单的文本图片，显示"PDF预览"
      try {
        const canvas = document.createElement('canvas');
        canvas.width = 800;
        canvas.height = 1000;
        const ctx = canvas.getContext('2d');
        
        // 绘制白色背景
        ctx.fillStyle = '#FFFFFF';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // 绘制边框
        ctx.strokeStyle = '#CCCCCC';
        ctx.lineWidth = 2;
        ctx.strokeRect(10, 10, canvas.width - 20, canvas.height - 20);
        
        // 绘制文本
        ctx.fillStyle = '#333333';
        ctx.font = 'bold 30px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('PDF预览', canvas.width/2, 100);
        
        ctx.font = '20px Arial';
        ctx.fillText(this.filename, canvas.width/2, 150);
        
        ctx.font = '16px Arial';
        ctx.fillText('服务器未提供PDF渲染支持', canvas.width/2, 200);
        ctx.fillText('请使用下载功能查看完整PDF', canvas.width/2, 230);
        
        // 转换为Base64
        this.currentPageImageUrl = canvas.toDataURL('image/png');
      } catch(e) {
        console.error('无法创建预览图:', e);
        // 如果Canvas操作失败，创建一个文本提示
        this.errorMessage = '无法生成PDF预览，请下载PDF查看';
      }
      
      // 关闭加载状态
      this.loading = false;
    },
    
    // 处理图片加载完成事件
    handleImageLoaded(e) {
      console.log('图片加载完成:', e);
      
      try {
        // 获取图片尺寸
        const detail = e.detail || e.target || {};
        const width = detail.width || this.screenWidth * 0.95; // 默认使用屏幕宽度的95%
        const height = detail.height || width * 1.4; // 使用默认宽高比
        
        if (!this.baseImageWidth || !this.baseImageHeight) {
          // 只在第一次设置基础尺寸
          this.baseImageWidth = width;
          this.baseImageHeight = height;
          console.log('设置基础图片尺寸:', width, 'x', height);
        }
        
        this.loading = false;
        
        // 检查是否所有图片都已加载
        const allLoaded = this.allPagesImageUrls.every(url => url);
        if (allLoaded && this.isLoadingAllPages) {
          this.isLoadingAllPages = false;
          clearTimeout(this.loadingTimeout);
          uni.hideLoading();
        }
      } catch (error) {
        console.error('处理图片尺寸时出错:', error);
        this.loading = false;
      }
    },
    
    // 修改图片错误处理方法，实现自动清除缓存
    handleImageError(e) {
      console.error('图片加载失败:', e);
      
      // 计数失败的图片
      this.failedImagesCount = (this.failedImagesCount || 0) + 1;
      
      // 检查是否为431错误
      const errorMsg = e.detail?.errMsg || '';
      if (errorMsg.includes('431') || errorMsg.includes('header') || errorMsg.includes('too large')) {
        // 立即停止所有加载
        clearTimeout(this.loadingTimeout);
        this.loading = false;
        this.isLoadingAllPages = false;
        uni.hideLoading();
        
        // 自动尝试清除缓存并重新加载
        uni.showLoading({
          title: '正在清除缓存...',
          mask: true
        });
        
        // 先清除缓存
        this.clearCache(true);
        
        // 延迟后重试加载
        setTimeout(() => {
          this.retryLoad(true);
        }, 1000);
        
        return;
      }
      
      // 如果所有图片都加载失败，关闭加载状态
      if (this.failedImagesCount >= this.totalPages) {
        clearTimeout(this.loadingTimeout);
        this.loading = false;
        this.isLoadingAllPages = false;
        uni.hideLoading();
        
        // 自动尝试清除缓存并重新加载（如果失败次数不多）
        if (this.retryCount < 2) {
          uni.showToast({
            title: '加载失败，自动重试',
            icon: 'none',
            duration: 1500
          });
          
          // 延迟后清除缓存并重试
          setTimeout(() => {
            this.clearCache(true);
            this.retryLoad(true);
          }, 1500);
        } else {
          // 如果已经重试多次，显示备选方案
          this.showAlternative = true;
          this.errorMessage = '图片加载失败，请下载PDF查看';
        }
      }
    },
    
    // 适配屏幕
    fitScreen() {
      this.isOriginalSize = false;
      
      // 如果是服务端渲染，重新加载所有页面
      if (this.isServerSideRendering) {
        const baseUrl = this.downloadUrl.startsWith('http') ? '' : this.apiBaseUrl;
        const pdfUrl = this.downloadUrl.startsWith('http') ? this.downloadUrl : `${baseUrl}${this.downloadUrl}`;
        const encodedPdfUrl = encodeURIComponent(pdfUrl);
        this.loadAllPages(encodedPdfUrl);
      }
    },
    
    // 显示原始尺寸
    originalSize() {
      this.isOriginalSize = true;
      
      // 如果是服务端渲染，重新加载所有页面，使用更高清的图片
      if (this.isServerSideRendering) {
        const baseUrl = this.downloadUrl.startsWith('http') ? '' : this.apiBaseUrl;
        const pdfUrl = this.downloadUrl.startsWith('http') ? this.downloadUrl : `${baseUrl}${this.downloadUrl}`;
        const encodedPdfUrl = encodeURIComponent(pdfUrl);
        this.loadAllPages(encodedPdfUrl, 2.0); // 使用更高的缩放比例获取更清晰的图片
      }
    },
    
    // 重试加载
    retryLoad(isAuto = false) {
      this.retryCount++;
      if (this.retryCount > 3) {
        this.canRetry = false;
        this.errorMessage = '重试次数过多，请使用其他方式查看PDF';
        return;
      }
      
      // 先清除状态
      this.loading = true;
      this.showAlternative = false;
      this.errorMessage = '';
      this.allPagesImageUrls = [];
      this.failedImagesCount = 0;
      
      // 检查是否需要清除缓存
      if (this.retryCount > 1) {
        // 第二次重试时清除缓存
        this.clearCache();
      } else {
        // 第一次重试直接重新请求
        this.requestPdfImages();
      }
    },
    
    // 在系统浏览器中打开
    openInSystemBrowser() {
      if (!this.downloadUrl) {
        uni.showToast({
          title: '没有可用的下载链接',
          icon: 'none'
        });
        return;
      }
      
      // 使用全局配置的API地址
      const baseUrl = this.downloadUrl.startsWith('http') ? '' : this.apiBaseUrl;
      const fullUrl = this.downloadUrl.startsWith('http') ? this.downloadUrl : `${baseUrl}${this.downloadUrl}`;
      
      console.log('尝试在系统浏览器中打开:', fullUrl);
      
      try {
        // 检查平台类型
        const sysInfo = uni.getSystemInfoSync();
        
        if (sysInfo.platform === 'android' || sysInfo.platform === 'ios') {
          // App环境
          if (plus) {
            plus.runtime.openURL(fullUrl);
          } else {
            // 尝试使用uni的API
            uni.navigateTo({
              url: fullUrl,
              fail: () => {
                // 回退到window.open
                window.open(fullUrl, '_system');
              }
            });
          }
        } else {
          // H5环境，直接使用window.open
          window.open(fullUrl, '_blank');
        }
      } catch (error) {
        console.error('打开系统浏览器失败:', error);
        uni.showToast({
          title: '打开浏览器失败',
          icon: 'none'
        });
      }
    },
    
    // 使用第三方应用打开
    openWithThirdParty() {
      if (!this.downloadUrl) {
        uni.showToast({
          title: '没有可用的下载链接',
          icon: 'none'
        });
        return;
      }
      
      // 使用全局配置的API地址
      const baseUrl = this.downloadUrl.startsWith('http') ? '' : this.apiBaseUrl;
      const fullUrl = this.downloadUrl.startsWith('http') ? this.downloadUrl : `${baseUrl}${this.downloadUrl}`;
      
      try {
        if (plus) {
          plus.share.sendWithSystem({
            type: 'file',
            title: this.filename,
            href: fullUrl
          }, function() {
            console.log('分享成功');
          }, function(e) {
            console.log('分享失败：' + e.message);
          });
        } else {
          uni.showToast({
            title: '当前环境不支持系统分享',
            icon: 'none'
          });
        }
      } catch (error) {
        console.error('分享失败:', error);
        uni.showToast({
          title: '无法调用系统分享',
          icon: 'none'
        });
      }
    },
    
    // 下载PDF
    downloadPdf() {
      if (!this.downloadUrl) {
        uni.showToast({
          title: '没有可用的下载链接',
          icon: 'none'
        });
        return;
      }
      
      console.log('准备下载PDF文件');
      
      // 检查平台类型
      const sysInfo = uni.getSystemInfoSync();
      
      // 使用全局配置的API地址
      const baseUrl = this.downloadUrl.startsWith('http') ? '' : this.apiBaseUrl;
      const fullUrl = this.downloadUrl.startsWith('http') ? this.downloadUrl : `${baseUrl}${this.downloadUrl}`;
      
      if (sysInfo.platform === 'android' || sysInfo.platform === 'ios') {
        // 移动端 - 使用系统下载能力
        if (plus) {
          plus.runtime.openURL(fullUrl);
        } else {
          uni.downloadFile({
            url: fullUrl,
            success: (res) => {
              if (res.statusCode === 200) {
                // 获取下载的文件路径
                const filePath = res.tempFilePath;
                
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
              } else {
                uni.showToast({
                  title: '下载文件失败',
                  icon: 'none'
                });
              }
            },
            fail: () => {
              uni.showToast({
                title: '下载请求失败',
                icon: 'none'
              });
            }
          });
        }
      } else {
        // H5端 - 创建隐藏的a标签下载
        try {
          const link = document.createElement('a');
          link.href = fullUrl;
          link.target = '_blank';
          link.download = this.filename;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          
          uni.showToast({
            title: '文件下载中',
            icon: 'success'
          });
        } catch (e) {
          console.error('创建下载链接失败:', e);
          // 直接打开链接
          window.open(fullUrl, '_blank');
        }
      }
    },
    
    // 切换诊断信息显示
    toggleDiagnostic() {
      this.showDiagnostic = !this.showDiagnostic;
    },
    
    // 显示备选方案选项
    showAlternativeOptions() {
      this.showAlternative = true;
    },
    
    // 返回上一页
    goBack() {
      uni.navigateBack();
    },
    
    // 显示删除确认对话框
    showDeleteConfirm() {
      if (!this.reportId) {
        uni.showToast({
          title: '缺少报告ID，无法删除',
          icon: 'none'
        });
        return;
      }
      
      this.showDeleteModal = true;
    },
    
    // 取消删除
    cancelDelete() {
      this.showDeleteModal = false;
    },
    
    // 确认删除
    confirmDelete() {
      if (this.isDeleting) return; // 防止重复点击
      
      this.isDeleting = true;
      
      // 构建删除API的URL
      const deleteUrl = `${this.apiBaseUrl}${config.apiPaths.reports.delete}/${this.reportId}`;
      
      console.log('删除报告:', deleteUrl);
      
      uni.showLoading({
        title: '正在删除...',
        mask: true
      });
      
      uni.request({
        url: deleteUrl,
        method: 'DELETE',
        success: (res) => {
          uni.hideLoading();
          
          if (res.statusCode === 200 || res.statusCode === 204) {
            uni.showToast({
              title: '删除成功',
              icon: 'success',
              duration: 2000
            });
            
            // 延迟返回列表页
            setTimeout(() => {
              this.goBack();
            }, 1500);
          } else {
            console.error('删除报告失败:', res);
            uni.showToast({
              title: '删除失败: ' + (res.data?.message || '未知错误'),
              icon: 'none',
              duration: 3000
            });
          }
        },
        fail: (err) => {
          uni.hideLoading();
          console.error('删除请求失败:', err);
          uni.showToast({
            title: '删除请求失败',
            icon: 'none',
            duration: 3000
          });
        },
        complete: () => {
          this.isDeleting = false;
          this.showDeleteModal = false;
        }
      });
    },
    
    // 清除缓存
    clearCache(silent = false) {
      console.log('尝试清除缓存');
      // 清除浏览器缓存
      if (typeof plus !== 'undefined') {
        // App环境
        plus.webview.currentWebview().reload(true);
      } else {
        // 尝试清除图片缓存
        this.allPagesImageUrls = [];
        // 使用随机参数重新加载
        if (this.isServerSideRendering && this.downloadUrl) {
          const baseUrl = this.downloadUrl.startsWith('http') ? '' : this.apiBaseUrl;
          const pdfUrl = this.downloadUrl.startsWith('http') ? this.downloadUrl : `${baseUrl}${this.downloadUrl}`;
          const encodedPdfUrl = encodeURIComponent(pdfUrl);
          // 添加随机参数避免缓存
          const timestamp = new Date().getTime();
          this.loadAllPages(encodedPdfUrl + '&_t=' + timestamp);
        } else {
          // 如果没有服务端渲染或下载链接，重新请求图片
          this.requestPdfImages();
        }
      }
      
      // 显示提示（除非是静默模式）
      if (!silent) {
        uni.showToast({
          title: '缓存已清除',
          icon: 'success'
        });
      }
    }
  }
}
</script>

<style scoped>
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

.subtitle-container {
  margin-top: 10rpx;
  display: flex;
  justify-content: center;
  align-items: center;
}

.subtitle-label {
  font-size: 28rpx;
  color: #666;
  font-weight: bold;
}

.subtitle {
  font-size: 28rpx;
  color: #666;
  display: inline;
  max-width: 80%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pdf-image-container {
  flex: 1;
  width: 100%;
  display: flex;
  flex-direction: column;
  background-color: #e0e0e0;
  overflow: hidden;
}

.page-controls {
  padding: 10rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f8f8f8;
  border-bottom: 1px solid #ddd;
}

.page-button {
  min-width: 80rpx;
  height: 60rpx;
  line-height: 60rpx;
  font-size: 24rpx;
  margin: 0 10rpx;
  padding: 0 20rpx;
  background-color: #2871FA;
  color: white;
}

.page-info {
  margin: 0 20rpx;
  font-size: 28rpx;
  color: #333;
}

.zoom-button {
  background-color: #1890FF;
}

.image-scroll {
  flex: 1;
  width: 100%;
  background-color: #f0f0f0;
  display: flex;
  align-items: flex-start; /* 改为顶部对齐 */
  justify-content: center;
  overflow-x: hidden; /* 确保不显示水平滚动条 */
}

.all-pages-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20rpx 0;
}

.page-wrapper {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20rpx; /* 减小间距 */
}

.pdf-image {
  background-color: white;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.2);
  transition: width 0.3s, height 0.3s;
  margin: 0 auto; /* 水平居中 */
  display: block;
  border-radius: 8rpx;
}

.page-separator {
  height: 1rpx; /* 减小分隔线高度 */
  background-color: #ddd;
  width: 80%;
  margin: 15rpx 0; /* 减小分隔线间距 */
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #999;
  font-size: 28rpx;
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
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 100;
}

.loader {
  width: 40rpx;
  height: 40rpx;
  border: 4rpx solid #2871FA;
  border-radius: 50%;
  border-left-color: transparent;
  animation: spin 1s linear infinite;
  margin-bottom: 20rpx;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-size: 32rpx;
  color: #333;
}

.button-section {
  padding: 20rpx;
  background-color: #ffffff;
  box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.button-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20rpx;
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
  width: 100%;
}

.action-button {
  width: 100%;
  background-color: #1890FF;
  color: #fff;
  border: none;
  border-radius: 8rpx;
  font-size: 28rpx;
  height: 80rpx;
  line-height: 80rpx;
  padding: 0 20rpx;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
}

.primary-button {
  background-color: #2871FA;
  color: #fff;
}

.delete-button {
  background-color: #ff4d4f;
  color: #fff;
}

.alternative-container {
  flex: 1;
  width: 100%;
  height: auto;
  padding: 40rpx;
  background-color: #f9f9f9;
  border-radius: 10rpx;
  margin: 20rpx;
  overflow-y: auto;
  box-sizing: border-box;
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
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  margin-bottom: 30rpx;
}

.button-wrapper {
  width: 45%;
  margin: 10rpx;
  box-sizing: border-box;
}

.browser-button {
  background-color: #22AD38;
}

.share-button {
  background-color: #F48F18;
}

.retry-button {
  background-color: #1890FF;
}

.button-icon {
  margin-right: 10rpx;
  font-size: 32rpx;
}

.button-text {
  font-size: 28rpx;
  color: #fff;
}

.divider {
  height: 1px;
  background-color: #ddd;
  margin: 20rpx 0;
  width: 100%;
}

.diagnostic-section {
  margin-top: 20rpx;
  padding: 20rpx;
  background-color: #f2f2f2;
  border-radius: 10rpx;
  width: 100%;
  box-sizing: border-box;
}

.diagnostic-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #666;
}

.diagnostic-details {
  margin-top: 10rpx;
  display: flex;
  flex-direction: column;
}

.diagnostic-item {
  font-size: 24rpx;
  color: #999;
  margin: 6rpx 0;
}

/* 删除确认弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.modal-content {
  width: 80%;
  max-width: 600rpx;
  background-color: #fff;
  border-radius: 12rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.15);
}

.modal-header {
  padding: 30rpx;
  background-color: #f8f8f8;
  border-bottom: 1rpx solid #eee;
}

.modal-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  text-align: center;
  display: block;
}

.modal-body {
  padding: 40rpx 30rpx;
}

.modal-text {
  font-size: 28rpx;
  color: #333;
  text-align: center;
  display: block;
  margin-bottom: 20rpx;
}

.modal-filename {
  font-size: 26rpx;
  color: #666;
  text-align: center;
  display: block;
  word-break: break-all;
  padding: 0 20rpx;
}

.modal-footer {
  display: flex;
  border-top: 1rpx solid #eee;
}

.modal-button {
  flex: 1;
  height: 90rpx;
  line-height: 90rpx;
  text-align: center;
  font-size: 30rpx;
  border: none;
  border-radius: 0;
}

.cancel-button {
  background-color: #f5f5f5;
  color: #333;
  border-right: 1rpx solid #eee;
}

.confirm-button {
  background-color: #ff4d4f;
  color: #fff;
}
</style> 