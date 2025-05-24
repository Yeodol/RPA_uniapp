import numpy as np
from scipy.signal import medfilt, savgol_filter
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import re
from collections import defaultdict
from scipy.optimize import curve_fit

class PCRAnalyzer:
    def __init__(self):
        self.base_point_count = 15  # 与C#版本保持一致
        self.threshold = 800.0  # 与C#版本保持一致
        self.channel_colors = ['#FF0000', '#00AA00', '#0000FF', '#FF00FF']
        self.marker_styles = ['o', 's', '^', 'v']

    def parse_data(self, file_path):
        """解析数据文件"""
        fam_data = defaultdict(list)
        vic_data = defaultdict(list)

        with open(file_path) as f:
            for line in f:
                try:
                    cycle = int(re.search(r'cycle:(\d+)', line).group(1))
                    channel = int(re.search(r'channel:(\d+)', line).group(1))
                    fam = float(re.search(r'fam:(\d+)', line).group(1))
                    vic = float(re.search(r'vic:(\d+)', line).group(1))

                    fam_data[channel].append(fam)
                    vic_data[channel].append(vic)
                except (AttributeError, ValueError) as e:
                    print(f"数据解析错误: {line.strip()} - {str(e)}")
                    continue

        return dict(fam_data), dict(vic_data)

    def find_curve(self, data, size, start):
        """寻找曲线起始点，与C#版本保持一致"""
        if size - 4 < start:
            return False, 0

        # 计算差值
        diff = np.diff(data)
        
        for i in range(start, size - 4):
            if (diff[i] > 50.0 and diff[i + 3] > 50.0 and 
                50.0 < diff[i + 1] and diff[i + 1] < diff[i + 2] + 50.0):
                return True, i - i // 9
                
        return False, 0

    def median_filter(self, data, window_size):
        """中值滤波，与C#版本保持一致"""
        if window_size % 2 == 0:
            raise ValueError("Window size must be odd.")
            
        result = np.zeros_like(data)
        half = window_size // 2
        
        for i in range(len(data)):
            start = max(0, i - half)
            end = min(len(data), i + half + 1)
            window = data[start:end]
            result[i] = np.median(window)
            
        return result

    def exponential_smoothing(self, data, alpha):
        """指数平滑，与C#版本保持一致"""
        if alpha < 0.0 or alpha > 1.0:
            raise ValueError("Alpha must be between 0 and 1.")
            
        result = np.zeros_like(data)
        result[0] = data[0]
        
        for i in range(1, len(data)):
            result[i] = alpha * data[i] + (1.0 - alpha) * result[i - 1]
            
        return result

    def logistic_function(self, x, L, k, x0):
        """Logistic 函数用于拟合 PCR 扩增曲线"""
        return L / (1 + np.exp(-k * (x - x0)))

    def fit_logistic_curve(self, x, y):
        """使用 logistic 函数拟合数据"""
        try:
            # 初始参数估计
            L = np.max(y)  # 最大荧光值
            k = 0.5  # 增长率
            x0 = np.mean(x)  # 中点位置
            
            # 使用 curve_fit 进行拟合
            popt, _ = curve_fit(self.logistic_function, x, y, p0=[L, k, x0], maxfev=10000)
            
            # 生成拟合曲线
            x_fit = np.linspace(min(x), max(x), 100)
            y_fit = self.logistic_function(x_fit, *popt)
            
            return x_fit, y_fit, popt
        except Exception as e:
            print(f"曲线拟合失败: {str(e)}")
            return None, None, None

    def process_data(self, raw_data):
        """处理单个通道数据，与C#版本保持一致"""
        data = np.array(raw_data, dtype=np.float64)
        size = len(data)
        
        # 初始化结果
        result = {
            'raw': data,
            'baseline': 0.0,
            'positive': False,
            'ct_value': 0.0,
            'ct_found': False,
            'data_size': size,
            'curve_start': 15,
            'smoothed': None,  # 保存平滑后的数据
            'trend': None      # 保存趋势线数据
        }
        
        # 如果数据量小于8，直接返回阴性
        if size < 8:
            return result
            
        # 寻找曲线起始点
        result['positive'], result['curve_start'] = self.find_curve(data, size, 3)
        
        # 计算基线
        baseline_data = data[:self.base_point_count]
        result['baseline'] = np.mean(baseline_data)
        
        # 扣除基线
        data = data - result['baseline']
        
        # 中值滤波
        filtered = self.median_filter(data, 5)
        
        # 指数平滑
        smoothed = self.exponential_smoothing(filtered, 0.6)
        result['smoothed'] = smoothed
        
        # 使用Savitzky-Golay滤波进行进一步平滑
        window_length = min(11, size)
        if window_length % 2 == 0:
            window_length = max(3, window_length - 1)
        polyorder = min(2, window_length - 1)
        
        if size >= 3:
            trend = savgol_filter(smoothed, window_length=window_length, polyorder=polyorder)
        else:
            trend = smoothed.copy()
            
        result['trend'] = trend
        
        # 计算CT值
        if result['positive']:
            scale_factor = 800.0 / self.threshold
            scaled_data = smoothed * scale_factor
            
            # 对前5个点进行特殊处理
            for i in range(5):
                scaled_data[i] *= 0.1 * i
                
            # 寻找CT值
            for i in range(len(scaled_data)):
                if not result['ct_found'] and scaled_data[i] >= 800.0:
                    # 线性插值计算CT值
                    ct = i - 1 + (800.0 - scaled_data[i - 1]) / (scaled_data[i] - scaled_data[i - 1])
                    result['ct_value'] = ct
                    result['ct_found'] = True
                    break
                    
        return result

    def plot_results(self, raw_data, processed_data, title_prefix):
        """绘制结果图表"""
        fig, axes = plt.subplots(4, 4, figsize=(24, 16))  # 修改为4列
        fig.suptitle(f'{title_prefix} Analysis', y=1.02, fontsize=16)

        for ch in sorted(raw_data.keys()):
            row = ch
            cycles = np.arange(len(raw_data[ch]))
            
            # 原始数据
            ax = axes[row, 0]
            ax.plot(cycles, raw_data[ch],
                   color=self.channel_colors[ch],
                   marker=self.marker_styles[ch],
                   markersize=4,
                   linestyle='-',
                   alpha=0.7)
            ax.axhline(processed_data[ch]['baseline'],
                      color='gray',
                      linestyle=':',
                      alpha=0.5)
            ax.set_title(f'Ch{ch} - Raw Data')
            ax.set_ylabel('Fluorescence')
            ax.grid(True, alpha=0.3)
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            
            # 处理后的数据（扣除基线）
            ax = axes[row, 1]
            processed = processed_data[ch]
            ax.plot(cycles, processed['raw'] - processed['baseline'],
                   color=self.channel_colors[ch],
                   linewidth=2)
            
            if processed['positive'] and processed['ct_found']:
                ax.axvline(processed['ct_value'],
                          color='red',
                          linestyle='--',
                          alpha=0.7)
                ax.text(processed['ct_value'],
                       0,
                       f"CT={processed['ct_value']:.1f}",
                       color='red',
                       ha='center')
            
            ax.axhline(800.0, color='gray', linestyle=':', alpha=0.5)
            ax.text(cycles[-1], 800.0, 'threshold', ha='right', va='bottom', color='gray')
            
            ax.set_title(f'Ch{ch} - Processed Data')
            ax.set_ylabel('ΔRn')
            ax.grid(True, alpha=0.3)
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            
            # 平滑后的数据
            ax = axes[row, 2]
            if processed['trend'] is not None:
                ax.plot(cycles, processed['trend'],
                       color=self.channel_colors[ch],
                       linewidth=2)
                
                ax.axhline(800.0, color='gray', linestyle=':', alpha=0.5)
                ax.text(cycles[-1], 800.0, 'threshold', ha='right', va='bottom', color='gray')
                
                if processed['positive'] and processed['ct_found']:
                    ax.axvline(processed['ct_value'],
                             color='red',
                             linestyle='--',
                             alpha=0.7)
                    ax.text(processed['ct_value'],
                           800.0,
                           f"CT={processed['ct_value']:.1f}",
                           color='red',
                           ha='center')
            
            ax.set_title(f'Ch{ch} - Smoothed Trend')
            ax.set_ylabel('ΔRn')
            ax.grid(True, alpha=0.3)
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))

            # S型拟合曲线
            ax = axes[row, 3]
            if processed['trend'] is not None and processed['positive']:
                # 使用处理后的数据进行拟合
                x_fit, y_fit, popt = self.fit_logistic_curve(cycles, processed['trend'])
                
                if x_fit is not None:
                    # 绘制原始数据点
                    ax.scatter(cycles, processed['trend'],
                             color=self.channel_colors[ch],
                             alpha=0.5,
                             label='Data Points')
                    
                    # 绘制拟合曲线
                    ax.plot(x_fit, y_fit,
                           color=self.channel_colors[ch],
                           linewidth=2,
                           label='Fitted Curve')
                    
                    # 添加阈值线
                    ax.axhline(800.0, color='gray', linestyle=':', alpha=0.5)
                    ax.text(cycles[-1], 800.0, 'threshold', ha='right', va='bottom', color='gray')
                    
                    # 计算并显示CT值
                    if processed['ct_found']:
                        ax.axvline(processed['ct_value'],
                                 color='red',
                                 linestyle='--',
                                 alpha=0.7)
                        ax.text(processed['ct_value'],
                               800.0,
                               f"CT={processed['ct_value']:.1f}",
                               color='red',
                               ha='center')
                    
                    # 添加图例
                    ax.legend()
                    
                    ax.set_title(f'Ch{ch} - S-Curve Fit')
                    ax.set_ylabel('ΔRn')
                    ax.grid(True, alpha=0.3)
                    ax.xaxis.set_major_locator(MaxNLocator(integer=True))

        plt.tight_layout()
        plt.show()

    def analyze(self, file_path):
        """主分析流程"""
        # 1. 解析数据
        fam_raw, vic_raw = self.parse_data(file_path)

        # 2. 处理数据
        fam_processed = {ch: self.process_data(fam_raw[ch]) for ch in fam_raw}
        vic_processed = {ch: self.process_data(vic_raw[ch]) for ch in vic_raw}

        # 3. 输出结果
        print("\n检测结果:")
        for ch in sorted(fam_raw.keys()):
            fam = fam_processed[ch]
            vic = vic_processed[ch]

            print(f"\n通道 {ch}:")
            print(f"  FAM: {'阳性' if fam['positive'] else '阴性'}",
                 f"CT={fam['ct_value']:.1f}" if fam['ct_found'] else "")
            print(f"  VIC: {'阳性' if vic['positive'] else '阴性'}",
                 f"CT={vic['ct_value']:.1f}" if vic['ct_found'] else "")

        # 4. 绘制曲线
        self.plot_results(fam_raw, fam_processed, "FAM")
        self.plot_results(vic_raw, vic_processed, "VIC")


if __name__ == "__main__":
    analyzer = PCRAnalyzer()
    analyzer.analyze(r"D:\eichi\RPA_uniapp\RPA\backend/2025-02-10_09-46-30.txt") 