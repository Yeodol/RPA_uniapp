from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
import mysql.connector
import os
import json
import traceback
from datetime import datetime
from dotenv import load_dotenv
import numpy as np
from scipy.signal import savgol_filter
from scipy.optimize import curve_fit
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import sqlite3
import scipy.signal as signal
import scipy.optimize as optimize
import re
from collections import defaultdict
from report_generator import PCRReportGenerator
import fitz  # PyMuPDF
import tempfile
from PIL import Image, ImageDraw, ImageFont
import requests

# 加载.env文件中的环境变量
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # 允许所有域的跨域请求

# 设置文件上传目录
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'RPA', 'data', 'txt')
print(f"文件上传目录: {app.config['UPLOAD_FOLDER']}")

# 确保目录存在
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
    print(f"创建目录: {app.config['UPLOAD_FOLDER']}")

# 加载配置文件
def load_config():
    config_path = os.environ.get('CONFIG_PATH', 'config.json')
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"加载配置文件错误: {e}")
        return {}

# 配置信息
server_config = load_config()

# 获取服务器配置
def get_server_config():
    return {
        'port': int(server_config.get('port', os.environ.get('PORT', 5032))),
        'host': server_config.get('host', os.environ.get('HOST', '0.0.0.0')),
        'debug': server_config.get('debug', os.environ.get('DEBUG', 'False').lower() == 'true')
    }

# 数据库连接函数
def get_db_connection(config):
    try:
        conn = mysql.connector.connect(
            host=server_config.get('db_host', os.environ.get('DB_HOST', 'localhost')),
            user=config.get('username'),
            password=config.get('password'),
            database=config.get('database')
        )
        return conn
    except mysql.connector.Error as err:
        print(f"数据库连接错误: {err}")
        return None

