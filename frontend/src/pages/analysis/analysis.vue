<template>
  <view class="container">
    <view class="header">
      <text class="title">PCR数据分析结果</text>
      <text class="subtitle">{{ filename }}</text>
    </view>
    
    <view class="content">
      <!-- 调试工具栏 -->
      <view class="debug-toolbar">
        <text class="debug-info">Chart数据: {{ analysisResults && analysisResults.chart_data ? analysisResults.chart_data.length : 0 }}项</text>
        <text class="debug-info">{{ debugInfo }}</text>
        <button class="debug-button" @tap="checkCanvasElements">检查Canvas</button>
        <button class="debug-button" @tap="forceRender">强制渲染</button>
      </view>
      
      <!-- 测试画布区域 -->
      <view class="test-canvas-section">
        <text class="section-title">测试画布</text>
        <view class="test-canvas-wrapper" style="position: relative; width: 300px; height: 200px; margin: 0 auto; border: 1px solid #ddd;">
          <canvas 
            canvas-id="testCanvas"
            id="testCanvas"
            class="test-canvas"
            style="width: 300px; height: 200px; position: absolute; left: 0; top: 0; z-index: 1;"
          ></canvas>
        </view>
        <view class="button-group">
          <button class="test-button" @tap="testBasicDraw">测试基础绘图</button>
          <button class="test-button" @tap="testComplexDraw">测试复杂绘图</button>
        </view>
      </view>
      
      <!-- 图表展示区域 -->
      <view class="plots-section">
        <text class="section-title">扩增曲线</text>
        <view v-if="analysisResults && analysisResults.chart_data && analysisResults.chart_data.length > 0" class="plots-grid">
          <view v-for="(chartData, index) in analysisResults.chart_data" :key="index" class="plot-container">
            <view class="chart-title">{{ `通道${chartData.channel} - ${chartData.type}` }}</view>
            <view class="chart-wrapper" :id="`chartWrapper_${index}`">
              <canvas 
                :canvas-id="`pcrChart_${index}`" 
                :id="`pcrChart_${index}`"
                class="chart-canvas"
                style="width: 300px; height: 300px;"
                @touchstart="onTouchStart"
                @touchmove="onTouchMove"
                @touchend="onTouchEnd">
              </canvas>
            </view>
            <view class="chart-info" v-if="chartData.ct_value">
              <text class="ct-value">CT值: {{ chartData.ct_value.toFixed(1) }}</text>
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
        <view class="results-table">
          <view class="table-header">
            <text class="header-cell">通道</text>
            <text class="header-cell">类型</text>
            <text class="header-cell">结果</text>
            <text class="header-cell">CT值</text>
          </view>
          <view v-for="(result, index) in analysisResults?.results" :key="index" class="table-row">
            <text class="table-cell">{{ result.channel }}</text>
            <text class="table-cell">{{ result.type }}</text>
            <text class="table-cell" :class="{ 'positive': result.positive, 'negative': !result.positive }">
              {{ result.positive ? '阳性' : '阴性' }}
            </text>
            <text class="table-cell">{{ result.ct_value ? result.ct_value.toFixed(1) : '-' }}</text>
          </view>
        </view>
      </view>
      
      <!-- 返回按钮 -->
      <view class="button-section">
        <button class="back-button" @tap="goBack">返回文件列表</button>
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
      analysisResults: {
        chart_data: [],
        results: []
      },
      charts: [],
      chartColors: ['#FF0000', '#00AA00', '#0000FF', '#FF00FF'],
      canvasContext: null,
      touches: {},
      chartsRendered: false,
      debugInfo: '等待数据'
    }
  },
  
  onLoad(options) {
    console.log('页面加载 onLoad，参数:', options);
    
    // 确保analysisResults已初始化为对象
    if (!this.analysisResults) {
      console.log('初始化analysisResults');
      this.analysisResults = {
        chart_data: [],
        results: []
      };
    }
    
    if (options.filename) {
      this.filename = options.filename;
      this.debugInfo = '正在加载: ' + options.filename;
      
      // 首先检查API状态
      console.log('检查API状态');
      this.checkApiStatus().then(() => {
        console.log('API状态正常，加载分析结果');
        this.loadAnalysisResults(options.filename);
      }).catch((err) => {
        // API状态检查失败，直接尝试加载
        console.log('API状态检查失败，直接加载分析结果', err);
        this.loadAnalysisResults(options.filename);
      });
    } else {
      console.error('缺少filename参数');
      this.debugInfo = '错误: 缺少文件名参数';
    }
  },
  
  // 当页面初次渲染完成
  onReady() {
    console.log('页面已准备完毕 onReady')
    
    // 确保页面元素已经渲染
    setTimeout(() => {
      // 检查是否已有数据
      if (this.analysisResults && this.analysisResults.chart_data) {
        console.log('onReady: 数据已存在，主动触发图表渲染')
        this.renderCharts()
      } else {
        console.log('onReady: 尚无数据，等待数据加载')
      }
    }, 300)
  },
  
  // 页面显示时
  onShow() {
    console.log('页面显示 onShow')
    
    // 如果已有数据但尚未渲染图表，尝试渲染
    if (this.analysisResults && this.analysisResults.chart_data && !this.chartsRendered) {
      console.log('onShow: 检测到未渲染的数据，触发图表渲染')
      setTimeout(() => {
        this.renderCharts()
      }, 300)
    }
  },
  
  // 监听数据变化
  watch: {
    analysisResults: {
      handler(newVal) {
        // 当分析结果数据更新后，重新渲染图表
        if (newVal && newVal.chart_data) {
          console.log('watch: 分析结果数据更新，准备渲染图表')
          this.chartsRendered = false
          this.$nextTick(() => {
            setTimeout(() => {
              console.log('watch: 延迟渲染图表')
              this.renderCharts()
            }, 300)
          })
        }
      },
      deep: true
    }
  },
  
  methods: {
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
        this.debugInfo = '正在加载数据...';
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
          // 输出数据结构以便调试
          console.log('返回数据结构分析:\n            数据类型:', typeof response.data,
                     '\n            包含plots?:', !!response.data.plots,
                     '\n            包含results?:', !!response.data.results, 
                     response.data.results ? `，有${response.data.results.length}个结果` : '',
                     '\n            包含chart_data?:', !!response.data.chart_data, 
                     response.data.chart_data ? `，有${response.data.chart_data.length}个图表数据` : '',
                     '\n            chart_data样本:', response.data.chart_data && response.data.chart_data.length > 0 ? 
                        JSON.stringify(response.data.chart_data[0]).substring(0, 100) + '...' : '无'
                    );
          
          // ===== 添加检查点 =====
          console.log('准备进入处理数据代码块，检查点1');
          
          try {
            console.log('准备处理和渲染数据，检查点2');
            
            // 检查response.data的完整性
            if (!response.data) {
              console.error('response.data为空，检查点3A');
              throw new Error('返回数据为空');
            }
            
            console.log('response.data类型:', typeof response.data, '检查点3B');
            
            // 保存分析结果
            try {
              console.log('准备保存分析结果，检查点4');
              this.analysisResults = JSON.parse(JSON.stringify(response.data)); // 深拷贝避免引用问题
              console.log('分析结果已保存，检查点5');
            } catch (copyError) {
              console.error('复制分析结果时出错:', copyError, '检查点5E');
              this.analysisResults = response.data; // 退回到直接赋值
            }
            
            this.debugInfo = `已加载数据: ${this.analysisResults.chart_data ? this.analysisResults.chart_data.length : 0}项`;
            console.log('已保存分析结果到this.analysisResults，检查点6');
            
            // 立即检查是否确实存在chart_data
            console.log('开始检查chart_data，检查点7');
            if (this.analysisResults.chart_data && this.analysisResults.chart_data.length > 0) {
              console.log('确认chart_data存在，共', this.analysisResults.chart_data.length, '项，检查点8A');
              console.log('第一项数据类型:', this.analysisResults.chart_data[0] ? typeof this.analysisResults.chart_data[0] : '无数据');
            } else {
              console.error('chart_data不存在或为空，检查点8B');
              // 创建测试数据用于调试
              console.log('准备创建测试数据，检查点9');
              this.createTestData();
              console.log('测试数据创建完成，检查点10');
            }
            
            // 强制触发图表渲染 - 使用直接调用而非setTimeout
            console.log('直接调用renderCharts()，检查点11');
            try {
              this.renderCharts();
              console.log('renderCharts()调用完成，检查点12');
            } catch (renderError) {
              console.error('renderCharts直接调用错误:', renderError, '错误堆栈:', renderError.stack, '检查点12E');
            }
            
            // 为确保DOM已更新，也使用setTimeout调用
            console.log('设置延迟渲染，检查点13');
            setTimeout(() => {
              console.log('执行延迟渲染，检查点14');
              try {
                this.renderCharts();
                console.log('延迟渲染完成，检查点15');
              } catch (delayedRenderError) {
                console.error('延迟renderCharts调用错误:', delayedRenderError, '检查点15E');
              }
            }, 500);
            
            console.log('所有处理逻辑已执行，检查点16');
          } catch (e) {
            console.error('触发渲染时出错:', e, '错误堆栈:', e.stack, '检查点ERR');
            this.debugInfo = `渲染错误: ${e.message}`;
          }
          
          console.log('数据处理完成，检查点FINAL');
        } else {
          console.error(`请求失败: 状态码=${response.statusCode}`, response.data);
          this.debugInfo = `请求失败: ${response.statusCode}`;
          
          // 检查是否需要重试
          if (retryCount < 2) {
            console.log(`尝试重新请求 (${retryCount + 1}/2)...`);
            setTimeout(() => {
              this.loadAnalysisResults(filename, retryCount + 1);
            }, 1000);
            return;
          }
          
          uni.showToast({
            title: '获取分析结果失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('获取分析结果错误:', error);
        this.debugInfo = `加载错误: ${error.message}`;
        
        // 检查是否需要重试
        if (retryCount < 2) {
          console.log(`出错后尝试重新请求 (${retryCount + 1}/2)...`);
          setTimeout(() => {
            this.loadAnalysisResults(filename, retryCount + 1);
          }, 1000);
          return;
        }
        
        uni.showToast({
          title: '获取分析结果失败',
          icon: 'none'
        })
      } finally {
        uni.hideLoading()
      }
    },
    
    // 创建测试数据用于调试
    createTestData() {
      console.log('创建测试数据');
      this.debugInfo = '使用测试数据';
      
      // 如果this.analysisResults不存在或不是对象，初始化它
      if (!this.analysisResults || typeof this.analysisResults !== 'object') {
        this.analysisResults = {};
      }
      
      // 创建一些随机数据点
      const createRandomData = (length, base) => {
        return Array.from({length}, (_, i) => {
          if (i < 10) return base + Math.random() * 100;
          else if (i < 20) return base + 100 + i * 20 + Math.random() * 200;
          else return base + 500 + Math.random() * 300;
        });
      };
      
      // 设置测试chart_data
      this.analysisResults.chart_data = [
        {
          channel: 1,
          type: 'FAM',
          raw_data: createRandomData(40, 100),
          threshold: 800,
          ct_value: 22.5
        },
        {
          channel: 1,
          type: 'VIC',
          raw_data: createRandomData(40, 200),
          threshold: 800,
          ct_value: null
        },
        {
          channel: 2,
          type: 'FAM',
          raw_data: createRandomData(40, 150),
          threshold: 800,
          ct_value: 18.7
        },
        {
          channel: 2,
          type: 'VIC',
          raw_data: createRandomData(40, 250),
          threshold: 800,
          ct_value: null
        }
      ];
      
      // 设置测试results
      this.analysisResults.results = [
        { channel: 1, type: 'FAM', positive: true, ct_value: 22.5 },
        { channel: 1, type: 'VIC', positive: false, ct_value: null },
        { channel: 2, type: 'FAM', positive: true, ct_value: 18.7 },
        { channel: 2, type: 'VIC', positive: false, ct_value: null }
      ];
      
      console.log('测试数据已创建，chart_data:', this.analysisResults.chart_data.length, '项');
    },
    
    // 渲染所有图表
    renderCharts() {
      try {
        console.log('renderCharts被调用，检查点RC1');
        
        if (!this.analysisResults) {
          console.error('this.analysisResults为空，检查点RC2A');
          return;
        }
        
        if (!this.analysisResults.chart_data) {
          console.error('this.analysisResults.chart_data为空，检查点RC2B');
          return;
        }
        
        console.log('开始渲染图表，数据集数量:', this.analysisResults.chart_data.length, 
                    '第一条数据:', this.analysisResults.chart_data[0] ? 
                    `通道${this.analysisResults.chart_data[0].channel}-${this.analysisResults.chart_data[0].type}` : '无', '检查点RC3');
        
        // 标记图表渲染状态
        this.chartsRendered = true;
        
        // 检查Canvas元素是否存在
        console.log('准备检查Canvas元素，检查点RC4');
        try {
          console.log('执行创建SelectorQuery，检查点RC5');
          const query = uni.createSelectorQuery();
          console.log('执行selectAll，检查点RC6');
          query.selectAll('.chart-canvas')
            .boundingClientRect(rects => {
              console.log('Canvas元素数量:', rects ? rects.length : 0, 
                        '详情:', JSON.stringify(rects ? rects.slice(0, 2) : []), '检查点RC7');
              
              if (!rects || rects.length === 0) {
                console.error('找不到Canvas元素，DOM可能未更新，检查点RC8A');
                this.debugInfo = '找不到Canvas元素';
                this.chartsRendered = false;
                
                // 强制DOM更新后重试
                console.log('强制更新DOM，检查点RC9');
                this.$forceUpdate();
                setTimeout(() => {
                  console.log('强制DOM更新后重试渲染，检查点RC10');
                  try {
                    this.renderPCRCharts();
                    console.log('重试渲染完成，检查点RC11');
                  } catch (retryError) {
                    console.error('重试渲染出错:', retryError, '检查点RC11E');
                  }
                }, 300);
                return;
              }
              
              // 直接渲染图表
              console.log('找到Canvas元素，调用renderPCRCharts()，检查点RC12');
              try {
                this.renderPCRCharts();
                console.log('renderPCRCharts调用完成，检查点RC13');
              } catch (pcrError) {
                console.error('renderPCRCharts调用出错:', pcrError, '检查点RC13E');
              }
            });
          
          console.log('准备执行query.exec()，检查点RC14');
          query.exec();
          console.log('query.exec()执行完成，检查点RC15');
        } catch (e) {
          console.error('检查Canvas元素时出错:', e, '检查点RC16E');
          this.debugInfo = '检查Canvas出错: ' + e.message;
          // 如果查询失败，也尝试直接渲染
          console.log('尝试直接渲染，检查点RC17');
          try {
            this.renderPCRCharts();
            console.log('直接渲染完成，检查点RC18');
          } catch (directError) {
            console.error('直接渲染出错:', directError, '检查点RC18E');
          }
        }
        
        console.log('renderCharts方法执行完毕，检查点RC19');
      } catch (e) {
        console.error('renderCharts方法错误:', e, '错误堆栈:', e.stack, '检查点RC20E');
        this.debugInfo = '渲染出错: ' + e.message;
        this.chartsRendered = false;
      }
    },
    
    // 使用uni.createCanvasContext渲染所有PCR图表
    renderPCRCharts() {
      try {
        console.log('开始逐个渲染PCR图表，共', this.analysisResults.chart_data.length, '个，检查点PCR1');
        this.debugInfo = `开始渲染${this.analysisResults.chart_data.length}个图表`;
        
        // 清空现有图表
        this.charts = [];
        
        // 判断是否有数据可渲染
        if (!this.analysisResults || !this.analysisResults.chart_data || this.analysisResults.chart_data.length === 0) {
          console.error('没有有效的图表数据可渲染，检查点PCR2E');
          this.debugInfo = '没有有效图表数据';
          
          // 如果没有数据，尝试创建测试数据
          console.log('尝试创建测试数据，检查点PCR3');
          try {
            this.createTestData();
            console.log('测试数据创建完成，检查点PCR4');
          } catch (testDataError) {
            console.error('创建测试数据出错:', testDataError, '检查点PCR4E');
          }
          
          if (!this.analysisResults || !this.analysisResults.chart_data || this.analysisResults.chart_data.length === 0) {
            console.error('即使创建测试数据后仍然没有图表数据，检查点PCR5E');
            this.debugInfo = '无法创建测试数据';
            return;
          }
        }
        
        // 延迟执行绘制，确保DOM已渲染
        console.log('设置延迟执行绘制，检查点PCR6');
        setTimeout(() => {
          console.log('开始延迟执行绘制，检查点PCR7');
          // 使用简单非交互式方式绘制所有图表
          try {
            this.drawAllChartsSimple();
            console.log('绘制完成，检查点PCR8');
          } catch (drawError) {
            console.error('绘制出错:', drawError, '检查点PCR8E');
            this.debugInfo = '绘制出错: ' + drawError.message;
          }
        }, 200);
        
        console.log('renderPCRCharts方法执行完毕，检查点PCR9');
      } catch (e) {
        console.error('渲染PCR图表错误:', e, e.stack, '检查点PCR10E');
        this.debugInfo = `渲染错误: ${e.message}`;
      }
    },
    
    // 简单非交互式绘制所有图表
    drawAllChartsSimple() {
      console.log('drawAllChartsSimple被调用');
      
      if (!this.analysisResults || !this.analysisResults.chart_data) {
        console.error('没有图表数据');
        return;
      }
      
      console.log('使用简单模式绘制所有图表，共', this.analysisResults.chart_data.length, '个');
      
      try {
        this.analysisResults.chart_data.forEach((chartData, index) => {
          try {
            // 获取Canvas上下文
            const canvasId = `pcrChart_${index}`;
            console.log(`绘制图表 ${index}`, canvasId);
            
            const ctx = uni.createCanvasContext(canvasId, this);
            if (!ctx) {
              console.error(`无法获取Canvas上下文: ${canvasId}`);
              return;
            }
            
            console.log(`成功获取Canvas上下文: ${canvasId}`);
            
            // 绘制简单图表
            this.drawSimpleChart(ctx, chartData, index);
          } catch (e) {
            console.error(`绘制图表 ${index} 错误:`, e);
          }
        });
      } catch (e) {
        console.error('绘制所有图表出错:', e);
      }
    },
    
    // 绘制简单图表
    drawSimpleChart(ctx, chartData, index) {
      try {
        console.log(`开始绘制简单图表 ${index}`);
        
        // 清空画布
        ctx.clearRect(0, 0, 300, 300);
        
        // 设置背景
        ctx.setFillStyle('#f8f9fa');
        ctx.fillRect(0, 0, 300, 300);
        
        // 绘制边框和标题
        ctx.setFillStyle('#ffffff');
        ctx.fillRect(10, 30, 280, 260);
        
        ctx.setStrokeStyle('#dddddd');
        ctx.strokeRect(10, 30, 280, 260);
        
        // 绘制标题
        ctx.setFillStyle('#333333');
        ctx.setFontSize(16);
        ctx.setTextAlign('center');
        ctx.fillText(`通道${chartData.channel} - ${chartData.type}`, 150, 20);
        
        // 检查数据
        if (!chartData.raw_data || !Array.isArray(chartData.raw_data) || chartData.raw_data.length === 0) {
          ctx.setFillStyle('#999999');
          ctx.setTextAlign('center');
          ctx.setFontSize(14);
          ctx.fillText('无数据', 150, 150);
          ctx.draw(); // 一次性绘制
          return;
        }
        
        // 计算参数
        const padding = { left: 40, right: 20, top: 40, bottom: 30 };
        const chartWidth = 300 - padding.left - padding.right;
        const chartHeight = 300 - padding.top - padding.bottom;
        
        // 获取数据
        const rawData = chartData.raw_data;
        
        // 计算数据范围
        const maxValue = Math.max(...rawData, 1000);
        const xScale = chartWidth / (rawData.length - 1);
        const yScale = chartHeight / maxValue;
        
        // 绘制坐标轴
        ctx.setStrokeStyle('#999999');
        ctx.setLineWidth(1);
        
        // X轴
        ctx.beginPath();
        ctx.moveTo(padding.left, 300 - padding.bottom);
        ctx.lineTo(300 - padding.right, 300 - padding.bottom);
        ctx.stroke();
        
        // Y轴
        ctx.beginPath();
        ctx.moveTo(padding.left, padding.top);
        ctx.lineTo(padding.left, 300 - padding.bottom);
        ctx.stroke();
        
        // 绘制网格线
        ctx.setStrokeStyle('#eeeeee');
        ctx.setLineWidth(0.5);
        
        // 水平网格线
        for (let i = 1; i <= 4; i++) {
          ctx.beginPath();
          const y = 300 - padding.bottom - (i * chartHeight / 4);
          ctx.moveTo(padding.left, y);
          ctx.lineTo(300 - padding.right, y);
          ctx.stroke();
        }
        
        // 垂直网格线
        for (let i = 1; i <= 4; i++) {
          ctx.beginPath();
          const x = padding.left + (i * chartWidth / 4);
          ctx.moveTo(x, padding.top);
          ctx.lineTo(x, 300 - padding.bottom);
          ctx.stroke();
        }
        
        // 绘制数据线
        ctx.beginPath();
        ctx.setStrokeStyle(chartData.type === 'FAM' ? '#FF6600' : '#0066FF');
        ctx.setLineWidth(2);
        
        // 采样数据点以减轻绘图负担
        const sampleInterval = Math.max(1, Math.floor(rawData.length / 20));
        const samplePoints = [];
        for (let i = 0; i < rawData.length; i += sampleInterval) {
          samplePoints.push(rawData[i]);
        }
        
        // 确保采样点数量足够
        if (samplePoints.length < 2) {
          samplePoints.push(rawData[rawData.length - 1]);
        }
        
        // 绘制折线
        for (let i = 0; i < samplePoints.length; i++) {
          const x = padding.left + i * (chartWidth / (samplePoints.length - 1));
          const y = 300 - padding.bottom - (samplePoints[i] * yScale);
          
          if (i === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        }
        
        ctx.stroke();
        
        // 绘制阈值线
        ctx.beginPath();
        ctx.setStrokeStyle('#999999');
        ctx.setLineWidth(1);
        ctx.setLineDash([5, 5]);
        const thresholdY = 300 - padding.bottom - (800 * yScale);
        ctx.moveTo(padding.left, thresholdY);
        ctx.lineTo(300 - padding.right, thresholdY);
        ctx.stroke();
        ctx.setLineDash([]);
        
        // 绘制阈值文本
        ctx.setFillStyle('#999999');
        ctx.setFontSize(10);
        ctx.setTextAlign('right');
        ctx.fillText('阈值=800', 280, thresholdY - 5);
        
        // 如果有CT值，标记出来
        if (chartData.ct_value) {
          const ctX = padding.left + (chartData.ct_value / rawData.length) * chartWidth;
          
          // CT线
          ctx.beginPath();
          ctx.setStrokeStyle('#33cc33');
          ctx.setLineWidth(1);
          ctx.setLineDash([5, 5]);
          ctx.moveTo(ctX, padding.top);
          ctx.lineTo(ctX, 300 - padding.bottom);
          ctx.stroke();
          ctx.setLineDash([]);
          
          // CT点
          ctx.beginPath();
          ctx.setFillStyle('#33cc33');
          ctx.arc(ctX, thresholdY, 4, 0, Math.PI * 2);
          ctx.fill();
          
          // CT文本
          ctx.setFillStyle('#009900');
          ctx.setFontSize(12);
          ctx.setTextAlign('center');
          ctx.fillText(`CT=${chartData.ct_value.toFixed(1)}`, ctX, thresholdY - 10);
        }
        
        // 一次性绘制
        ctx.draw();
        console.log(`图表 ${index} 绘制完成`);
        
        // 更新调试信息
        this.debugInfo = `已绘制 ${index + 1} 个图表`;
      } catch (e) {
        console.error(`绘制简单图表 ${index} 错误:`, e);
        this.debugInfo = `绘图错误: ${e.message}`;
      }
    },
    
    // 触摸事件处理
    onTouchStart(e) {
      const touch = e.touches[0]
      this.touches.startX = touch.x
      this.touches.startY = touch.y
    },
    
    onTouchMove(e) {
      // 可以添加拖动交互
    },
    
    onTouchEnd(e) {
      // 可以添加点击事件处理
    },
    
    goBack() {
      uni.navigateBack()
    },
    
    // 新增方法：测试基础绘图功能
    testBasicDraw() {
      try {
        console.log('执行基础绘图测试');
        this.debugInfo = '执行基础绘图测试';
        
        // 获取Canvas上下文
        const ctx = uni.createCanvasContext('testCanvas', this);
        
        if (!ctx) {
          console.error('无法获取测试画布上下文');
          this.debugInfo = '无法获取画布上下文';
          return;
        }
        
        // 测试clearRect
        ctx.clearRect(0, 0, 300, 200);
        
        // 测试setFillStyle和fillRect
        ctx.setFillStyle('#00AAFF');
        ctx.fillRect(0, 0, 300, 200);
        
        ctx.setFillStyle('#FFFFFF');
        ctx.fillRect(10, 10, 280, 180);
        
        // 测试文本绘制
        ctx.setFillStyle('#333333');
        ctx.setFontSize(20);
        ctx.setTextAlign('center');
        ctx.fillText('测试成功', 150, 100);
        
        // 执行绘制
        ctx.draw(false, () => {
          console.log('基础绘图测试完成');
          this.debugInfo = '基础绘图测试完成';
        });
      } catch (e) {
        console.error('基础绘图测试失败:', e);
        this.debugInfo = `绘图测试失败: ${e.message}`;
      }
    },
    
    // 测试复杂绘图功能
    testComplexDraw() {
      try {
        console.log('执行复杂绘图测试');
        const ctx = uni.createCanvasContext('testCanvas', this);
        
        if (!ctx) {
          console.error('无法获取测试画布上下文');
          return;
        }
        
        // 绘制测试图表
        this.drawTestChart(ctx);
      } catch (e) {
        console.error('复杂绘图测试失败:', e);
      }
    },
    
    drawTestChart(ctx) {
      // 设置画布尺寸和边距
      const width = 300;
      const height = 200;
      const padding = { top: 20, right: 20, bottom: 30, left: 40 };
      
      // 计算绘图区域尺寸
      const chartWidth = width - padding.left - padding.right;
      const chartHeight = height - padding.top - padding.bottom;
      
      // 清空画布
      ctx.clearRect(0, 0, width, height);
      
      // 设置背景
      ctx.setFillStyle('#f5f5f5');
      ctx.fillRect(0, 0, width, height);
      
      // 绘制网格线
      ctx.beginPath();
      ctx.setStrokeStyle('#ddd');
      ctx.setLineWidth(0.5);
      
      // 水平网格线
      for (let i = 0; i <= 5; i++) {
        const y = padding.top + (i * chartHeight / 5);
        ctx.moveTo(padding.left, y);
        ctx.lineTo(width - padding.right, y);
      }
      
      // 垂直网格线
      for (let i = 0; i <= 5; i++) {
        const x = padding.left + (i * chartWidth / 5);
        ctx.moveTo(x, padding.top);
        ctx.lineTo(x, height - padding.bottom);
      }
      
      ctx.stroke();
      
      // 执行绘制以确保网格线显示
      ctx.draw(true);
      
      // 生成测试数据
      const testData = Array.from({ length: 20 }, (_, i) => 
        Math.sin(i * 0.5) * 40 + 50 + Math.random() * 10
      );
      
      // 计算比例
      const xScale = chartWidth / (testData.length - 1);
      const yScale = chartHeight / 100;
      
      // 绘制数据线
      ctx.beginPath();
      ctx.setStrokeStyle('#FF6600');
      ctx.setLineWidth(2);
      
      for (let i = 0; i < testData.length; i++) {
        const x = padding.left + i * xScale;
        const y = height - padding.bottom - testData[i] * yScale;
        
        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }
      
      ctx.stroke();
      
      // 执行绘制以确保数据线显示
      ctx.draw(true);
      
      // 绘制轴线
      ctx.beginPath();
      ctx.setStrokeStyle('#333');
      ctx.setLineWidth(1);
      
      // X轴
      ctx.moveTo(padding.left, height - padding.bottom);
      ctx.lineTo(width - padding.right, height - padding.bottom);
      
      // Y轴
      ctx.moveTo(padding.left, padding.top);
      ctx.lineTo(padding.left, height - padding.bottom);
      
      ctx.stroke();
      
      // 绘制标签
      ctx.setFillStyle('#333');
      ctx.setFontSize(12);
      ctx.setTextAlign('center');
      
      // X轴标签
      for (let i = 0; i <= 5; i++) {
        const x = padding.left + (i * chartWidth / 5);
        const label = (i * 4).toString();
        ctx.fillText(label, x, height - padding.bottom + 15);
      }
      
      // Y轴标签
      ctx.setTextAlign('right');
      for (let i = 0; i <= 5; i++) {
        const y = padding.top + (i * chartHeight / 5);
        const label = (100 - i * 20).toString();
        ctx.fillText(label, padding.left - 5, y + 4);
      }
      
      // 绘制标题
      ctx.setFillStyle('#000');
      ctx.setFontSize(14);
      ctx.setTextAlign('center');
      ctx.fillText('测试曲线图', width / 2, 14);
      
      // 最终执行绘制
      ctx.draw(true, () => {
        console.log('复杂绘图测试完成');
      });
    },
    
    // 新方法：检查Canvas元素
    checkCanvasElements() {
      console.log('手动检查Canvas元素');
      this.debugInfo = '检查Canvas元素中...';
      
      try {
        // 先列出所有画布ID
        console.log('检查画布ID：');
        if (this.analysisResults && this.analysisResults.chart_data) {
          this.analysisResults.chart_data.forEach((data, index) => {
            console.log(`画布${index}: pcrChart_${index}`);
          });
        }
        
        // 查询所有Canvas元素
        uni.createSelectorQuery()
          .selectAll('.chart-canvas')
          .boundingClientRect(rects => {
            console.log('Canvas元素查询结果:', rects ? rects.length : 0, '个元素');
            
            if (rects && rects.length > 0) {
              this.debugInfo = `找到${rects.length}个Canvas元素`;
              rects.forEach((rect, i) => {
                console.log(`Canvas #${i}:`, rect.width, 'x', rect.height, 
                          rect.left, rect.top, rect.id || '无ID');
              });
              
              // 尝试获取第一个元素的上下文并绘制测试图形
              for (let i = 0; i < Math.min(rects.length, 2); i++) {
                const canvasId = `pcrChart_${i}`;
                try {
                  console.log(`尝试获取${canvasId}上下文`);
                  const ctx = uni.createCanvasContext(canvasId, this);
                  if (ctx) {
                    console.log(`Canvas上下文测试成功: ${canvasId}`);
                    this.debugInfo = `Canvas上下文测试成功: ${canvasId}`;
                    
                    // 绘制测试标记
                    ctx.setFillStyle('#FF0000');
                    ctx.fillRect(0, 0, 50, 50);
                    
                    ctx.setFillStyle('#FFFFFF');
                    ctx.setFontSize(20);
                    ctx.setTextAlign('center');
                    ctx.fillText(`测试${i+1}`, 25, 30);
                    
                    // 一次性绘制
                    ctx.draw(false, (res) => {
                      console.log(`Canvas ${canvasId} 测试绘制完成:`, res || '成功');
                    });
                  } else {
                    console.error(`无法获取${canvasId}上下文`);
                    this.debugInfo = `无法获取${canvasId}上下文`;
                  }
                } catch (e) {
                  console.error(`获取${canvasId}上下文出错:`, e);
                  this.debugInfo = `上下文错误: ${e.message}`;
                }
              }
            } else {
              console.error('未找到任何Canvas元素');
              this.debugInfo = '未找到Canvas元素';
              
              // 检查DOM结构
              this.inspectDOM();
            }
          })
          .exec();
      } catch (e) {
        console.error('检查Canvas元素出错:', e);
        this.debugInfo = `检查出错: ${e.message}`;
      }
    },
    
    // 检查DOM结构
    inspectDOM() {
      console.log('检查DOM结构');
      
      uni.createSelectorQuery()
        .selectAll('.plot-container')
        .boundingClientRect(rects => {
          console.log('图表容器数量:', rects ? rects.length : 0);
          
          if (rects && rects.length > 0) {
            // 检查每个容器内的结构
            uni.createSelectorQuery()
              .selectAll('.chart-wrapper')
              .boundingClientRect(wrappers => {
                console.log('图表包装器数量:', wrappers ? wrappers.length : 0);
                
                if (!wrappers || wrappers.length === 0) {
                  console.error('没有找到.chart-wrapper元素');
                  this.debugInfo = '缺少chart-wrapper元素';
                }
              })
              .exec();
          } else {
            console.error('没有找到.plot-container元素');
            this.debugInfo = '缺少plot-container元素';
          }
        })
        .exec();
    },
    
    // 新方法：强制渲染
    forceRender() {
      console.log('用户手动触发渲染');
      this.debugInfo = '手动触发渲染';
      
      try {
        // 确保有数据可渲染
        if (!this.analysisResults || !this.analysisResults.chart_data || this.analysisResults.chart_data.length === 0) {
          console.log('没有图表数据，创建测试数据');
          this.createTestData();
        }
        
        // 先检查Canvas元素
        this.checkCanvasElements();
        
        // 强制更新视图
        this.$forceUpdate();
        
        // 延迟后再渲染
        setTimeout(() => {
          console.log('强制DOM更新后渲染');
          this.drawAllChartsSimple();
        }, 300);
      } catch (e) {
        console.error('强制渲染出错:', e, e.stack);
        this.debugInfo = `强制渲染错误: ${e.message}`;
        
        uni.showToast({
          title: '渲染出错: ' + e.message,
          icon: 'none'
        });
      }
    },
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

.plots-section, .results-section {
  background-color: #fff;
  border-radius: 12rpx;
  padding: 20rpx;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.1);
}

.plots-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
}

