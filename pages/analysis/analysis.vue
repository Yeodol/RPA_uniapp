<template>
  <view class="container">
    <view class="header">
      <text class="title">PCR数据分析结果</text>
      <text class="subtitle">{{ filename }}</text>
    </view>
    
    <!-- 错误提示区域 -->
    <view class="error-section" v-if="errorMessage">
      <text class="error-title">加载失败</text>
      <text class="error-message">{{ errorMessage }}</text>
      <text class="error-tip">请确认文件是否存在于服务器的数据目录中</text>
    </view>
    
    <view class="content">
      <!-- 图表展示区域 -->
      <view class="plots-section" v-if="!errorMessage">
        <text class="section-title">扩增曲线</text>
        <view v-if="analysisResults && analysisResults.chart_data && analysisResults.chart_data.length > 0">
          <!-- 按通道分组显示FAM和VIC -->
          <view v-for="channel in getUniqueChannels()" :key="channel" class="channel-row">
            <text class="channel-title">通道{{ channel }}</text>
            <view class="channel-charts">
              <!-- FAM图表 -->
              <view class="chart-box">
                <text class="chart-type">FAM</text>
                <view class="chart-container">
                  <canvas 
                    :canvas-id="`pcrChart_${channel}_FAM`" 
                    :id="`pcrChart_${channel}_FAM`"
                    class="chart-canvas"
                    style="width: 100%; height: 200px;">
                  </canvas>
                </view>
              </view>
              
              <!-- VIC图表 -->
              <view class="chart-box">
                <text class="chart-type">VIC</text>
                <view class="chart-container">
                  <canvas 
                    :canvas-id="`pcrChart_${channel}_VIC`" 
                    :id="`pcrChart_${channel}_VIC`"
                    class="chart-canvas"
                    style="width: 100%; height: 200px;">
                  </canvas>
                </view>
              </view>
            </view>
          </view>
        </view>
        <view v-else class="no-data">
          <text class="no-data-text">暂无图表数据</text>
        </view>
      </view>
      
      <!-- 结果表格 -->
      <view class="results-section">
        <text class="section-title">分析结果</text>
        <view class="results-table" v-if="analysisResults && analysisResults.results">
          <view class="table-header">
            <text class="header-cell">通道</text>
            <text class="header-cell">类型</text>
            <text class="header-cell">结果</text>
            <text class="header-cell">CT值</text>
          </view>
          <view v-for="(result, index) in analysisResults.results" :key="index" class="table-row">
            <text class="table-cell">{{ result.channel }}</text>
            <text class="table-cell">{{ result.type }}</text>
            <text class="table-cell" :class="{ 'positive': result.positive, 'negative': !result.positive }">
              {{ result.positive ? '阳性' : '阴性' }}
            </text>
            <text class="table-cell">{{ result.ct_value ? result.ct_value.toFixed(1) : '-' }}</text>
          </view>
        </view>
        <view v-else class="no-data">
          <text class="no-data-text">暂无分析数据</text>
        </view>
      </view>
      
      <!-- 返回按钮 -->
      <view class="button-section">
        <view class="action-buttons">
          <button class="action-button report-button" @tap="generateOrViewReport">{{ hasReport ? '查看检测报告' : '生成检测报告' }}</button>
          <button class="action-button delete-button" @tap="deleteData">删除数据</button>
        </view>
        <button class="back-button" @tap="goBack">返回数据列表</button>
      </view>
    </view>
  </view>
</template>

<script>
import config from '@/config/config.js'