# PCR分析器类
class PCRAnalyzer:
    def __init__(self):
        self.base_point_count = 15
        self.threshold = 800.0
        self.channel_colors = ['#FF0000', '#00AA00', '#0000FF', '#FF00FF']

    def find_curve(self, data, size, start):
        if size - 4 < start:
            return False, 0

        diff = np.diff(data)
        
        for i in range(start, size - 4):
            if (diff[i] > 50.0 and diff[i + 3] > 50.0 and 
                50.0 < diff[i + 1] and diff[i + 1] < diff[i + 2] + 50.0):
                return True, i - i // 9
                
        return False, 0

    def median_filter(self, data, window_size):
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
        if alpha < 0.0 or alpha > 1.0:
            raise ValueError("Alpha must be between 0 and 1.")
            
        result = np.zeros_like(data)
        result[0] = data[0]
        
        for i in range(1, len(data)):
            result[i] = alpha * data[i] + (1.0 - alpha) * result[i - 1]
            
        return result

    def process_data(self, raw_data):
        try:
            data = np.array(raw_data, dtype=np.float64)
            size = len(data)
            
            result = {
                'raw': data.tolist(),
                'baseline': 0.0,
                'positive': False,
                'ct_value': 0.0,
                'ct_found': False,
                'data_size': size,
                'curve_start': 15,
                'smoothed': None,
                'trend': None
            }
            
            if size < 8:
                print(f"数据点太少({size}个)，无法进行有效处理")
                return result
                
            result['positive'], result['curve_start'] = self.find_curve(data, size, 3)
            
            # 计算基线（使用前1/3或固定点数）
            base_points = min(self.base_point_count, size // 3)
            baseline_data = data[:base_points]
            result['baseline'] = np.mean(baseline_data)
            
            # 扣除基线
            data = data - result['baseline']
            
            # 中值滤波
            window_size = min(5, size // 2 * 2 - 1)  # 确保窗口大小为奇数
            if window_size < 3:
                window_size = 3
            filtered = self.median_filter(data, window_size)
            
            # 指数平滑
            smoothed = self.exponential_smoothing(filtered, 0.6)
            
            # 使用Savitzky-Golay滤波进行进一步平滑
            window_length = min(11, size)
            if window_length % 2 == 0:
                window_length = max(3, window_length - 1)
            polyorder = min(2, window_length - 1)
            
            if size >= 3:
                trend = savgol_filter(smoothed, window_length=window_length, polyorder=polyorder)
            else:
                trend = smoothed.copy()
                
            result['trend'] = trend.tolist()
            result['smoothed'] = smoothed.tolist()
            
            # 计算CT值
            if result['positive']:
                scale_factor = 800.0 / self.threshold
                scaled_data = smoothed * scale_factor
                
                # 对前5个点进行特殊处理
                for i in range(min(5, size)):
                    scaled_data[i] *= 0.1 * i
                    
                # 寻找CT值 - 与pcr_analyzer.py保持一致
                for i in range(1, len(scaled_data)):
                    if not result['ct_found'] and scaled_data[i] >= 800.0:
                        # 线性插值计算CT值
                        ct = (i-1) + (800.0 - scaled_data[i-1]) / (scaled_data[i] - scaled_data[i-1])
                        result['ct_value'] = float(ct)
                        result['ct_found'] = True
                        break
                
                # 修改阳性判定条件：只有成功找到CT值的样本才判定为阳性
                result['positive'] = result['ct_found']
                        
            return result
            
        except Exception as e:
            print(f"PCR数据处理错误: {str(e)}")
            # 出错时返回初始结果
            return {
                'raw': [],
                'baseline': 0.0,
                'positive': False,
                'ct_value': 0.0,
                'ct_found': False,
                'data_size': 0,
                'curve_start': 15,
                'smoothed': None,
                'trend': None
            }

    def generate_plot(self, channel_data, channel_index, data_type):
        """生成图表"""
        try:
            # 创建高分辨率图表
            plt.figure(figsize=(10, 7), dpi=120)
            plt.clf()
            
            # 设置背景颜色和去除边框
            ax = plt.gca()
            ax.set_facecolor('#f8f9fa')
            
            # 删除所有边框
            for spine in ax.spines.values():
                spine.set_visible(False)
            
            # 绘制原始数据
            raw_data = channel_data[data_type]
            if not raw_data:
                plt.text(0.5, 0.5, '无数据', ha='center', va='center', fontsize=14)
                plt.title(f'通道{channel_index+1} - {data_type.upper()}', fontsize=14)
                
                # 保存为Base64
                buffer = BytesIO()
                plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight', pad_inches=0.1, transparent=True)
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                plt.close()
                return image_base64
            
            # 处理数据
            processed = self.process_data(raw_data)
            
            # 绘制网格线（在数据之前）
            plt.grid(True, linestyle='--', alpha=0.2, color='#cccccc')
            
            # 绘制原始数据
            x = range(1, len(raw_data) + 1)
            colors = ['#FF0000', '#00AA00', '#0000FF', '#FF00FF']
            color = colors[channel_index % len(colors)]
            
            # 绘制原始数据点（半透明）
            plt.plot(x, raw_data, 
                     color=color, 
                     alpha=0.2, 
                     linewidth=1, 
                     label='原始数据')
            
            # 绘制趋势线
            if processed['trend']:
                plt.plot(range(1, len(processed['trend']) + 1), 
                         processed['trend'], 
                         color=color, 
                         linewidth=2.5, 
                         label='趋势',
                         zorder=3)
                
                # 添加阈值线
                plt.axhline(y=800, color='#888888', linestyle='--', alpha=0.7, zorder=2)
                plt.text(len(processed['trend'])*0.95, 830, '阈值=800', 
                         ha='right', fontsize=10, color='#666666')
                
                # 如果找到CT值，显示标记
                if processed['ct_found']:
                    ct = processed['ct_value']
                    # 添加垂直CT线
                    plt.axvline(x=ct, color='#33cc33', linestyle='--', alpha=0.7, zorder=2)
                    # 添加CT点
                    plt.scatter([ct], [800], color='#33cc33', s=80, zorder=4, edgecolor='white')
                    # 添加CT值文本
                    plt.text(ct, 900, f'CT={ct:.1f}', 
                             ha='center', fontsize=12, color='#009900',
                             bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=3))
            
            # 设置标题和标签
            plt.title(f'通道{channel_index+1} - {data_type.upper()}', 
                      fontsize=16, 
                      color=color, 
                      pad=20,
                      fontweight='bold')
            
            plt.xlabel('循环次数', fontsize=12)
            plt.ylabel('荧光值', fontsize=12)
            
            # 设置刻度样式
            plt.tick_params(axis='both', which='both', length=0)
            
            # 设置图例
            plt.legend(loc='upper left', fontsize=10, frameon=False)
            
            # 确保Y轴从0开始
            bottom, top = plt.ylim()
            plt.ylim(0, max(top, 1000))
            
            # 保存为Base64，使用高DPI值
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight', pad_inches=0.1, transparent=True)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()
            
            return image_base64
        except Exception as e:
            print(f"生成图表错误: {str(e)}")
            # 创建错误图表
            plt.figure(figsize=(10, 7), dpi=120)
            plt.text(0.5, 0.5, f'图表生成错误:\n{str(e)}', ha='center', va='center', fontsize=12)
            
            # 去除边框
            for spine in plt.gca().spines.values():
                spine.set_visible(False)
                
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight', pad_inches=0.1)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()
            return image_base64

    def parse_pcr_data(self, file_content):
        """使用正则表达式解析PCR数据"""
        fam_data = defaultdict(list)
        vic_data = defaultdict(list)
        
        for line in file_content.splitlines():
            line = line.strip()
            if not line:
                continue
                
            # 使用正则表达式匹配数据
            try:
                cycle_match = re.search(r'cycle:(\d+)', line)
                channel_match = re.search(r'channel:(\d+)', line)
                fam_match = re.search(r'fam:(\d+)', line)
                vic_match = re.search(r'vic:(\d+)', line)
                
                if cycle_match and channel_match and fam_match and vic_match:
                    cycle = int(cycle_match.group(1))
                    channel = int(channel_match.group(1))
                    fam = int(fam_match.group(1))
                    vic = int(vic_match.group(1))
                    
                    fam_data[channel].append(fam)
                    vic_data[channel].append(vic)
                    print(f"已解析数据 - 循环:{cycle}, 通道:{channel}, FAM:{fam}, VIC:{vic}")
            except (AttributeError, ValueError) as e:
                print(f"数据解析错误: {line} - {str(e)}")
                continue
        
        # 转换为普通字典
        return {k: v for k, v in fam_data.items()}, {k: v for k, v in vic_data.items()}

def create_plot(data, title, color, ct_value=None):
    plt.figure(figsize=(8, 7), dpi=120)
    
    # 去除边框
    ax = plt.gca()
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # 设置背景颜色
    ax.set_facecolor('#f8f9fa')
    
    # 绘制网格线
    plt.grid(True, linestyle='--', alpha=0.2, color='#cccccc')
    
    # 绘制数据
    plt.plot(data, color=color, linewidth=2.5)
    
    # 添加阈值线
    plt.axhline(800.0, color='#888888', linestyle='--', alpha=0.7)
    plt.text(len(data)*0.95, 830, '阈值=800', ha='right', fontsize=10, color='#666666')
    
    if ct_value is not None:
        # 添加CT线
        plt.axvline(ct_value, color='#33cc33', linestyle='--', alpha=0.7)
        # 添加CT点
        plt.scatter([ct_value], [800], color='#33cc33', s=80, zorder=4, edgecolor='white')
        # 添加CT文本
        plt.text(ct_value, 900, f"CT={ct_value:.1f}", 
                 color='#009900', ha='center', fontsize=12,
                 bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=3))
    
    # 设置标题
    plt.title(title, fontsize=16, pad=20, fontweight='bold')
    
    # 设置刻度样式
    plt.tick_params(axis='both', which='both', length=0)
    
    plt.xlabel('循环数', fontsize=12)
    plt.ylabel('荧光值', fontsize=12)
    
    # 确保Y轴从0开始
    bottom, top = plt.ylim()
    plt.ylim(0, max(top, 1000))
    
    # 将图表转换为base64字符串
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=120, pad_inches=0.1, transparent=True)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(image_png).decode('utf-8')

