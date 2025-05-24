<template>
  <view class="container">
    <view class="header">
      <text class="title">PCR数据分析</text>
    </view>
    
    <view class="content">
      <view class="file-list">
        <text class="section-title">数据文件列表</text>
        <scroll-view scroll-y class="file-scroll">
          <view v-for="(file, index) in fileList" :key="index" 
                class="file-item">
            <text class="file-name">{{ file }}</text>
            <view class="view-button" @tap="selectFile(file)">查看</view>
          </view>
        </scroll-view>
      </view>
      
      <view class="results" v-if="analysisResults">
        <text class="section-title">分析结果</text>
        <view v-if="analysisResults.chart_data && analysisResults.chart_data.length > 0" class="plots-grid">
          <view v-for="(chartData, index) in analysisResults.chart_data" :key="index" class="plot-container">
            <view class="chart-title">{{ `通道${chartData.channel} - ${chartData.type}` }}</view>
            <view class="chart-wrapper">
              <canvas 
                :canvas-id="`pcrChart_${index}`" 
                :id="`pcrChart_${index}`"
                class="chart-canvas">
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
        
        <view class="results-table">
          <view class="table-header">
            <text class="header-cell">通道</text>
            <text class="header-cell">类型</text>
            <text class="header-cell">结果</text>
            <text class="header-cell">CT值</text>
          </view>
          <view v-for="(result, index) in analysisResults.results" :key="index" class="table-row">
            <text class="table-cell">{{ result.channel }}</text>
            <text class="table-cell">{{ result.type }}</text>
            <text class="table-cell" :class="{ 'positive': result.positive }">
              {{ result.positive ? '阳性' : '阴性' }}
            </text>
            <text class="table-cell">{{ result.ct_value ? result.ct_value.toFixed(1) : '-' }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import config from '@/config/config.js'

export default {
  data() {
    return {
      fileList: [],
      analysisResults: null,
      charts: [],
      chartColors: ['#FF0000', '#00AA00', '#0000FF', '#FF00FF']
    }
  },
  
  onLoad() {
    this.loadFileList()
  },
  
  // 当数据更新时重新渲染图表
  watch: {
    analysisResults: {
      handler(newVal) {
        if (newVal && newVal.chart_data) {
          console.log('分析结果数据更新，准备渲染图表')
          this.$nextTick(() => {
            setTimeout(() => {
              this.renderCharts()
            }, 500)
          })
        }
      },
      deep: true
    }
  },
  
  methods: {
    async loadFileList() {
      try {
        const response = await uni.request({
          url: `${config.apiBaseUrl}${config.apiPaths.files}`,
          method: 'GET'
        })
        
        if (response.statusCode === 200) {
          this.fileList = response.data.files
        } else {
          uni.showToast({
            title: '获取文件列表失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('加载文件列表错误:', error)
        uni.showToast({
          title: '加载文件列表失败',
          icon: 'none'
        })
      }
    },
    
    selectFile(filename) {
      console.log(`跳转到分析页面，文件名: ${filename}`)
      // 直接跳转到分析页面
      uni.navigateTo({
        url: `/pages/analysis/analysis?filename=${encodeURIComponent(filename)}`
      })
    },
    
    // 渲染所有图表
    renderCharts() {
      try {
        if (!this.analysisResults || !this.analysisResults.chart_data) {
          console.log('没有图表数据可渲染')
          return
        }
        
        console.log('开始渲染图表，数据集数量:', this.analysisResults.chart_data.length)
        
        // 清空现有图表
        this.charts = []
        
        // 延迟执行，确保DOM元素已经渲染
        setTimeout(() => {
          // 逐个处理每个图表
          this.analysisResults.chart_data.forEach((chartData, index) => {
            const canvasId = `pcrChart_${index}`
            console.log(`准备渲染图表 ${index+1}:`, chartData.channel, chartData.type, canvasId)
            
            try {
              // 尝试直接获取Canvas上下文
              const ctx = uni.createCanvasContext(canvasId, this)
              
              if (!ctx) {
                console.error(`无法获取Canvas上下文: ${canvasId}`)
                return
              }
              
              // 简单测试Canvas是否正常工作
              ctx.setFillStyle('#FF0000')
              ctx.fillRect(0, 0, 300, 300)
              ctx.setFillStyle('#FFFFFF')
              ctx.setFontSize(20)
              ctx.setTextAlign('center')
              ctx.fillText(`通道${chartData.channel}-${chartData.type}`, 150, 150)
              ctx.draw(true, () => {
                console.log(`测试绘制图表 ${index} 完成`)
                
                // 在测试绘制成功后，再进行完整绘制
                setTimeout(() => {
                  this.drawChart(ctx, chartData, index)
                }, 100)
              })
            } catch (e) {
              console.error(`创建或测试图表 ${index} 失败:`, e)
            }
          })
        }, 500)
      } catch (e) {
        console.error('renderCharts方法出错:', e)
      }
    },
    
    // 绘制单个图表
    drawChart(ctx, chartData, index) {
      try {
        console.log(`绘制图表 ${index}`, chartData.type)
        
        // 设置固定大小，确保在不同设备上显示一致
        const canvasWidth = 300
        const canvasHeight = 300
        const padding = {
          left: 40,
          right: 20,
          top: 30,
          bottom: 40
        }
        
        // 检查数据
        if (!chartData.raw_data || chartData.raw_data.length === 0) {
          console.warn(`图表 ${index} 原始数据为空`)
          ctx.setFillStyle('#999')
          ctx.setTextAlign('center')
          ctx.setFontSize(14)
          ctx.fillText('无数据', canvasWidth / 2, canvasHeight / 2)
          ctx.draw(true)
          return
        }
        
        console.log(`数据点数量: raw=${chartData.raw_data.length}, trend=${chartData.trend_data ? chartData.trend_data.length : 0}`)
        
        // 计算绘图区域
        const chartWidth = canvasWidth - padding.left - padding.right
        const chartHeight = canvasHeight - padding.top - padding.bottom
        
        // 使用uni-app的clearRect方法清空画布
        ctx.clearRect(0, 0, canvasWidth, canvasHeight)
        
        // 设置背景色
        ctx.setFillStyle('#f8f9fa')
        ctx.fillRect(0, 0, canvasWidth, canvasHeight)
        
        // 先绘制一个简单的文本，验证Canvas绘图功能是否正常
        ctx.setFillStyle('#000000')
        ctx.setTextAlign('center')
        ctx.setTextBaseline('middle')
        ctx.setFontSize(16)
        ctx.fillText(`${chartData.type}-${chartData.channel} 数据图表`, canvasWidth / 2, 20)
        
        // 获取颜色
        const colorIndex = (chartData.channel - 1) % this.chartColors.length
        const color = this.chartColors[colorIndex]
        
        // 获取数据
        const rawData = chartData.raw_data || []
        const trendData = chartData.trend_data || []
        const cycles = chartData.cycles || Array.from({length: rawData.length}, (_, i) => i + 1)
        
        // 计算数据范围
        const maxValue = Math.max(...rawData, chartData.threshold || 800, 1000) // 确保至少有一个合理的上限值
        const maxCycle = cycles.length
        
        // 计算缩放比例
        const xScale = chartWidth / maxCycle
        const yScale = chartHeight / (maxValue * 1.2) // 留出一些顶部空间
        
        // 绘制网格线
        ctx.beginPath()
        ctx.setStrokeStyle('#dddddd')
        ctx.setLineWidth(0.5)
        
        // 水平网格线
        for (let i = 0; i <= 5; i++) {
          const y = padding.top + chartHeight - (i * chartHeight / 5)
          ctx.moveTo(padding.left, y)
          ctx.lineTo(padding.left + chartWidth, y)
        }
        
        // 垂直网格线
        for (let i = 0; i <= 5; i++) {
          const x = padding.left + (i * chartWidth / 5)
          ctx.moveTo(x, padding.top)
          ctx.lineTo(x, padding.top + chartHeight)
        }
        
        ctx.stroke()
        
        // 执行一次绘制，确保网格线显示
        ctx.draw(true)
        
        // 绘制阈值线
        ctx.beginPath()
        const threshold = chartData.threshold || 800
        const thresholdY = padding.top + chartHeight - (threshold * yScale)
        ctx.setStrokeStyle('#888888')
        ctx.setLineWidth(1)
        ctx.setLineDash([5, 5]) // 注意：某些平台可能不支持LineDash
        ctx.moveTo(padding.left, thresholdY)
        ctx.lineTo(padding.left + chartWidth, thresholdY)
        ctx.stroke()
        ctx.setLineDash([]) // 重置虚线样式
        
        // 绘制阈值标签
        ctx.setFillStyle('#666666')
        ctx.setTextAlign('right')
        ctx.setFontSize(12)
        ctx.fillText('阈值=800', padding.left + chartWidth - 5, thresholdY - 5)
        
        // 绘制原始数据曲线 (半透明)
        if (rawData.length > 0) {
          ctx.beginPath()
          ctx.setStrokeStyle(color)
          ctx.setLineWidth(1)
          ctx.setGlobalAlpha(0.2)
          
          for (let i = 0; i < rawData.length; i++) {
            const x = padding.left + i * xScale
            const y = padding.top + chartHeight - (rawData[i] * yScale)
            
            if (i === 0) {
              ctx.moveTo(x, y)
            } else {
              ctx.lineTo(x, y)
            }
          }
          
          ctx.stroke()
          ctx.setGlobalAlpha(1.0)
        }
        
        // 再次执行绘制，确保原始数据曲线显示
        ctx.draw(true)
        
        // 绘制趋势线
        if (trendData && trendData.length > 0) {
          ctx.beginPath()
          ctx.setStrokeStyle(color)
          ctx.setLineWidth(2)
          
          for (let i = 0; i < trendData.length; i++) {
            const x = padding.left + i * xScale
            const y = padding.top + chartHeight - (trendData[i] * yScale)
            
            if (i === 0) {
              ctx.moveTo(x, y)
            } else {
              ctx.lineTo(x, y)
            }
          }
          
          ctx.stroke()
        }
        
        // 再次执行绘制，确保趋势线显示
        ctx.draw(true)
        
        // 如果有CT值，绘制CT线和点
        if (chartData.ct_value) {
          const ctX = padding.left + chartData.ct_value * xScale
          
          // 绘制CT垂直线
          ctx.beginPath()
          ctx.setStrokeStyle('#33cc33')
          ctx.setLineWidth(1)
          ctx.setLineDash([5, 3])
          ctx.moveTo(ctX, padding.top)
          ctx.lineTo(ctX, padding.top + chartHeight)
          ctx.stroke()
          ctx.setLineDash([])
          
          // 绘制CT点
          const ctY = thresholdY
          ctx.beginPath()
          ctx.setFillStyle('#33cc33')
          ctx.arc(ctX, ctY, 5, 0, Math.PI * 2)
          ctx.fill()
          
          // 绘制CT文本
          ctx.setFillStyle('#009900')
          ctx.setTextAlign('center')
          ctx.setFontSize(12)
          ctx.fillText(`CT=${chartData.ct_value.toFixed(1)}`, ctX, ctY - 15)
        }
        
        // 再次执行绘制，确保CT线和点显示
        ctx.draw(true)
        
        // 绘制X轴和Y轴
        ctx.beginPath()
        ctx.setStrokeStyle('#aaaaaa')
        ctx.setLineWidth(1)
        
        // X轴
        ctx.moveTo(padding.left, padding.top + chartHeight)
        ctx.lineTo(padding.left + chartWidth, padding.top + chartHeight)
        
        // Y轴
        ctx.moveTo(padding.left, padding.top)
        ctx.lineTo(padding.left, padding.top + chartHeight)
        
        ctx.stroke()
        
        // 绘制X轴刻度
        ctx.setFillStyle('#666666')
        ctx.setTextAlign('center')
        ctx.setFontSize(10)
        
        const xStep = Math.max(1, Math.ceil(maxCycle / 5))
        for (let i = 0; i <= maxCycle; i += xStep) {
          const x = padding.left + i * xScale
          ctx.fillText(String(i), x, padding.top + chartHeight + 15)
        }
        
        // 绘制Y轴刻度
        ctx.setTextAlign('right')
        
        for (let i = 0; i <= 5; i++) {
          const y = padding.top + chartHeight - (i * chartHeight / 5)
          const value = Math.round(maxValue * i / 5)
          ctx.fillText(String(value), padding.left - 5, y + 3)
        }
        
        // 最终执行绘制
        ctx.draw(true, () => {
          console.log(`图表 ${index} 绘制完成`)
        })
      } catch (e) {
        console.error('绘制图表错误:', e)
        // 绘制错误提示
        ctx.setFillStyle('#f56c6c')
        ctx.setTextAlign('center')
        ctx.setFontSize(12)
        ctx.fillText('图表渲染错误', 150, 150)
        ctx.draw(true)
      }
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
}

.title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 30rpx;
}

.file-list {
  background-color: #fff;
  border-radius: 12rpx;
  padding: 20rpx;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.1);
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
}

.file-scroll {
  height: 300rpx;
}

.file-item {
  padding: 20rpx;
  border-bottom: 1rpx solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-name {
  font-size: 28rpx;
  color: #666;
}

.view-button {
  background-color: #2871FA;
  color: #fff;
  padding: 10rpx 20rpx;
  border-radius: 6rpx;
  font-size: 24rpx;
}

.view-button:active {
  background-color: #1a5fd9;
}

.results {
  background-color: #fff;
  border-radius: 12rpx;
  padding: 20rpx;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.1);
}

.plots-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
  margin-bottom: 30rpx;
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
}

.chart-title {
  font-size: 26rpx;
  font-weight: bold;
  color: #333;
  text-align: center;
  margin-bottom: 10rpx;
}

.chart-wrapper {
  width: 300px;
  height: 300px;
  margin: 0 auto;
  position: relative; /* 添加相对定位 */
  border: 1px solid #eee; /* 添加边框 */
}

.chart-canvas {
  width: 300px;
  height: 300px;
  position: absolute; /* 绝对定位 */
  left: 0;
  top: 0;
  z-index: 1; /* 确保画布在最上层 */
  /* 添加边框以便调试 */
  border: 1px dashed #ccc;
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
</style> 