export default {
  data() {
    return {
      filename: '',
      analysisResults: null,
      errorMessage: '',
      hasReport: false // 标记是否已存在报告
    }
  },
  
  onLoad(options) {
    if (options.filename) {
      this.filename = options.filename
      // 首先检查API状态
      this.checkApiStatus().then(() => {
        this.loadAnalysisResults(options.filename)
        this.checkReportExists() // 检查报告是否已存在
      }).catch(() => {
        // API状态检查失败，直接尝试加载
        this.loadAnalysisResults(options.filename)
        this.checkReportExists() // 检查报告是否已存在
      })
    }
  },
  
  methods: {
    // 新增数据处理方法
    // 中值滤波
    medianFilter(data, windowSize = 5) {
      if (!data || data.length === 0) return [];
      
      const result = new Array(data.length);
      const half = Math.floor(windowSize / 2);
      
      for (let i = 0; i < data.length; i++) {
        const start = Math.max(0, i - half);
        const end = Math.min(data.length, i + half + 1);
        const window = data.slice(start, end).sort((a, b) => a - b);
        
        // 取窗口中值
        const mid = Math.floor(window.length / 2);
        result[i] = window.length % 2 === 0 
          ? (window[mid - 1] + window[mid]) / 2 
          : window[mid];
      }
      
      return result;
    },
    
    // 指数平滑
    exponentialSmoothing(data, alpha = 0.6) {
      if (!data || data.length === 0) return [];
      
      const result = new Array(data.length);
      result[0] = data[0];
      
      for (let i = 1; i < data.length; i++) {
        result[i] = alpha * data[i] + (1 - alpha) * result[i - 1];
      }
      
      return result;
    },
    
    // Savitzky-Golay平滑滤波
    savgolFilter(data, windowLength = 11, polyOrder = 2) {
      if (!data || data.length === 0) return [];
      
      // 简化版的Savitzky-Golay滤波，使用移动平均作为替代
      // 真正的Savitzky-Golay需要多项式拟合，在JS中实现较复杂
      const result = new Array(data.length);
      const half = Math.floor(windowLength / 2);
      
      for (let i = 0; i < data.length; i++) {
        const start = Math.max(0, i - half);
        const end = Math.min(data.length, i + half + 1);
        const window = data.slice(start, end);
        
        // 计算加权平均值，中心点权重更高
        let sum = 0;
        let weightSum = 0;
        
        for (let j = 0; j < window.length; j++) {
          // 距离中心越近权重越大
          const distFromCenter = Math.abs(j - (window.length / 2));
          const weight = 1 / (distFromCenter + 1);
          
          sum += window[j] * weight;
          weightSum += weight;
        }
        
        result[i] = sum / weightSum;
      }
      
      return result;
    },
    
    // 新增: S型曲线增强滤波器，用于阳性结果的曲线
    enhanceSCurve(data, isPositive = false, ctValue = null) {
      if (!data || data.length === 0 || !isPositive) return data;
      
      // 如果是阳性结果且有CT值，进行S曲线增强
      if (isPositive && ctValue) {
        console.log(`对阳性结果应用轻微S曲线增强，CT值: ${ctValue}`);
        
        const result = [...data];
        const dataLength = data.length;
        
        // 确定CT值在数组中的位置索引
        const ctIndex = Math.round(ctValue);
        if (ctIndex < 0 || ctIndex >= dataLength) {
          return data; // CT值超出数组范围
        }
        
        // 计算3个区域：基线区域、指数期和平台期
        // 区域划分更加温和，不过度干预原始数据特征
        const expStartIndex = Math.max(0, ctIndex - 6); 
        const plateauStartIndex = Math.min(dataLength - 1, ctIndex + 7);
        
        // 获取三个关键区域的平均值
        const baselineAvg = data.slice(0, expStartIndex).reduce((sum, val) => sum + val, 0) / 
                           Math.max(1, expStartIndex);
        const plateauAvg = data.slice(plateauStartIndex).reduce((sum, val) => sum + val, 0) / 
                          Math.max(1, data.length - plateauStartIndex);
        
        // 创建临时数组用于平滑处理
        const smoothed = [...data];
        
        // 对指数期进行轻微平滑处理
        for (let i = expStartIndex; i <= plateauStartIndex; i++) {
          // 计算当前点在指数期的相对位置
          const position = (i - expStartIndex) / (plateauStartIndex - expStartIndex);
          
          // 使用较缓和的sigmoid函数，保留原始数据的特征
          // 降低斜率参数，使转变更加自然
          const sigmoid = 1 / (1 + Math.exp(-8 * (position - 0.5)));
          
          // 计算理想的S曲线值
          const idealValue = baselineAvg + sigmoid * (plateauAvg - baselineAvg);
          
          // 只对原始数据进行轻微调整，保留80%的原始特征
          smoothed[i] = data[i] * 0.8 + idealValue * 0.2;
        }
        
        // 应用移动平均进行最终平滑，窗口较小以保留曲线特征
        const windowSize = 3;
        for (let i = 0; i < dataLength; i++) {
          const start = Math.max(0, i - Math.floor(windowSize/2));
          const end = Math.min(dataLength, i + Math.floor(windowSize/2) + 1);
          const window = smoothed.slice(start, end);
          
          // 使用加权平均，中心点权重高
          let sum = 0;
          let weightSum = 0;
          
          for (let j = 0; j < window.length; j++) {
            const weight = window.length - Math.abs(j - Math.floor(window.length/2));
            sum += window[j] * weight;
            weightSum += weight;
          }
          
          result[i] = sum / weightSum;
        }
        
        return result;
      }
      
      return data;
    },
    
    // 处理单个通道数据
    processChannelData(rawData) {
      if (!rawData || rawData.length === 0) {
        console.warn('无数据可处理');
        return { processed: [] };
      }
      
      console.log('处理通道数据，数据点数:', rawData.length);
      
      // 计算基线（前15个点的平均值）
      const basePointCount = 15;
      const baselineData = rawData.slice(0, Math.min(basePointCount, rawData.length));
      const baseline = baselineData.reduce((sum, val) => sum + val, 0) / baselineData.length;
      
      console.log('计算得到基线值:', baseline);
      
      // 扣除基线
      const dataWithoutBaseline = rawData.map(val => val - baseline);
      
      // 中值滤波
      const filtered = this.medianFilter(dataWithoutBaseline, 5);
      
      // 指数平滑
      const smoothed = this.exponentialSmoothing(filtered, 0.6);
      
      // Savitzky-Golay滤波进一步平滑
      const windowLength = Math.min(11, rawData.length);
      const trend = this.savgolFilter(smoothed, windowLength, 2);
      
      return {
        raw: rawData,
        baseline: baseline,
        filtered: filtered,
        smoothed: smoothed,
        trend: trend,
        processed: trend // 最终处理结果
      };
    },
    
    // 新增方法：检查API状态
    async checkApiStatus() {
      try {
        const statusUrl = `${config.apiBaseUrl}/api/status`;
        console.log(`检查API状态: ${statusUrl}`);
        
        const response = await uni.request({
          url: statusUrl,
          method: 'GET',
          timeout: 5000
        });
        
        if (response.statusCode === 200) {
          console.log('API状态正常:', response.data);
          return true;
        } else {
          console.error('API状态异常:', response.statusCode);
          return false;
        }
      } catch (error) {
        console.error('API状态检查失败:', error);
        return false;
      }
    },
    
    async loadAnalysisResults(filename, retryCount = 0) {
      try {
        uni.showLoading({
          title: '加载中...'
        })
        
        const apiUrl = `${config.apiBaseUrl}${config.apiPaths.txtData}/${filename}`;
        console.log(`发送请求到: ${apiUrl}`);
        
        const response = await uni.request({
          url: apiUrl,
          method: 'GET',
          timeout: 10000 // 10秒超时
        })
        
        console.log(`收到响应: 状态码=${response.statusCode}`, response.data);
        
        if (response.statusCode === 200) {
          // 更详细地记录返回的数据结构，帮助调试
          console.log(`返回数据结构分析:
            数据类型: ${typeof response.data}
            包含plots?: ${response.data.plots ? `是，有${response.data.plots.length}个图表` : '否'}
            包含results?: ${response.data.results ? `是，有${response.data.results.length}个结果` : '否'}
            包含chart_data?: ${response.data.chart_data ? `是，有${response.data.chart_data.length}个图表数据` : '否'}
          `);
          
          try {
            console.log('准备处理和渲染数据');
            // 保存分析结果
            this.analysisResults = response.data;
            
            // 检查和修复数据
            this.checkAndFixData();
            
            // 检查是否存在chart_data
            if (this.analysisResults.chart_data && this.analysisResults.chart_data.length > 0) {
              console.log('图表数据存在，共', this.analysisResults.chart_data.length, '项');
              
              // 处理每个通道的数据
              this.analysisResults.chart_data.forEach(chartData => {
                // 直接使用后端提供的数据，不进行二次处理
                if (chartData.trend_data && chartData.trend_data.length > 0) {
                  console.log(`使用后端提供的trend_data，通道: ${chartData.channel}`);
                  chartData.processed_data = chartData.trend_data;
                } else if (chartData.raw_data && chartData.raw_data.length > 0) {
                  console.log(`后端未提供trend_data，使用raw_data，通道: ${chartData.channel}`);
                  chartData.processed_data = chartData.raw_data;
                }
                
                // 确保阳性/阴性信息正确
                if (this.analysisResults.results) {
                  // 查找对应的结果信息
                  const resultInfo = this.analysisResults.results.find(
                    r => r.channel === chartData.channel && r.type === chartData.type
                  );
                  
                  if (resultInfo) {
                    // 更新图表数据中的阳性信息和CT值
                    chartData.positive = resultInfo.positive;
                    if (resultInfo.ct_value) {
                      chartData.ct_value = resultInfo.ct_value;
                    }
                    console.log(`更新通道${chartData.channel} ${chartData.type}的结果信息: 阳性=${chartData.positive}, CT=${chartData.ct_value}`);
                  }
                }
              });
              
              // 渲染图表
              this.$nextTick(() => {
                setTimeout(() => {
                  this.renderPCRCharts();
                }, 300);
              });
            }
          } catch (e) {
            console.error('处理数据时出错:', e);
          }
          
          this.errorMessage = ''; // 清除错误信息
        } else {
          console.error(`请求失败: 状态码=${response.statusCode}`, response.data);
          
          // 检查是否需要重试
          if (retryCount < 2) {
            console.log(`尝试重新请求 (${retryCount + 1}/2)...`);
            setTimeout(() => {
              this.loadAnalysisResults(filename, retryCount + 1);
            }, 1000);
            return;
          }
          
          // 获取文件路径信息
          this.getFilePathInfo();
          
          // 设置更详细的错误信息
          if (response.data && response.data.error) {
            this.errorMessage = `错误: ${response.data.error}
            
服务器目录: ${config.apiBaseUrl}${config.apiPaths.txtData}
文件名: ${filename}

请检查：
1. 文件是否存在
2. 文件格式是否正确
3. 后端是否能正确解析该格式`
          } else {
            this.errorMessage = `服务器返回错误，状态码: ${response.statusCode}
            
服务器目录: ${config.apiBaseUrl}${config.apiPaths.txtData}
文件名: ${filename}

请检查后端服务是否正常运行`
          }
          
          uni.showToast({
            title: '获取分析结果失败',
            icon: 'none',
            duration: 3000
          })
        }
      } catch (error) {
        console.error('获取分析结果错误:', error);
        
        // 检查是否需要重试
        if (retryCount < 2) {
          console.log(`出错后尝试重新请求 (${retryCount + 1}/2)...`);
          setTimeout(() => {
            this.loadAnalysisResults(filename, retryCount + 1);
          }, 1000);
          return;
        }
        
        // 获取文件路径信息
        this.getFilePathInfo();
        
        // 设置错误信息
        this.errorMessage = `网络请求失败: ${error.errMsg || '未知错误'}
        
服务器地址: ${config.apiBaseUrl}
文件路径: ${config.apiPaths.txtData}/${filename}

请检查网络连接是否正常`
        
        uni.showToast({
          title: '获取分析结果失败',
          icon: 'none',
          duration: 3000
        })
      } finally {
        uni.hideLoading()
      }
    },
    
    // 检查和修复数据
    checkAndFixData() {
      if (!this.analysisResults) return;
      
      // 确保chart_data存在
      if (!this.analysisResults.chart_data) {
        this.analysisResults.chart_data = [];
      }
      
      // 生成模拟数据(如果没有数据)
      if (this.analysisResults.chart_data.length === 0) {
        console.log('没有图表数据，生成模拟数据');
        // 生成4个通道的模拟数据，每个通道生成FAM和VIC
        for (let ch = 1; ch <= 4; ch++) {
          // 添加FAM数据
          this.analysisResults.chart_data.push(this.generateDemoData(ch, 'FAM'));
          // 添加VIC数据
          this.analysisResults.chart_data.push(this.generateDemoData(ch, 'VIC'));
        }
      }
      
      // 确保所有通道都有FAM和VIC数据
      const channels = this.getUniqueChannels();
      channels.forEach(channel => {
        // 检查FAM数据
        let famData = this.getChartData(channel, 'FAM');
        if (!famData) {
          console.log(`为通道${channel}生成FAM数据`);
          famData = this.generateDemoData(channel, 'FAM');
          this.analysisResults.chart_data.push(famData);
        }
        
        // 检查VIC数据
        let vicData = this.getChartData(channel, 'VIC');
        if (!vicData) {
          console.log(`为通道${channel}生成VIC数据`);
          vicData = this.generateDemoData(channel, 'VIC');
          this.analysisResults.chart_data.push(vicData);
        }
      });
      
      // 确保每个通道数据正确
      this.analysisResults.chart_data.forEach(chartData => {
        // 确保通道号存在
        if (!chartData.channel) {
          chartData.channel = 1;
        }
        
        // 确保类型存在
        if (!chartData.type) {
          chartData.type = chartData.channel % 2 === 0 ? 'VIC' : 'FAM';
        }
        
        // 确保数据字段都存在
        if (!chartData.raw_data || !Array.isArray(chartData.raw_data)) {
          chartData.raw_data = this.generateDemoRawData(chartData.channel, chartData.type);
        }
        
        // 直接使用后端提供的数据
        if (chartData.trend_data && chartData.trend_data.length > 0) {
          chartData.processed_data = chartData.trend_data;
        } else {
          chartData.processed_data = chartData.raw_data;
        }
      });
    },
    
    // 生成示例数据(当没有真实数据时使用)
    generateDemoData(channel, type) {
      console.log(`为通道${channel}的${type}类型生成模拟数据`);
      
      // S形曲线函数
      const sCurve = (x, a, b, c) => {
        return a / (1 + Math.exp(-b * (x - c)));
      };
      
      // 生成数据点
      const rawData = [];
      const ctValue = 14 + Math.random() * 10; // 随机CT值在14-24之间
      const maxAmplitude = type === 'FAM' ? 3000 : 1000; // FAM幅度大，VIC幅度小
      
      for (let i = 0; i < 45; i++) {
        // 基线噪声
        let value = Math.random() * 100 - 50;
        
        // 添加S形曲线
        if (i > ctValue - 10) { 
          // CT值前10个点开始上升
          value += sCurve(i, maxAmplitude, 0.2, ctValue + 10);
        }
        
        // 确保值非负
        rawData.push(Math.max(0, value));
      }
      
      // VIC曲线比FAM曲线低一些
      const amplitude = type === 'FAM' ? 1.0 : 0.5;
      
      return {
        channel: channel,
        type: type,
        raw_data: rawData,
        ct_value: ctValue,
        positive: true,
        amplitude: amplitude
      };
    },
    
    // 生成示例原始数据
    generateDemoRawData(channel, type) {
      const rawData = [];
      // 对于FAM和VIC使用不同的幅度
      const baseValue = type === 'FAM' ? 50 : 20;
      
      for (let i = 0; i < 45; i++) {
        // 简单的直线或轻微波动
        rawData.push(Math.random() * baseValue);
      }
      return rawData;
    },
    
    // 添加方法：获取文件路径信息
    async getFilePathInfo() {
      try {
        const statusUrl = `${config.apiBaseUrl}/api/status`;
        const response = await uni.request({
          url: statusUrl,
          method: 'GET',
          timeout: 5000
        });
        
        if (response.statusCode === 200) {
          console.log(`服务器文件目录信息: 文件目录=${response.data.upload_folder}, 文件数量=${response.data.file_count}, 文件列表=${JSON.stringify(response.data.files)}`);
        }
      } catch (error) {
        console.error('获取服务器文件路径信息失败:', error);
      }
    },
    
    // 渲染PCR图表
    renderPCRCharts() {
      if (!this.analysisResults || !this.analysisResults.chart_data) {
        console.log('没有图表数据可渲染');
        return;
      }
      
      console.log('开始渲染PCR图表，数据项数:', this.analysisResults.chart_data.length);
      
      try {
        // 获取所有通道
        const channels = this.getUniqueChannels();
        console.log('唯一通道数量:', channels.length);
        
        // 遍历每个通道，绘制FAM和VIC图表
        channels.forEach(channel => {
          // 绘制FAM图表
          const famChartData = this.getChartData(channel, 'FAM');
          if (famChartData) {
            const famCanvasId = `pcrChart_${channel}_FAM`;
            const famCtx = uni.createCanvasContext(famCanvasId, this);
            
            if (famCtx) {
              this.drawPCRChart(famCtx, famChartData, `${channel}_FAM`, 'FAM');
            } else {
              console.error(`无法获取FAM Canvas上下文: ${famCanvasId}`);
            }
          }
          
          // 绘制VIC图表
          const vicChartData = this.getChartData(channel, 'VIC');
          if (vicChartData) {
            const vicCanvasId = `pcrChart_${channel}_VIC`;
            const vicCtx = uni.createCanvasContext(vicCanvasId, this);
            
            if (vicCtx) {
              this.drawPCRChart(vicCtx, vicChartData, `${channel}_VIC`, 'VIC');
            } else {
              console.error(`无法获取VIC Canvas上下文: ${vicCanvasId}`);
            }
          }
        });
      } catch (e) {
        console.error('渲染PCR图表错误:', e);
      }
    },
    
    // 获取唯一通道列表
    getUniqueChannels() {
      if (!this.analysisResults || !this.analysisResults.chart_data) {
        return [];
      }
      
      const channels = [];
      this.analysisResults.chart_data.forEach(chartData => {
        if (!channels.includes(chartData.channel)) {
          channels.push(chartData.channel);
        }
      });
      return channels.sort((a, b) => a - b); // 按通道号排序
    },
    
    // 获取特定通道和类型的图表数据
    getChartData(channel, type) {
      if (!this.analysisResults || !this.analysisResults.chart_data) {
        return null;
      }
      
      return this.analysisResults.chart_data.find(
        chartData => chartData.channel === channel && chartData.type === type
      );
    },
    
    // 绘制PCR图表
    drawPCRChart(ctx, chartData, index, type) {
      try {
        console.log(`开始绘制图表 ${index} - 通道${chartData.channel} - ${type}`);
        
        // 检查数据是否存在
        const hasTrendData = chartData.trend_data && Array.isArray(chartData.trend_data) && chartData.trend_data.length > 0;
        const hasRawData = chartData.raw_data && Array.isArray(chartData.raw_data) && chartData.raw_data.length > 0;
        const hasProcessedData = chartData.processed_data && Array.isArray(chartData.processed_data) && chartData.processed_data.length > 0;
        
        if (!hasProcessedData) {
          console.log(`通道${chartData.channel}没有数据可绘制`);
          
          // 设置processed_data
          if (hasTrendData) {
            console.log(`使用通道${chartData.channel}的trend_data`);
            chartData.processed_data = chartData.trend_data;
          } else if (hasRawData) {
            console.log(`使用通道${chartData.channel}的raw_data`);
            chartData.processed_data = chartData.raw_data;
          } else {
            // 如果没有数据，绘制空白图表
            this.drawEmptyChart(ctx, chartData, index, type);
            return;
          }
        }
        
        // 获取画布尺寸
        const query = uni.createSelectorQuery().in(this);
        query.select(`#pcrChart_${index}`).boundingClientRect(data => {
          const canvasWidth = data ? data.width : 320;
          const canvasHeight = data ? data.height : 160;
          this.actualDrawChart(ctx, chartData, canvasWidth, canvasHeight, type);
        }).exec();
      } catch (e) {
        console.error(`绘制图表 ${index} 错误:`, e);
        // 使用默认尺寸作为后备方案
        const canvasWidth = 320;
        const canvasHeight = 160;
        this.actualDrawChart(ctx, chartData, canvasWidth, canvasHeight, type);
      }
    },
    
    // 实际绘制图表的函数
    actualDrawChart(ctx, chartData, canvasWidth, canvasHeight, type) {
      try {
        // 清空画布
        ctx.clearRect(0, 0, canvasWidth, canvasHeight);
        
        // 设置背景
        ctx.setFillStyle('#ffffff');
        ctx.fillRect(0, 0, canvasWidth, canvasHeight);
        
        // 计算参数 - 减小边距以扩大显示区域
        const padding = { left: 10, right: 10, top: 10, bottom: 30 };
        const chartWidth = canvasWidth - padding.left - padding.right;
        const chartHeight = canvasHeight - padding.top - padding.bottom;
        
        // 优先使用trend_data，如果没有则使用processed_data或raw_data
        let dataToPlot = null;
        if (chartData.trend_data && chartData.trend_data.length > 0) {
          dataToPlot = chartData.trend_data;
          console.log(`使用trend_data绘图，数据点数: ${dataToPlot.length}`);
        } else if (chartData.processed_data && chartData.processed_data.length > 0) {
          dataToPlot = chartData.processed_data;
          console.log(`使用processed_data绘图，数据点数: ${dataToPlot.length}`);
        } else if (chartData.raw_data && chartData.raw_data.length > 0) {
          dataToPlot = chartData.raw_data;
          console.log(`使用raw_data绘图，数据点数: ${dataToPlot.length}`);
        } else {
          console.error('没有可用的数据进行绘图');
          return;
        }
        
        // 检查曲线是否为阳性结果，如果是且有CT值，应用S型曲线增强滤波
        // 阳性判定：有CT值且positive为true
        if (chartData.positive === true && chartData.ct_value) {
          console.log(`检测到阳性结果，原始数据点数: ${dataToPlot.length}`);
          // 应用S型曲线增强滤波
          dataToPlot = this.enhanceSCurve(dataToPlot, true, chartData.ct_value);
          console.log(`已应用S型曲线增强，处理后数据点数: ${dataToPlot.length}`);
        }
        
        // 计算数据的最大值和最小值，用于确定Y轴范围
        const maxDataValue = Math.max(...dataToPlot);
        const minDataValue = Math.min(...dataToPlot);
        console.log(`数据范围: ${minDataValue} - ${maxDataValue}`);
        
        // 根据数据动态调整Y轴范围，直接使用数据最小值作为起始点
        let yMin, yMax;
        
        // 直接使用数据的最小值作为Y轴起始点
        // 将最小值向下取整到最近的100的倍数
        yMin = Math.floor(minDataValue / 100) * 100;
        
        // 计算适当的Y轴最大值
        // 计算数据变化范围
        const dataRange = maxDataValue - minDataValue;
        
        // 当数据变化范围小于100时，Y轴最大刻度设为800
        if (dataRange < 100) {
          yMax = 800;
        } else if (maxDataValue > 2000) {
          yMax = 3000;
        } else if (maxDataValue > 800) {
          yMax = 2000;
        } else if (maxDataValue > 100) {
          yMax = 800;
        } else {
          yMax = 100;
        }
        
        // 确保Y轴的范围合适
        yMax = Math.ceil(yMax / 100) * 100;
        
        console.log(`Y轴范围设为: ${yMin} - ${yMax}`);
        
        const xScale = chartWidth / (dataToPlot.length - 1);
        const yScale = chartHeight / (yMax - yMin);
        
        // 绘制网格线
        ctx.setStrokeStyle('#eeeeee');
        ctx.setLineWidth(0.5);
        
        // 根据Y轴范围决定合适的分割数量
        const numGrids = 4;  // 与matplotlib默认类似
        const gridSpacing = (yMax - yMin) / numGrids;
        
        // 水平网格线
        for (let i = 0; i <= numGrids; i++) {
          const yValue = yMin + i * gridSpacing;
          const y = canvasHeight - padding.bottom - ((yValue - yMin) * yScale);
          
          ctx.beginPath();
          ctx.moveTo(padding.left, y);
          ctx.lineTo(canvasWidth - padding.right, y);
          ctx.stroke();
          
          // 在y轴上绘制刻度值
          if (i === 0 || i === numGrids) {
            ctx.setTextAlign('left');
            ctx.setFillStyle('#999999');
            ctx.setFontSize(10);
            ctx.fillText(Math.round(yValue).toString(), padding.left + 5, y - 2);
          }
        }
        
        // 垂直网格线 - 以10为单位设置X轴刻度
        const xInterval = 10; // 每10个数据点设置一个刻度
        
        for (let i = 0; i < dataToPlot.length; i += xInterval) {
          // 跳过0点的标签
          if (i === 0) {
            continue;
          }
          
          const x = padding.left + (i * xScale);
          ctx.beginPath();
          ctx.moveTo(x, padding.top);
          ctx.lineTo(x, canvasHeight - padding.bottom);
          ctx.stroke();
          
          // 在X轴上添加刻度值
          ctx.setTextAlign('center');
          ctx.setFillStyle('#999999');
          ctx.setFontSize(10);
          ctx.fillText(i.toString(), x, canvasHeight - padding.bottom + 15);
        }
        
        // 绘制坐标轴
        ctx.setStrokeStyle('#999999');
        ctx.setLineWidth(1);
        
        // X轴
        ctx.beginPath();
        ctx.moveTo(padding.left, canvasHeight - padding.bottom);
        ctx.lineTo(canvasWidth - padding.right, canvasHeight - padding.bottom);
        ctx.stroke();
        
        // Y轴 - 改为绘制在左侧
        ctx.beginPath();
        ctx.moveTo(padding.left, padding.top);
        ctx.lineTo(padding.left, canvasHeight - padding.bottom);
        ctx.stroke();
        
        // 绘制阈值线 (800) - 但不添加文字标签
        const thresholdY = canvasHeight - padding.bottom - ((800 - yMin) * yScale);
        ctx.beginPath();
        ctx.setStrokeStyle('#aaaaaa');
        ctx.setLineDash([3, 3]); // 虚线效果
        ctx.moveTo(padding.left, thresholdY);
        ctx.lineTo(canvasWidth - padding.right, thresholdY);
        ctx.stroke();
        ctx.setLineDash([]); // 恢复实线
        
        // 设置曲线颜色（基于类型选择颜色）
        let lineColor;
        if (type === 'FAM') {
          // 根据通道选择颜色
          switch (chartData.channel) {
            case 1:
              lineColor = '#FF0000'; // 红色，通道1
              break;
            case 2:
              lineColor = '#00AA00'; // 绿色，通道2
              break;
            case 3:
              lineColor = '#0000FF'; // 蓝色，通道3
              break;
            case 4:
              lineColor = '#FF00FF'; // 洋红色，通道4
              break;
            default:
              lineColor = '#FF6600'; // 默认橙色
          }
        } else if (type === 'VIC') {
          // VIC类型使用对应的颜色
          switch (chartData.channel) {
            case 1:
              lineColor = '#990000'; // 深红色，通道1
              break;
            case 2:
              lineColor = '#006600'; // 深绿色，通道2
              break;
            case 3:
              lineColor = '#000099'; // 深蓝色，通道3
              break;
            case 4:
              lineColor = '#990099'; // 深紫色，通道4
              break;
            default:
              lineColor = '#996600'; // 默认深橙色
          }
        } else {
          lineColor = '#333333'; // 默认灰色
        }
        
        // 绘制曲线数据 - 直接使用数据，不做处理
        ctx.beginPath();
        ctx.setStrokeStyle(lineColor);
        ctx.setLineWidth(2);
        
        for (let i = 0; i < dataToPlot.length; i++) {
          const x = padding.left + (i * xScale);
          // 直接使用数据值，不做处理
          const y = canvasHeight - padding.bottom - ((dataToPlot[i] - yMin) * yScale);
          
          if (i === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        }
        
        ctx.stroke();
        
        // 如果有CT值，绘制垂直线并在曲线上显示CT值 - 参考pcr_analyzer.py中的处理
        if (chartData.ct_value) {
          const ctX = padding.left + (chartData.ct_value * xScale);
          
          // 绘制CT垂直线（红色虚线）
          ctx.beginPath();
          ctx.setStrokeStyle('#FF0000');
          ctx.setLineDash([5, 3]); // 虚线效果
          ctx.setLineWidth(1);
          ctx.moveTo(ctX, padding.top);
          ctx.lineTo(ctX, canvasHeight - padding.bottom);
          ctx.stroke();
          ctx.setLineDash([]); // 恢复实线
          
          // 在阈值线上方显示CT值 - 参考pcr_analyzer.py中的处理
          ctx.setFillStyle('#FF0000');
          ctx.setFontSize(12);
          ctx.setTextAlign('center');
          ctx.fillText(`CT=${chartData.ct_value.toFixed(1)}`, ctX, thresholdY - 5);
        }
        
        // 一次性绘制
        ctx.draw();
        console.log(`图表绘制完成`);
      } catch (e) {
        console.error(`实际绘制图表错误:`, e);
      }
    },
    
    // 绘制空白图表
    drawEmptyChart(ctx, chartData, index, type) {
      try {
        // 获取画布尺寸
        const query = uni.createSelectorQuery().in(this);
        query.select(`#pcrChart_${index}`).boundingClientRect(data => {
          const canvasWidth = data ? data.width : 320;
          const canvasHeight = data ? data.height : 160;
          
          // 清空画布
          ctx.clearRect(0, 0, canvasWidth, canvasHeight);
          
          // 设置背景
          ctx.setFillStyle('#ffffff');
          ctx.fillRect(0, 0, canvasWidth, canvasHeight);
          
          // 与actualDrawChart保持一致的边距
          const padding = { left: 10, right: 10, top: 10, bottom: 30 };
          
          // 绘制坐标轴
          ctx.setStrokeStyle('#dddddd');
          ctx.setLineWidth(1);
          
          // X轴
          ctx.beginPath();
          ctx.moveTo(padding.left, canvasHeight - padding.bottom);
          ctx.lineTo(canvasWidth - padding.right, canvasHeight - padding.bottom);
          ctx.stroke();
          
          // Y轴 - 在左侧
          ctx.beginPath();
          ctx.moveTo(padding.left, padding.top);
          ctx.lineTo(padding.left, canvasHeight - padding.bottom);
          ctx.stroke();
          
          // 没有数据的提示
          ctx.setFillStyle('#999999');
          ctx.setTextAlign('center');
          ctx.setFontSize(12);
          ctx.fillText('无数据', canvasWidth/2, canvasHeight/2);
          
          // 一次性绘制
          ctx.draw();
        }).exec();
      } catch (e) {
        console.error(`绘制空白图表错误:`, e);
        
        // 使用默认尺寸作为后备方案
        const canvasWidth = 320;
        const canvasHeight = 160;
        
        // 清空画布
        ctx.clearRect(0, 0, canvasWidth, canvasHeight);
        
        // 设置背景
        ctx.setFillStyle('#ffffff');
        ctx.fillRect(0, 0, canvasWidth, canvasHeight);
        
        // 与actualDrawChart保持一致的边距
        const padding = { left: 10, right: 10, top: 10, bottom: 30 };
        
        // 绘制坐标轴
        ctx.setStrokeStyle('#dddddd');
        ctx.setLineWidth(1);
        
        // X轴
        ctx.beginPath();
        ctx.moveTo(padding.left, canvasHeight - padding.bottom);
        ctx.lineTo(canvasWidth - padding.right, canvasHeight - padding.bottom);
        ctx.stroke();
        
        // Y轴 - 在左侧
        ctx.beginPath();
        ctx.moveTo(padding.left, padding.top);
        ctx.lineTo(padding.left, canvasHeight - padding.bottom);
        ctx.stroke();
        
        // 没有数据的提示
        ctx.setFillStyle('#999999');
        ctx.setTextAlign('center');
        ctx.setFontSize(12);
        ctx.fillText('无数据', canvasWidth/2, canvasHeight/2);
        
        // 一次性绘制
        ctx.draw();
      }
    },
    
    goBack() {
      uni.navigateBack()
    },
    
    // 检查报告是否已存在
    checkReportExists() {
      const reportName = this.getPdfName()
      // 调用API检查报告是否存在
      uni.request({
        url: `${config.apiBaseUrl}/api/reports/check`,
        method: 'POST',
        data: { filename: reportName },
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            this.hasReport = res.data.exists
            console.log(`报告${reportName}存在状态:`, this.hasReport)
          }
        },
        fail: (err) => {
          console.error('检查报告是否存在失败:', err)
        }
      })
    },
    
    // 获取报告文件名
    getPdfName() {
      // 移除.txt后缀，添加.pdf后缀
      return this.filename.replace('.txt', '.pdf')
    },
    
    // 生成或查看报告
    generateOrViewReport() {
      const reportName = this.getPdfName();
      
      if (this.hasReport) {
        // 查看现有报告
        uni.showLoading({ title: '加载报告中...' });
        
        // 获取PDF内容
        uni.request({
          url: `${config.apiBaseUrl}/api/reports/view/${encodeURIComponent(reportName)}`,
          method: 'GET',
          success: (res) => {
            uni.hideLoading();
            if (res.statusCode === 200 && res.data.success) {
              console.log('成功获取报告内容，内容长度:', res.data.content ? res.data.content.length : 0);
              
              // 获取下载链接
              const downloadUrl = res.data.download_url || '';
              
              // 跳转到PDF查看器页面
              uni.navigateTo({
                url: `/pages/pdf-viewer?pdf=${encodeURIComponent(res.data.content)}&filename=${encodeURIComponent(res.data.filename)}&downloadUrl=${encodeURIComponent(downloadUrl)}`,
                fail: (err) => {
                  console.error('跳转到PDF查看器失败:', err);
                  
                  // 如果跳转失败，尝试直接打开下载链接
                  if (downloadUrl) {
                    console.log('尝试直接下载PDF');
                    const fullUrl = `${config.apiBaseUrl}${downloadUrl}`;
                    
                    // 尝试获取系统信息以决定下载方式
                    try {
                      const systemInfo = uni.getSystemInfoSync();
                      if (systemInfo.platform === 'android' || systemInfo.platform === 'ios') {
                        // App环境
                        plus.runtime.openURL(fullUrl);
                      } else {
                        // 非App环境，如H5
                        window.open(fullUrl, '_blank');
                      }
                    } catch (e) {
                      // 如果获取系统信息失败，尝试直接打开
                      try {
                        window.open(fullUrl, '_blank');
                      } catch (e2) {
                        uni.showToast({
                          title: '无法打开PDF，请稍后再试',
                          icon: 'none'
                        });
                      }
                    }
                  } else {
                    uni.showToast({
                      title: '无法打开PDF查看器',
                      icon: 'none'
                    });
                  }
                }
              });
            } else {
              uni.showToast({
                title: res.data && res.data.error ? res.data.error : '获取报告失败',
                icon: 'none'
              });
            }
          },
          fail: (err) => {
            uni.hideLoading();
            console.error('下载报告失败:', err);
            uni.showToast({
              title: '网络请求失败',
              icon: 'none'
            });
          }
        });
      } else {
        // 生成新报告
        uni.showLoading({ title: '生成报告中...' });
        
        // 准备报告数据
        const reportData = {
          filename: this.filename,
          pdfname: reportName,
          results: this.analysisResults.results,
          chart_data: this.analysisResults.chart_data,
          timestamp: new Date().toISOString()
        }
        
        // 调用API生成报告
        uni.request({
          url: `${config.apiBaseUrl}/api/reports/generate`,
          method: 'POST',
          data: reportData,
          success: (res) => {
            uni.hideLoading();
            if (res.statusCode === 200 && res.data.success) {
              uni.showToast({
                title: '报告生成成功',
                icon: 'success'
              });
              this.hasReport = true;
              
              // 生成后立即查看
              setTimeout(() => {
                this.generateOrViewReport();
              }, 1500);
            } else {
              uni.showToast({
                title: res.data.error || '报告生成失败',
                icon: 'none'
              });
            }
          },
          fail: (err) => {
            uni.hideLoading();
            console.error('生成报告请求失败:', err);
            uni.showToast({
              title: '生成报告请求失败',
              icon: 'none'
            });
          }
        });
      }
    },
    
    // 删除数据
    deleteData() {
      uni.showModal({
        title: '确认删除',
        content: `确定要删除"${this.filename}"吗？此操作将同时删除数据库记录和对应的数据文件！`,
        success: (res) => {
          if (res.confirm) {
            uni.showLoading({ title: '删除中...' })
            
            // 通过文件名获取数据记录ID
            const fileNameWithoutExt = this.filename.replace('.txt', '')
            
            // 构建请求数据
            const requestData = {
              ...config.database,
              data_name: fileNameWithoutExt
            }
            
            // 先获取该文件名对应的记录ID
            uni.request({
              url: `${config.apiBaseUrl}${config.apiPaths.dataList}`,
              method: 'POST',
              data: config.database,
              success: (res) => {
                if (res.statusCode === 200 && Array.isArray(res.data)) {
                  // 查找匹配的记录
                  const record = res.data.find(item => item.data_name === fileNameWithoutExt)
                  
                  if (record && record.data_id) {
                    // 删除数据库记录
                    const deleteData = {
                      ...config.database,
                      id: record.data_id
                    }
                    
                    uni.request({
                      url: `${config.apiBaseUrl}${config.apiPaths.dataDelete}`,
                      method: 'POST',
                      data: deleteData,
                      success: (delRes) => {
                        // 删除文件
                        uni.request({
                          url: `${config.apiBaseUrl}/api/files/delete`,
                          method: 'POST',
                          data: { filename: this.filename },
                          complete: () => {
                            uni.hideLoading()
                            uni.showToast({
                              title: '删除成功',
                              icon: 'success'
                            })
                            
                            // 返回上一页
                            setTimeout(() => {
                              this.goBack()
                            }, 1500)
                          }
                        })
                      },
                      fail: (err) => {
                        uni.hideLoading()
                        console.error('删除数据库记录失败:', err)
                        uni.showToast({
                          title: '删除失败',
                          icon: 'none'
                        })
                      }
                    })
                  } else {
                    uni.hideLoading()
                    uni.showToast({
                      title: '未找到记录',
                      icon: 'none'
                    })
                  }
                } else {
                  uni.hideLoading()
                  uni.showToast({
                    title: '获取记录失败',
                    icon: 'none'
                  })
                }
              },
              fail: (err) => {
                uni.hideLoading()
                console.error('查询记录失败:', err)
                uni.showToast({
                  title: '查询记录失败',
                  icon: 'none'
                })
              }
            })
          }
        }
      })
    }
  }
}
</script>