@app.route('/api/data', methods=['POST'])
def get_data():
    """获取数据记录API"""
    try:
        # 获取请求中的数据库配置
        db_config = request.json
        print("接收到的数据库配置:", db_config)
        
        # 连接数据库
        conn = get_db_connection(db_config)
        if not conn:
            print("数据库连接失败")
            return jsonify({"error": "数据库连接失败"}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # 从配置中获取表名
        table = db_config.get('table', 'data')
        print("查询的表名:", table)
        
        # 查询数据
        query = f"SELECT * FROM {table} ORDER BY data_update DESC"
        print("执行的SQL查询:", query)
        cursor.execute(query)
        
        # 获取结果
        records = cursor.fetchall()
        print("查询到的记录数:", len(records))
        print("查询结果:", records)
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        return jsonify(records)
    
    except Exception as e:
        print(f"获取数据错误: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/delete', methods=['POST'])
def delete_data():
    """删除数据记录API"""
    try:
        # 获取请求中的数据库配置和记录ID
        data = request.json
        print(f"收到删除记录请求: {data}")
        
        db_config = {
            'username': data.get('username'),
            'password': data.get('password'),
            'database': data.get('database')
        }
        
        record_id = data.get('id')
        print(f"要删除的记录ID: {record_id}, 类型: {type(record_id)}")
        
        table = data.get('table', 'data')
        
        if not record_id:
            print(f"错误: 缺少记录ID, 请求数据: {data}")
            return jsonify({"error": "缺少记录ID"}), 400
        
        # 连接数据库
        conn = get_db_connection(db_config)
        if not conn:
            return jsonify({"error": "数据库连接失败"}), 500
        
        cursor = conn.cursor()
        
        # 删除记录 - 使用data_id字段，而不是id
        query = f"DELETE FROM {table} WHERE data_id = %s"
        print(f"执行SQL: {query}, 参数: {record_id}")
        cursor.execute(query, (record_id,))
        
        # 提交事务
        conn.commit()
        
        # 检查删除结果
        affected_rows = cursor.rowcount
        print(f"删除操作影响行数: {affected_rows}")
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        if affected_rows > 0:
            return jsonify({"success": True, "message": f"记录删除成功，影响行数: {affected_rows}"})
        else:
            return jsonify({"warning": True, "message": "记录可能不存在，未删除任何数据"}), 200
    
    except Exception as e:
        print(f"删除数据错误: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/data/txt/<filename>', methods=['GET'])
def get_txt_data(filename):
    """获取txt文件内容并处理数据API"""
    try:
        print(f"收到请求：获取文件 {filename}")
        
        # 允许预检请求
        if request.method == 'OPTIONS':
            response = Response()
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', '*')
            response.headers.add('Access-Control-Allow-Methods', '*')
            return response

        # 读取文件内容
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"尝试读取文件路径: {file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"错误：文件不存在 {file_path}")
            # 检查目录中的所有文件
            dir_path = app.config['UPLOAD_FOLDER']
            if os.path.exists(dir_path):
                files = os.listdir(dir_path)
                print(f"目录 {dir_path} 中的文件: {files}")
            return jsonify({'error': f'文件不存在: {filename}'}), 404
        
        print(f"文件存在，大小: {os.path.getsize(file_path)} 字节")
        
        # 检查文件编码
        encodings = ['utf-8', 'gbk', 'iso-8859-1']
        file_content = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    file_content = f.read()
                    print(f"成功使用 {encoding} 编码读取文件")
                    break
            except UnicodeDecodeError:
                print(f"使用 {encoding} 编码读取失败")
            except Exception as e:
                print(f"读取文件时出错 ({encoding}): {str(e)}")
        
        if file_content is None:
            return jsonify({'error': '无法读取文件内容，编码不支持'}), 500

        # 创建PCR分析器实例
        analyzer = PCRAnalyzer()
        
        # 使用改进的解析方法
        fam_data, vic_data = analyzer.parse_pcr_data(file_content)
        
        # 检查是否成功解析数据
        if not fam_data and not vic_data:
            print("错误：未能从文件中解析出任何数据")
            return jsonify({'error': '未能从文件中解析出任何数据'}), 400

        # 准备结果
        chart_data = []
        analysis_results = []

        # 处理每个通道的数据
        for channel in sorted(set(list(fam_data.keys()) + list(vic_data.keys()))):
            # 处理FAM数据
            if channel in fam_data and fam_data[channel]:
                print(f"处理通道 {channel+1} 的FAM数据 ({len(fam_data[channel])} 个点)")
                
                # 分析数据
                fam_processed = analyzer.process_data(fam_data[channel])
                
                # 准备前端图表数据
                fam_chart_data = {
                    'channel': channel + 1,
                    'type': 'FAM',
                    'raw_data': fam_processed['raw'],
                    'trend_data': fam_processed['trend'],
                    'smoothed_data': fam_processed['smoothed'],
                    'baseline': fam_processed['baseline'],
                    'ct_value': fam_processed['ct_value'] if fam_processed['ct_found'] else None,
                    'positive': fam_processed['positive'],
                    'threshold': 800.0,
                    'cycle_count': len(fam_processed['raw']),
                    'cycles': list(range(1, len(fam_processed['raw']) + 1))
                }
                chart_data.append(fam_chart_data)
                
                # 添加FAM结果
                analysis_results.append({
                    'channel': channel + 1,
                    'type': 'FAM',
                    'positive': fam_processed['positive'],
                    'ct_value': fam_processed['ct_value'] if fam_processed['ct_found'] else None
                })
                print(f"通道 {channel+1} FAM结果: {'阳性' if fam_processed['positive'] else '阴性'}, CT值: {fam_processed['ct_value'] if fam_processed['ct_found'] else '未检测到'}")
            
            # 处理VIC数据
            if channel in vic_data and vic_data[channel]:
                print(f"处理通道 {channel+1} 的VIC数据 ({len(vic_data[channel])} 个点)")
                
                # 分析数据
                vic_processed = analyzer.process_data(vic_data[channel])
                
                # 准备前端图表数据
                vic_chart_data = {
                    'channel': channel + 1,
                    'type': 'VIC',
                    'raw_data': vic_processed['raw'],
                    'trend_data': vic_processed['trend'],
                    'smoothed_data': vic_processed['smoothed'],
                    'baseline': vic_processed['baseline'],
                    'ct_value': vic_processed['ct_value'] if vic_processed['ct_found'] else None,
                    'positive': vic_processed['positive'],
                    'threshold': 800.0,
                    'cycle_count': len(vic_processed['raw']),
                    'cycles': list(range(1, len(vic_processed['raw']) + 1))
                }
                chart_data.append(vic_chart_data)
                
                # 添加VIC结果
                analysis_results.append({
                    'channel': channel + 1,
                    'type': 'VIC',
                    'positive': vic_processed['positive'],
                    'ct_value': vic_processed['ct_value'] if vic_processed['ct_found'] else None
                })
                print(f"通道 {channel+1} VIC结果: {'阳性' if vic_processed['positive'] else '阴性'}, CT值: {vic_processed['ct_value'] if vic_processed['ct_found'] else '未检测到'}")
        
        print(f"结果统计: {len(chart_data)} 个数据集, {len(analysis_results)} 个分析结果")
        return jsonify({
            'filename': filename,
            'chart_data': chart_data,  # 前端绘图数据
            'results': analysis_results,  # 分析结果
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    except Exception as e:
        print(f"处理文件 {filename} 时发生严重错误:")
        print(traceback.format_exc())
        app.logger.error(f'Error processing file {filename}: {str(e)}')
        app.logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# 用于检查API状态的端点
@app.route('/api/status', methods=['GET'])
def status():
    # 获取运行环境信息
    upload_folder = app.config['UPLOAD_FOLDER'] 
    
    # 检查文件目录
    files = []
    file_count = 0
    try:
        if os.path.exists(upload_folder):
            files = [f for f in os.listdir(upload_folder) if f.lower().endswith('.txt')]
            file_count = len(files)
    except Exception as e:
        print(f"获取文件列表错误: {str(e)}")
    
    return jsonify({
        "status": "running",
        "version": os.environ.get('API_VERSION', '1.0.0'),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "upload_folder": upload_folder,
        "upload_folder_exists": os.path.exists(upload_folder),
        "file_count": file_count,
        "files": files[:10] if files else []  # 只返回前10个文件
    })

@app.route('/api/files', methods=['GET'])
def get_files():
    """获取txt文件列表API"""
    try:
        # 构建文件路径
        txt_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'txt')
        
        # 确保目录存在
        if not os.path.exists(txt_dir):
            os.makedirs(txt_dir)
        
        # 获取所有txt文件
        files = [f for f in os.listdir(txt_dir) if f.lower().endswith('.txt')]
        
        return jsonify({"files": files})
            
    except Exception as e:
        print(f"获取文件列表错误: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/files/delete', methods=['POST'])
def delete_file():
    """删除txt文件API"""
    try:
        # 获取要删除的文件名
        data = request.json
        filename = data.get('filename')
        
        if not filename:
            return jsonify({"error": "缺少文件名参数"}), 400
        
        # 构建文件路径
        txt_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'txt')
        file_path = os.path.join(txt_dir, filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({"error": f"文件不存在: {filename}"}), 404
        
        # 删除文件
        os.remove(file_path)
        print(f"成功删除文件: {file_path}")
        
        # 返回成功信息
        return jsonify({"success": True, "message": f"文件 {filename} 已成功删除"})
            
    except Exception as e:
        print(f"删除文件错误: {e}")
        return jsonify({"error": str(e)}), 500

# 初始化报告生成器
report_generator = PCRReportGenerator()

@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    """生成PDF报告API"""
    try:
        # 获取请求数据
        data = request.json
        
        if not data:
            return jsonify({"success": False, "error": "缺少数据"}), 400
        
        # 检查必要字段
        if 'filename' not in data:
            return jsonify({"success": False, "error": "缺少filename字段"}), 400
        
        # 确保chart_data中包含了smoothed_data
        if 'chart_data' in data:
            print(f"处理{len(data['chart_data'])}个图表数据，准备生成PDF报告")
            # 迭代每个通道的数据
            for chart in data['chart_data']:
                # 如果存在smoothed_data
                if 'smoothed_data' in chart and chart['smoothed_data']:
                    # 保存原始trend_data作为备份
                    if 'original_trend_data' not in chart:
                        chart['original_trend_data'] = chart.get('trend_data', [])
                    
                    # 直接使用smoothed_data
                    chart['trend_data'] = chart['smoothed_data']
                    print(f"使用smoothed_data替换trend_data，通道:{chart.get('channel')}, 类型:{chart.get('type')}")
        
        # 生成报告
        result = report_generator.create_report(data)
        
        if result.get('success'):
            print(f"报告生成成功: {result.get('path')}")
        else:
            print(f"报告生成失败: {result.get('error')}")
            
        return jsonify(result)
        
    except Exception as e:
        print(f"生成报告错误: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/reports/check', methods=['POST'])
def check_report_exists():
    """检查报告是否存在API"""
    try:
        # 获取请求数据
        data = request.json
        
        if not data or 'filename' not in data:
            return jsonify({"success": False, "error": "缺少filename字段"}), 400
        
        # 检查报告是否存在
        filename = data['filename']
        exists = report_generator.check_report_exists(filename)
        
        return jsonify({
            "success": True,
            "exists": exists,
            "filename": filename
        })
        
    except Exception as e:
        print(f"检查报告存在错误: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/reports/list', methods=['GET'])
def list_reports():
    """获取报告列表API"""
    try:
        # 获取所有报告
        reports = report_generator.get_report_list()
        return jsonify(reports)
        
    except Exception as e:
        print(f"获取报告列表错误: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/reports/delete', methods=['POST'])
def delete_report():
    """删除报告API"""
    try:
        # 获取请求数据
        data = request.json
        
        if not data or 'filename' not in data:
            return jsonify({"success": False, "error": "缺少filename字段"}), 400
        
        # 删除报告
        filename = data['filename']
        result = report_generator.delete_report(filename)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"删除报告错误: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# PDF渲染功能 - 开始
def render_pdf_to_image(pdf_data, page_num=1, scale=2.0):
    """
    将PDF数据渲染为图片
    
    参数:
    - pdf_data: PDF文件的二进制数据
    - page_num: 要渲染的页码 (从1开始)
    - scale: 缩放因子
    
    返回:
    - 图片的二进制数据 (PNG格式)
    """
    try:
        # 使用BytesIO创建内存文件对象
        pdf_stream = BytesIO(pdf_data)
        
        # 打开PDF文档
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        
        # 检查页码是否有效
        if page_num < 1 or page_num > len(doc):
            print(f"无效的页码: {page_num}, PDF共有 {len(doc)} 页")
            return None
        
        # 获取指定页面
        page = doc.load_page(page_num - 1)  # 页码从0开始
        
        # 设置渲染参数
        zoom_matrix = fitz.Matrix(scale, scale)
        
        # 渲染为像素图
        pix = page.get_pixmap(matrix=zoom_matrix, alpha=False)
        
        # 将像素图转换为PIL Image对象
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # 保存为PNG格式
        img_stream = BytesIO()
        img.save(img_stream, format="PNG")
        img_data = img_stream.getvalue()
        
        # 关闭文档
        doc.close()
        
        return img_data
    except Exception as e:
        print(f"渲染PDF时出错: {str(e)}")
        return None

def get_pdf_metadata(pdf_data):
    """
    获取PDF的元数据
    
    参数:
    - pdf_data: PDF文件的二进制数据
    
    返回:
    - 包含元数据的字典
    """
    try:
        # 使用BytesIO创建内存文件对象
        pdf_stream = BytesIO(pdf_data)
        
        # 打开PDF文档
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        
        # 获取元数据
        metadata = {
            "pageCount": len(doc),
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "creator": doc.metadata.get("creator", ""),
            "producer": doc.metadata.get("producer", ""),
            "creationDate": doc.metadata.get("creationDate", ""),
            "modificationDate": doc.metadata.get("modificationDate", "")
        }
        
        # 关闭文档
        doc.close()
        
        return metadata
    except Exception as e:
        print(f"获取PDF元数据时出错: {str(e)}")
        return {"error": str(e)}

def pdf_to_base64_image(pdf_data, page_num=1, scale=2.0):
    """
    将PDF转换为Base64编码的图片
    
    参数:
    - pdf_data: PDF文件的二进制数据
    - page_num: 要渲染的页码 (从1开始)
    - scale: 缩放因子
    
    返回:
    - Base64编码的图片字符串 (带有data:image/png;base64,前缀)
    """
    try:
        img_data = render_pdf_to_image(pdf_data, page_num, scale)
        if img_data:
            base64_data = base64.b64encode(img_data).decode('utf-8')
            return f"data:image/png;base64,{base64_data}"
        return None
    except Exception as e:
        print(f"转换PDF为Base64图片时出错: {str(e)}")
        return None
# PDF渲染功能 - 结束

# 在app.py文件中添加PDF渲染相关的路由
@app.route('/api/reports/check-rendering', methods=['GET'])
def check_rendering():
    """检查是否支持PDF渲染"""
    try:
        # 检查是否安装了PyMuPDF
        import fitz
        return jsonify({"supported": True, "version": fitz.version[0]})
    except ImportError:
        return jsonify({"supported": False, "reason": "PyMuPDF未安装"})

@app.route('/api/reports/pdf-metadata', methods=['GET'])
def pdf_metadata():
    """获取PDF元数据"""
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "未提供PDF URL"}), 400
    
    try:
        # 如果URL不是以http开头，假设它是相对路径
        if not url.startswith('http'):
            # 获取当前服务器的基础URL
            base_url = request.host_url.rstrip('/')
            url = f"{base_url}{url}"
        
        # 下载PDF
        print(f"下载PDF: {url}")
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            return jsonify({"error": f"无法下载PDF，状态码: {response.status_code}"}), 400
        
        # 读取PDF内容
        pdf_data = response.content
        
        # 获取元数据
        metadata = get_pdf_metadata(pdf_data)
        return jsonify(metadata)
    except Exception as e:
        print(f"获取PDF元数据时出错: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/reports/render-page', methods=['GET'])
def render_page():
    """将PDF页面渲染为图片"""
    url = request.args.get('url')
    page_num = int(request.args.get('page', 1))
    scale = float(request.args.get('scale', 2.0))
    
    if not url:
        return jsonify({"error": "未提供PDF URL"}), 400
    
    try:
        # 如果URL不是以http开头，假设它是相对路径
        if not url.startswith('http'):
            # 获取当前服务器的基础URL
            base_url = request.host_url.rstrip('/')
            url = f"{base_url}{url}"
        
        # 下载PDF
        print(f"下载PDF以渲染: {url}")
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            return jsonify({"error": f"无法下载PDF，状态码: {response.status_code}"}), 400
        
        # 读取PDF内容
        pdf_data = response.content
        
        # 渲染PDF页面为图片
        img_data = render_pdf_to_image(pdf_data, page_num, scale)
        
        if not img_data:
            return jsonify({"error": "渲染PDF页面失败"}), 500
        
        # 创建临时文件保存图像
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_filename = tmp.name
            tmp.write(img_data)
        
        # 返回图像文件
        return send_file(tmp_filename, mimetype='image/png')
    except Exception as e:
        print(f"渲染PDF页面时出错: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/reports/render-page-base64', methods=['GET'])
def render_page_base64():
    """将PDF页面渲染为Base64编码的图片"""
    url = request.args.get('url')
    page_num = int(request.args.get('page', 1))
    scale = float(request.args.get('scale', 2.0))
    
    if not url:
        return jsonify({"error": "未提供PDF URL"}), 400
    
    try:
        # 如果URL不是以http开头，假设它是相对路径
        if not url.startswith('http'):
            # 获取当前服务器的基础URL
            base_url = request.host_url.rstrip('/')
            url = f"{base_url}{url}"
        
        # 下载PDF
        print(f"下载PDF以渲染为Base64: {url}")
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            return jsonify({"error": f"无法下载PDF，状态码: {response.status_code}"}), 400
        
        # 读取PDF内容
        pdf_data = response.content
        
        # 将PDF转换为Base64编码的图片
        base64_image = pdf_to_base64_image(pdf_data, page_num, scale)
        
        if not base64_image:
            return jsonify({"error": "渲染PDF页面为Base64失败"}), 500
        
        return jsonify({"image": base64_image})
    except Exception as e:
        print(f"渲染PDF页面为Base64时出错: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/common/sample-pdf-image', methods=['GET'])
def sample_pdf_image():
    """提供一个示例PDF图片"""
    try:
        # 创建一个简单的图片
        from PIL import ImageDraw, ImageFont
        
        width, height = 800, 1000
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # 绘制边框
        draw.rectangle([10, 10, width-10, height-10], outline='#CCCCCC', width=2)
        
        # 绘制文本
        try:
            # 尝试使用系统字体
            font_path = None
            if os.name == 'nt':  # Windows
                font_path = "C:\\Windows\\Fonts\\Arial.ttf"
            elif os.name == 'posix':  # Linux/Mac
                font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/System/Library/Fonts/Helvetica.ttc",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
                ]
                for path in font_paths:
                    if os.path.exists(path):
                        font_path = path
                        break
            
            if font_path and os.path.exists(font_path):
                font_title = ImageFont.truetype(font_path, 30)
                font_normal = ImageFont.truetype(font_path, 20)
                font_small = ImageFont.truetype(font_path, 16)
            else:
                # 如果找不到字体，使用默认
                font_title = ImageFont.load_default()
                font_normal = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
        except Exception as e:
            print(f"加载字体失败: {str(e)}")
            # 如果加载字体失败，使用默认
            font_title = ImageFont.load_default()
            font_normal = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # 绘制标题和文本
        try:
            draw.text((width//2, 100), "PDF预览示例", fill='#333333', font=font_title, anchor='mm')
            draw.text((width//2, 150), "PDF渲染功能正常工作", fill='#333333', font=font_normal, anchor='mm')
            draw.text((width//2, 200), "这是一个测试图片", fill='#666666', font=font_small, anchor='mm')
        except Exception as e:
            print(f"绘制文本失败: {str(e)}")
            # 使用更简单的绘制方式
            draw.text((width//2, 100), "PDF预览示例", fill='#333333')
            draw.text((width//2, 150), "PDF渲染功能正常工作", fill='#333333')
            draw.text((width//2, 200), "这是一个测试图片", fill='#666666')
        
        # 创建临时文件保存图像
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_filename = tmp.name
            img.save(tmp_filename, format="PNG")
        
        # 返回图像文件
        return send_file(tmp_filename, mimetype='image/png')
    except Exception as e:
        print(f"生成示例图片时出错: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 修改现有的view_report方法，增加渲染为图片的功能
@app.route('/api/reports/view/<filename>', methods=['GET'])
def view_report(filename):
    """查看报告API"""
    try:
        # 检查是否请求直接下载文件
        download_mode = request.args.get('download', 'false').lower() == 'true'
        # 检查是否请求渲染为图片
        render_image = request.args.get('render', 'false').lower() == 'true'
        page_num = int(request.args.get('page', 1))
        scale = float(request.args.get('scale', 2.0))
        
        # 获取报告文件路径
        report_path = report_generator.get_report_file(filename)
        
        if not report_path:
            return jsonify({"success": False, "error": "报告不存在"}), 404
        
        # 如果请求渲染为图片
        if render_image:
            print(f"渲染报告为图片: {filename}, 页码: {page_num}, 缩放: {scale}")
            try:
                # 读取PDF文件
                with open(report_path, 'rb') as file:
                    pdf_data = file.read()
                
                # 渲染PDF页面为图片
                img_data = render_pdf_to_image(pdf_data, page_num, scale)
                
                if not img_data:
                    return jsonify({"error": "渲染PDF页面失败"}), 500
                
                # 创建临时文件保存图像
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    tmp_filename = tmp.name
                    tmp.write(img_data)
                
                # 返回图像文件
                return send_file(tmp_filename, mimetype='image/png')
            except Exception as e:
                print(f"渲染报告为图片时出错: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500
        
        # 直接提供文件下载
        if download_mode:
            print(f"提供直接下载: {filename}")
            return send_file(
                report_path,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
        
        # 读取PDF文件并转换为base64编码（保持原有行为）
        with open(report_path, 'rb') as file:
            pdf_base64 = base64.b64encode(file.read()).decode('utf-8')
        
        # 返回base64编码的PDF内容
        return jsonify({
            "success": True, 
            "content": pdf_base64,
            "filename": filename,
            "download_url": f"/api/reports/view/{filename}?download=true",
            "render_url": f"/api/reports/view/{filename}?render=true&page=1"
        })
        
    except Exception as e:
        print(f"查看报告错误: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/reports/render-page-lite', methods=['GET'])
def render_page_lite():
    """轻量级API：将PDF页面渲染为图片，使用简化的请求处理减少头部大小问题"""
    url = request.args.get('url')
    page_num = int(request.args.get('page', 1))
    scale = float(request.args.get('scale', 2.0))
    
    if not url:
        return jsonify({"error": "未提供PDF URL"}), 400
    
    try:
        # 处理URL - 从URL中提取PDF文件名
        pdf_filename = None
        if '/view/' in url:
            # 如果是通过view接口获取的PDF
            parts = url.split('/view/')
            if len(parts) > 1:
                pdf_filename = parts[1].split('?')[0]
        
        # 如果无法从URL解析出文件名，则使用常规下载方式
        if not pdf_filename:
            # 如果URL不是以http开头，假设它是相对路径
            if not url.startswith('http'):
                # 获取当前服务器的基础URL
                base_url = request.host_url.rstrip('/')
                url = f"{base_url}{url}"
            
            # 下载PDF
            print(f"下载PDF以渲染(轻量模式): {url}")
            response = requests.get(url, stream=True)
            if response.status_code != 200:
                return jsonify({"error": f"无法下载PDF，状态码: {response.status_code}"}), 400
            
            # 读取PDF内容
            pdf_data = response.content
        else:
            # 直接从文件系统读取PDF
            reports_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'RPA', 'data', 'reports')
            pdf_path = os.path.join(reports_folder, pdf_filename)
            
            if not os.path.exists(pdf_path):
                return jsonify({"error": "找不到PDF文件"}), 404
                
            # 读取PDF内容
            with open(pdf_path, 'rb') as f:
                pdf_data = f.read()
        
        # 渲染PDF页面为图片
        img_data = render_pdf_to_image(pdf_data, page_num, scale)
        
        if not img_data:
            return jsonify({"error": "渲染PDF页面失败"}), 500
        
        # 创建临时文件保存图像
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_filename = tmp.name
            tmp.write(img_data)
        
        # 设置头部缓存控制以减少后续请求的头部大小
        response = send_file(tmp_filename, mimetype='image/png')
        response.headers['Cache-Control'] = 'public, max-age=86400'  # 缓存1天
        response.headers['X-Accel-Buffering'] = 'no'  # 关闭Nginx缓冲，减少头部
        return response
    except Exception as e:
        print(f"轻量渲染PDF页面时出错: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # 获取服务器配置
    server_config = get_server_config()
    print(f"服务器配置: 端口={server_config['port']}, 主机={server_config['host']}, 调试模式={server_config['debug']}")
    
    # 设置Werkzeug服务器选项，增加请求头限制
    from werkzeug.serving import WSGIRequestHandler
    WSGIRequestHandler.protocol_version = "HTTP/1.1"  # 使用HTTP/1.1
    
    # 启动Flask应用
    print(f"服务器运行在 http://{server_config['host']}:{server_config['port']}")
    
    # 设置最大请求头大小，默认值太小可能导致431错误
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 设置为16MB
    
    # 在生产环境中，应该使用正确的WSGI服务器
    app.run(
        host=server_config['host'],
        port=server_config['port'],
        debug=server_config['debug'],
        threaded=True
    ) 