.plot-container {
  background-color: #fff;
  border-radius: 8rpx;
  overflow: hidden;
  padding: 10rpx;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2rpx 6rpx rgba(0,0,0,0.05);
  height: 340px; /* 固定高度，确保canvas有足够空间 */
  position: relative; /* 添加相对定位 */
}

.chart-title {
  font-size: 26rpx;
  font-weight: bold;
  color: #333;
  text-align: center;
  margin-bottom: 10rpx;
  height: 30px; /* 固定高度 */
}

.chart-wrapper {
  width: 300px;
  height: 300px;
  margin: 0 auto;
  position: relative; /* 确保相对定位 */
  border: 1px solid #eee; /* 添加边框 */
  background-color: #f8f9fa; /* 添加背景色 */
}

.chart-canvas {
  width: 300px;
  height: 300px;
  position: absolute; /* 绝对定位 */
  left: 0;
  top: 0;
  z-index: 1; /* 确保画布在最上层 */
}

.chart-info {
  text-align: center;
  margin-top: 10rpx;
}

.ct-value {
  font-size: 24rpx;
  color: #009900;
  font-weight: bold;
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
}

.button-section {
  display: flex;
  justify-content: center;
  margin-top: 20rpx;
}

.back-button {
  background-color: #2871FA;
  color: #fff;
  border-radius: 8rpx;
  padding: 20rpx 60rpx;
  font-size: 28rpx;
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

.test-canvas-section {
  background-color: #fff;
  border-radius: 12rpx;
  padding: 20rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.1);
}

.test-canvas-wrapper {
  width: 300px;
  height: 200px;
  margin: 0 auto;
  position: relative;
  border: 1px solid #ddd;
  background-color: #f5f5f5;
}

.test-canvas {
  width: 300px;
  height: 200px;
  position: absolute;
  left: 0;
  top: 0;
  z-index: 1;
}

.button-group {
  display: flex;
  justify-content: center;
  margin-top: 15rpx;
  gap: 20rpx;
}

.test-button {
  background-color: #2871FA;
  color: #fff;
  font-size: 24rpx;
  padding: 10rpx 20rpx;
  border-radius: 6rpx;
  min-width: 120rpx;
}

.debug-toolbar {
  background-color: #fff;
  padding: 10rpx;
  margin-bottom: 10rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 8rpx;
  box-shadow: 0 2rpx 6rpx rgba(0,0,0,0.1);
}

.debug-info {
  font-size: 24rpx;
  color: #666;
  flex: 1;
}

.debug-button {
  font-size: 22rpx;
  padding: 6rpx 12rpx;
  margin: 0 6rpx;
  background-color: #2871FA;
  color: #fff;
  border-radius: 6rpx;
  line-height: 1.5;
  min-width: auto;
  height: auto;
}
</style> 