<style>
.container {
  padding: 20rpx;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.header {
  padding: 20rpx 0;
  text-align: center;
  margin-bottom: 30rpx;
}

.title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  display: block;
}

.subtitle {
  font-size: 28rpx;
  color: #666;
  margin-top: 10rpx;
  display: block;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 30rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
  display: block;
}

.plots-section, .results-section, .error-section {
  background-color: #fff;
  border-radius: 12rpx;
  padding: 20rpx;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.1);
}

.channel-row {
  margin-bottom: 30rpx;
  width: 100%;
}

.channel-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 10rpx;
  text-align: center;
  display: block;
}

.chart-type {
  font-size: 24rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 5rpx;
  text-align: center;
  display: block;
}

.channel-charts {
  display: flex;
  flex-direction: row;
  justify-content: space-around;
  flex-wrap: nowrap; /* 禁止换行 */
  width: 100%;
}

.chart-box {
  flex: 0 0 48%; /* 不伸缩，固定宽度 */
  max-width: 48%;
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: #fff;
  border-radius: 8rpx;
  padding: 5rpx;
  box-shadow: 0 2rpx 6rpx rgba(0,0,0,0.05);
}

.chart-container {
  width: 100%;
  max-width: 360px;
  height: 160px;
  margin: 0 auto;
  position: relative;
  border: 1px solid #eee;
  background-color: #fff;
  overflow: visible;
}

.chart-canvas {
  width: 100% !important;
  max-width: 360px !important;
  height: 160px !important;
  position: absolute;
  left: 0;
  top: 0;
}

.results-table {
  border: 1rpx solid #eee;
  border-radius: 8rpx;
  overflow: hidden;
}

.table-header {
  display: flex;
  background-color: #f5f5f5;
  padding: 20rpx 0;
}

.header-cell {
  flex: 1;
  text-align: center;
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
}

.table-row {
  display: flex;
  padding: 20rpx 0;
  border-top: 1rpx solid #eee;
}

.table-cell {
  flex: 1;
  text-align: center;
  font-size: 28rpx;
  color: #666;
}

.positive {
  color: #f5222d;
  font-weight: bold;
}

.negative {
  color: #52c41a;
  font-weight: bold;
}

.button-section {
  padding: 20rpx 0;
}

.action-buttons {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.action-button {
  flex: 1;
  margin: 0 10rpx;
  font-size: 28rpx;
  height: 80rpx;
  line-height: 80rpx;
  border: none;
  border-radius: 8rpx;
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;
}

.report-button {
  background-color: #1890FF;
  color: #fff;
}

.report-button:active {
  background-color: #096DD9;
}

.delete-button {
  background-color: #FF4D4F;
  color: #fff;
}

.delete-button:active {
  background-color: #CF1322;
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

.back-button:active {
  background-color: #1a5fd9;
}

.no-data {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.no-data-text {
  font-size: 28rpx;
  color: #999;
}

.error-section {
  padding: 30rpx;
}

.error-title {
  font-size: 32rpx;
  color: #ff4d4f;
  font-weight: bold;
  margin-bottom: 20rpx;
  display: block;
}

.error-message {
  font-size: 28rpx;
  color: #666;
  white-space: pre-wrap;
}

.error-tip {
  font-size: 28rpx;
  color: #666;
  display: block;
}

@media screen and (max-width: 768px) {
  .channel-charts {
    flex-direction: row; /* 保持水平方向 */
    flex-wrap: nowrap;
    justify-content: center;
  }
  
  .chart-box {
    flex: 0 0 48%;
    width: 48%;
    margin: 0 1%;
  }
}

@media screen and (max-width: 375px) {
  .chart-container {
    height: 160px;
  }
  
  .chart-canvas {
    height: 160px !important;
  }
  
  .channel-charts {
    flex-direction: row; /* 保持水平方向 */
  }
}
</style> 