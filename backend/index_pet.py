# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, \
    QLabel, QLineEdit, QPushButton,  QGridLayout, QDesktopWidget, QProgressBar, \
    QSizePolicy, QDialog, QHBoxLayout, QSpinBox, QMessageBox, QMenu, QListWidget,\
    QStyle, QSpacerItem
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, pyqtSignal, \
    QPropertyAnimation, QEasingCurve, QSettings, QThread, QObject
import os
import sys
import serial
import serial.tools.list_ports
from datetime import datetime
from qt_material import apply_stylesheet
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from scipy.signal import medfilt, savgol_filter
import matplotlib.pyplot as plt
import subprocess
import platform
import pymysql
import tempfile
import ctypes
from index_ui import Ui_MainWindow
from login_ui import Ui_Form
from setting_ui import Ui_Form as Setting_Ui_Form
from scipy.optimize import curve_fit

resize_data = [1920, 1080]

# 添加全局触摸屏优化参数
TOUCH_OPTIMIZED = True  # 触摸屏优化开关
TOUCH_BUTTON_HEIGHT = 60  # 按钮高度
TOUCH_BUTTON_MIN_WIDTH = 120  # 按钮最小宽度
TOUCH_FONT_SIZE = 25  # 字体大小
TOUCH_INPUT_HEIGHT = 60  # 输入框高度
TOUCH_SPACING = 15  # 元素间距


class BaseWindow:
    def _show_custom_message(self, title, text, icon_type, parent=None):
        """通用自定义消息框"""
        msg = QMessageBox(parent or self)
        msg.setObjectName("msg")
        msg.setWindowIcon(QIcon("img/logo.ico"))
        msg.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        msg.setIcon(icon_type)


        msg.setStyleSheet("""
            QMessageBox#msg {
                background-color: #f0f7fd;
                min-width: 600px;
                min-height: 600px;
                padding: 100px;
                border:2px #cfcfcf;
            }
            QMessageBox#msg QLabel {
                font-size: 28px;
                min-height: 150px;
                padding: 20px;
                qproperty-alignment: AlignCenter;
                background-color: #f0f7fd;
            }
            QMessageBox#msg QPushButton {
                border: none;
                background-color: #409EFF;
                color: white;
                font-size: 25px;
                min-width: 100px;
                min-height: 60px;
                margin: 20px 20px;
            }
            QMessageBox#msg QPushButton:hover {
                background-color: #66B1FF;
            }
        """)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.addButton(QMessageBox.Ok)
        msg.exec_()

    def validate_server_connection(self):
        settings = QSettings("MyApp", "WiFiConfig")
        server_ip = settings.value("server/ip", "")
        server_port = settings.value("server/port", "")
        device_id = settings.value("server/did", "")

        try:
            conn = pymysql.connect(
                host=server_ip,
                port=3306,
                user="admin",
                password="Tda250414",
                database="apppet",
                connect_timeout=5
            )
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            conn.close()
            return True, f"服务器连接成功\n当前数据上传至：{server_ip}:3306"
        except Exception as e:
            return False, f"连接失败：{str(e)}"

    def _start_loading_task(self, task_func, finish_callback, *args):
        """通用方法：启动加载对话框和执行后台任务"""
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.show()

        # 创建并启动线程
        self.worker_thread = QThread()
        self.worker = GenericWorker(task_func, *args)
        self.worker.moveToThread(self.worker_thread)
        if finish_callback is not None:
            self.worker.finished.connect(finish_callback)
        # self.worker.finished.connect(finish_callback)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.loading_dialog.close)
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()


class SerialManager(QObject, BaseWindow):
    # 定义信号
    data_received = pyqtSignal(str)  # 接收到新数据时发射
    status_changed = pyqtSignal(str)  # 状态变化时发射
    error_occurred = pyqtSignal(str, str)  # 错误发生时发射 (title, message)

    def __init__(self, port_name=None, baudrate=115200):
        super().__init__()
        self.serial_port = None
        self.port_name = port_name
        self.baudrate = baudrate
        self.is_running = False
        self.receive_buffer = bytearray()
        self.data_packets = []
        self.output_file = None
        # 用于存储原始字符串数据，保持接收顺序
        self.raw_data_strings = []

    def open_port(self):
        """打开串口"""
        try:
            self.serial_port = serial.Serial(
                port=self.port_name,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            self.status_changed.emit(f"已连接到 {self.port_name}")
            return True
        except Exception as e:
            self.error_occurred.emit("错误", f"连接失败: {str(e)}")
            return False

    def close_port(self):
        """关闭串口"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            # self.error_occurred.emit("提示", "串口已关闭")

    def send_command(self, command_hex):
        """发送16进制指令"""
        try:
            if not self.serial_port or not self.serial_port.is_open:
                self.error_occurred.emit("错误", "串口未连接")
                return False

            # 将16进制字符串转换为字节
            if isinstance(command_hex, str):
                command_bytes = bytes.fromhex(command_hex.replace(' ', ''))
            else:
                command_bytes = command_hex

            self.serial_port.write(command_bytes)
            # self.error_occurred.emit("提示", f"已发送指令: {command_bytes.hex(' ').upper()}")
            return True
        except Exception as e:
            self.error_occurred.emit("错误", f"发送失败: {str(e)}")
            return False

    def start_receiving(self):
        """开始接收数据"""
        if not self.serial_port or not self.serial_port.is_open:
            self.error_occurred.emit("错误", "串口未连接")
            return False

        self.is_running = True
        self.data_packets = []  # 清空之前的数据
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_file = f"serial_data_{timestamp}.txt"

        # 发送开始指令
        self.send_command("AA 55 00 06 00 01")
        return True

    def stop_receiving(self):
        """停止接收数据"""
        self.is_running = False
        self.send_command("AA 55 00 06 00 09")
        self.error_occurred.emit("提示", "停止测试")
        
        # 移除自动保存功能
        # if self.data_packets:
        #    self._save_to_file()
        #    # self._show_custom_message("提示", f"数据已保存到 {self.output_file}", QMessageBox.Information)

    def read_data(self):
        """新版串口读取线程"""
        while self.is_running:
            try:
                # 非阻塞读取（建议超时设为100ms）
                data = self.serial_port.read(max(1, self.serial_port.in_waiting))
                if data:
                    # 打印原始接收数据（调试用）
                    print(f"原始接收: {data.hex(' ')}")

                    # 追加到缓冲区
                    self.receive_buffer.extend(data)

                    # 立即处理缓冲区
                    self._process_buffer()

            except serial.SerialException as e:
                print(f"串口读取异常: {e}")
                break

    def _process_buffer(self):
        """改进版数据包处理逻辑，严格匹配12字节数据格式"""
        while len(self.receive_buffer) >= 12:  # 只有缓冲区有足够数据时才处理
            # 1. 查找包头位置 (AA 55 00 0C 00 04)
            header = bytes.fromhex("AA 55 00 0C 00 04")
            header_pos = -1

            # 在缓冲区中搜索包头（至少需要6字节）
            for i in range(len(self.receive_buffer) - 5):
                if self.receive_buffer[i:i + 6] == header:
                    header_pos = i
                    break

            # 2. 如果没有找到包头
            if header_pos == -1:
                # 如果缓冲区长度超过可能的最大包头前缀(5字节)，则丢弃多余数据
                if len(self.receive_buffer) > 5:
                    discarded = self.receive_buffer[:-5]
                    print(f"未找到包头，丢弃数据: {discarded.hex(' ')}")
                    self.receive_buffer = self.receive_buffer[-5:]
                return

            # 3. 丢弃包头前的无效数据
            if header_pos > 0:
                discarded = self.receive_buffer[:header_pos]
                print(f"丢弃包头前无效数据: {discarded.hex(' ')}")
                self.receive_buffer = self.receive_buffer[header_pos:]

            # 4. 检查是否收到完整包（12字节）
            if len(self.receive_buffer) < 12:
                return  # 等待更多数据

            # 5. 提取并处理完整数据包
            packet = self.receive_buffer[:12]

            # 6. 验证包尾（可选，根据实际协议需求）
            # 如果协议中数据包有固定结尾，可以在这里验证

            # 7. 解析数据包
            try:
                # 解析各字段（注意字节序和位置）
                sample_count = packet[6]  # 第7字节：采样次数（0-255）
                channel = packet[7]  # 第8字节：孔位号（1-4）
                fam = (packet[8] << 8) | packet[9]  # 第9-10字节：FAM（大端）
                vic = (packet[10] << 8) | packet[11]  # 第11-12字节：VIC（大端）


                # 格式化为字符串
                data_str = f"采样次数：{sample_count};孔位：{channel+1};FAM：{fam};VIC：{vic}"
                print(f"成功解析: {data_str}")

                # 保存原始格式的数据字符串
                raw_data_string = f"cycle:{sample_count};channel:{channel};fam:{fam};vic:{vic}"
                self.raw_data_strings.append(raw_data_string)
                
                # 保存数据并发射信号
                self.data_packets.append(data_str)
                self.data_received.emit(data_str)

                # 移除已处理的数据包
                self.receive_buffer = self.receive_buffer[12:]

            except Exception as e:
                error_msg = f"数据包解析错误: {e}\n原始数据: {packet.hex(' ')}"
                print(error_msg)
                self.error_occurred.emit("解析错误", error_msg)
                # 跳过这个包继续处理
                self.receive_buffer = self.receive_buffer[12:]

    def _save_to_file(self):
        """将接收到的数据保存到文件"""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                for packet in self.raw_data_strings:
                    f.write(packet + "\n")
        except Exception as e:
            print("错误", f"保存文件失败: {str(e)}")


class SerialThread(QThread):
    """串口线程，用于后台读取数据"""

    def __init__(self, serial_manager):
        super().__init__()
        self.serial_manager = serial_manager

    def run(self):
        self.serial_manager.read_data()

class GenericWorker(QObject):
    finished = pyqtSignal(bool, object)  # (success, message)

    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args

    def run(self):
        try:
            success, message = self.func(*self.args)
            self.finished.emit(success, message)
        except Exception as e:
            self.finished.emit(False, str(e))


class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LoadingDialog")
        self.setWindowTitle("数据上传中")
        self.setFixedSize(400, 250)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        self.setStyleSheet("""
            QDialog#LoadingDialog {
                background-color: #f0f7fd;
                border-radius: 10px;
            }
        """)

        layout = QVBoxLayout(self)
        self.label = QLabel("正在上传数据，请稍候...", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QDialog#LoadingDialog QLabel {
                background-color: #f0f7fd;
                font-size: 25px; 
            }
        """)


        # 使用环形进度条
        self.progress = QProgressBar(self)
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)

        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)


class MainWindow(QMainWindow, Ui_MainWindow, BaseWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.resize(resize_data[0], resize_data[1])
        self.setObjectName("MainWindow")
        self.setStatusBar(None)

        # 重新设置 pushButton_start 的布局
        self.pushButton_start.setParent(self.centralwidget)  # 重新设置父对象
        self.gridLayout.addWidget(self.pushButton_start, 0, 0, 1, 1)  # 添加到主布局
        
        # 移除原来的 groupBox_top_left
        self.groupBox_top_left.hide()
        self.groupBox_top_left.deleteLater()
        
        # 设置按钮的大小策略
        self.pushButton_start.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.pushButton_start.setFixedHeight(100)
        self.pushButton_start.setFixedWidth(350)  # 与 groupBox_chan 的宽度保持一致

        self.upload_thread = None
        self.loading_dialog = None
        self.setting_ui = None

        # 初始化数据存储结构
        self.data = {
            'channels': {i: {
                'cycle': [],  # 循环次数
                'fam': [],    # FAM原始数据
                'vic': [],    # VIC原始数据
                'fam_processed': None,  # FAM处理后的数据
                'vic_processed': None   # VIC处理后的数据
            } for i in range(4)}
        }
        
        self.current_type = 'fam'  # 当前显示的数据类型
        self.colors = ['#FF0000', '#00AA00', '#0000FF', '#FF00FF']  # 四个通道颜色
        self.display_mode = "analysis"  # 默认显示分析数据

        # 初始化串口管理
        self.serial_manager = None
        self.serial_thread = None
        self.is_serial_running = False

        # 隐藏停止按钮
        self.pushButton_stop.hide()
        
        # 连接按钮事件
        self.pushButton_start.clicked.connect(self.toggle_serial)
        self.pushButton_rename.clicked.connect(self.show_rename_dialog)
        self.pushButton_upload.clicked.connect(self.handle_upload)

        # 初始化计时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.seconds = 0
        self.sampling_count = 0
        self.is_running = False

        # 设置UI样式
        self._setup_ui_styles()

        # 设置logo图片位置
        self.setup_logo_position()

        # 加载数据并初始化图表
        self.init_plots()

        if TOUCH_OPTIMIZED:
            self._optimize_for_touch()

        # 添加PCR分析器
        self.pcr_analyzer = PCRAnalyzer()
        
        # 初始化结果标签
        self.result_labels = [
            self.label_result1, self.label_result2, 
            self.label_result3, self.label_result4
        ]
        
        self.ct_labels = [
            self.label_tp1, self.label_tp2, 
            self.label_tp3, self.label_tp4
        ]
        
        # 初始化标签显示
        for label in self.result_labels + self.ct_labels:
            label.setText("-")
            label.setStyleSheet("font-size: 16px;")
            
        # 创建数据切换按钮
        self.create_toggle_button()

    def reset_data(self):
        """重置数据结构"""
        self.data = {
            'channels': {i: {
                'cycle': [],
                'fam': [],
                'vic': [],
                'fam_processed': None,
                'vic_processed': None
            } for i in range(4)}
        }
        
        # 重置图表显示
        for plot in self.plots:
            ax = plot['axes']
            ax.clear()
            ax.grid(True, which='major', linestyle='-', linewidth=0.8, color='#cccccc', alpha=1)
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            plot['canvas'].draw()
            
        # 重置结果标签
        for label in self.result_labels + self.ct_labels:
            label.setText("-")
            
        # 隐藏切换按钮
        self.toggle_button.hide()
        
        # 重置显示模式
        self.display_mode = "analysis"

    def _setup_ui_styles(self):
        """集中设置所有UI元素的样式"""
        # 全局样式设置
        plt.rcParams.update({
            'font.size': 10,  # 全局字体大小
            'axes.labelsize': 10,  # 坐标轴标签大小
            'xtick.labelsize': 10,  # X轴刻度大小
            'ytick.labelsize': 10,  # Y轴刻度大小
        })

        # 主窗口样式
        self.setStyleSheet("""
            #MainWindow { 
                background-color: #efefef !important;
                padding-bottom: 20px;
            }
            QPushButton{
                background-color: transparent !important;
                font: bold "SimHei";
            }
            QLabel {
                background-color: transparent !important;
                font: 16px "SimHei";
                qproperty-alignment: AlignCenter;
            }
            QLineEdit {
                font: bold 16px "SimHei";
                qproperty-alignment: AlignCenter;
            }
        """)

        # 设置所有QLineEdit文本居中
        for widget in self.findChildren(QLineEdit):
            widget.setAlignment(Qt.AlignCenter)

        # 设置spinBox
        self.spinBox.setRange(40, 60)
        self.spinBox.setSingleStep(20)
        self.spinBox.setValue(40)
        self.spinBox.setMinimumWidth(150)
        self.label_time.setMinimumWidth(150)

        # 设置结果标签样式
        for i in range(1, 5):
            result_label = getattr(self, f'label_result{i}')
            tp_label = getattr(self, f'label_tp{i}')
            result_label.setStyleSheet("font-size: 22px;")
            tp_label.setStyleSheet("font-size: 22px;")

        # 设置label_hex的样式
        self.label_hex.setStyleSheet("""
            QLabel {
                min-height: 30px;
                max-height: 30px;
                padding: 5px;
                font-size: 22px;
            }
        """)

        self.label_stm1.setStyleSheet("""
            QLabel {
                text-align: right;
                font:26px "SimHei"; 
            }
        """)

        self.pushButton_stm.setFixedSize(80, 400)
        self.pushButton_stm.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                color: #db5860;
                text-align: left; 
                font:bold 25px "SimHei"; 
                padding:0
            }
        """)

        # 按钮样式
        self._setup_button_styles()

        # GroupBox样式
        self._setup_groupbox_styles()

        # 通道标签样式
        self._setup_channel_labels()

        # 时间标签和spinBox样式
        self._setup_time_controls()

    def _setup_button_styles(self):

        # 人员按钮
        self.pushButton_person.setStyleSheet("""
            QPushButton {
                border: 2px solid #FCB93C !important;
                background-color: #FCB93C;
                color: white !important;
                font: bold 25px "SimHei";
                border-radius: 4px;
                min-height: 70px;
            }
            QPushButton:hover {
                background-color: #FABE2E;
                border-color: #FABE2E !important;
            }
            QPushButton:pressed {
                background-color: #E5A922;
            }
        """)

        # 设置按钮
        self.pushButton_setting.setStyleSheet("""
            QPushButton {
                border: 2px solid #0372AE !important;
                background-color: #0372AE;
                color: white !important;
                font: bold 25px "SimHei";
                border-radius: 4px;
                min-height: 70px;
            }
            QPushButton:hover {
                background-color: #025BB5;
                border-color: #025BB5 !important;
            }
            QPushButton:pressed {
                background-color: #014D9C;
            }
        """)

        for button in [self.pushButton_rename, self.pushButton_upload]:
            button.setStyleSheet("""
                QPushButton {
                    font-family: SimHei;
                    font-size: 23px;
                }
            """)

        # 修改开始按钮样式
        self.start_style = """
            QPushButton {
                border: 2px solid #69B96B !important;
                background-color: #69B96B;
                color: white !important;
                font: bold 25px "SimHei";
                border-radius: 4px;
                margin: 0px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #5AAE61;
                border-color: #5AAE61 !important;
            }
            QPushButton:pressed {
                background-color: #4A964F;
            }
        """
        self.pushButton_start.setStyleSheet(self.start_style)

        # 添加停止状态样式
        self.stop_style = """
            QPushButton {
                border: 2px solid #FF0000 !important;
                background-color: #FF0000;
                color: white !important;
                font: bold 25px "SimHei";
                border-radius: 4px;
                margin: 0px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #E60000;
                border-color: #E60000 !important;
            }
            QPushButton:pressed {
                background-color: #CC0000;
            }
        """

    def toggle_serial(self):
        """切换串口启动/停止状态"""
        if not self.is_serial_running:
            self.start_serial()
        else:
            self.stop_serial()

    def _setup_groupbox_styles(self):

        # 新增触摸按钮容器的样式
        for box in [self.groupBox_top_left, self.groupBox_person]:
            box.setStyleSheet("""
                QGroupBox {
                    background-color: white !important;
                    border: 0px solid transparent !important;
                    padding: 0px !important;
                    margin: 0px !important;
                    min-height: 100px;
                    max-height: 100px;
                }
            """)
            # 移除布局边距
            box.layout().setContentsMargins(0, 0, 0, 0)
            box.layout().setSpacing(20)

        self.groupBox_top_left.setStyleSheet("""
            QGroupBox {
                background-color: white !important;
                border: none !important;
                padding: 0px !important;
                margin: 0px !important;
            }
        """)

        self.groupBox_chan.setStyleSheet("""
                QGroupBox {
                    background-color: white !important;
                    padding: 0 0 10px 0;
                }
            """)
        self.groupBox_top_right.setStyleSheet("""
                QGroupBox {
                    background-color: white !important;
                    padding: 0 0 0 20px;
                }
            """)


        self.groupBox_plot.setStyleSheet("""
            QGroupBox {
                background: white;
                border: 0px solid transparent;
                margin: 0px;
                padding: 0px;
            }
        """)

        # 各个图表容器
        for i in range(1, 9):
            plot_box = getattr(self, f"groupBox_plot{i}")
            plot_box.setStyleSheet("""
                QGroupBox {
                    background: white;
                    border: 1px solid #cfcfcf;
                margin: 0px;
                    padding: 0px;
                }
            """)
            plot_box.setMinimumSize(360, 400)  # 高度设为0表示不限制
            plot_box.setMaximumSize(360, 400)  # 高度设为Qt允许的最大值（相当于不限制）

        # 通道相关GroupBox
        groupboxes_chan = [
            self.groupBox_chan_title,
            self.groupBox_chan1,
            self.groupBox_chan2,
            self.groupBox_chan3,
            self.groupBox_chan4,
        ]

        colored_boxes = {
            self.groupBox_chan_title,
            self.groupBox_chan2,
            self.groupBox_chan4
        }

        for box in groupboxes_chan:
            if box in colored_boxes:
                box.setStyleSheet("""
                    QGroupBox {
                        background-color: #f0f7fd !important;
                        border: none !important;
                        padding: 0px !important;
                        margin: 0px !important;
                    }
                """)
            else:
                box.setStyleSheet("""
                    QGroupBox {
                        background-color: transparent !important;
                        border: none !important;
                        padding: 0px !important;
                        margin: 0px !important;
                    }
                """)

        self.groupBox_chan.setFixedWidth(350)
        self.groupBox_top_right.setFixedHeight(100)

        self.label_fam.hide()  # 隐藏 label_fam
        self.label_vic.hide()  # 隐藏 label_vic

    def _setup_channel_labels(self):
        """设置通道标签样式"""
        button_colors = {
            "label_chan1": "#d64d43",
            "label_chan2": "#e4984d",
            "label_chan3": "#5074e4",
            "label_chan4": "#a351e3"
        }
        for btn_name, border_color in button_colors.items():
            button = getattr(self, btn_name)
            button.setStyleSheet(f"""
                QLabel {{
                    border: none !important;
                    color: {border_color};
                    font: bold 25px "SimHei";
                    font-weight: normal;
                }}
            """)

    def _setup_time_controls(self):
        """设置时间相关控件样式"""
        self.label_time.setStyleSheet("""
            QLabel {
                background-color: #f8f8f8 !important;
                font: bold 25px "SimHei";
                color:#2979ff;
                qproperty-alignment: AlignCenter;
                padding-left: 20px;
                padding-right: 20px;
                border-bottom: 2px solid #2979ff;
                border-radius: 0;
                margin-right: 20px;
                min-height: 65px;
                max-height: 65px;
            }
        """)

        self.spinBox.setStyleSheet("""
            QSpinBox::up-button, QSpinBox::down-button {
                width: 35px;  /* 按钮宽度 */
                height: 35px; /* 按钮高度 */
            }
            QSpinBox {
                background-color: #f8f8f8 !important;
                font: bold 25px "SimHei";
                color:#2979ff;
                qproperty-alignment: AlignCenter;
                border-bottom: 2px solid #2979ff;
                border-radius: 0;
                margin-right: 20px;
            }
        """)

    def setup_logo_position(self):
        """设置logo图片在右上角靠边缘位置"""
        # 1. 移除groupBox_top_right中的空白标签
        # self.label_none2.setParent(None)
        self.label_none2.setStyleSheet("""
            QLabel {
                font-size: 35px;
                font-weight: bold;
                color:#006ba8;
            }
        """)

        # 2. 调整groupBox_top_right的布局
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)  # 移除内边距
        self.horizontalLayout_4.setSpacing(10)  # 设置控件间距

        # 3. 调整水平布局，添加弹簧将logo推到最右边
        self.horizontalLayout.insertStretch(1, 1)  # 在groupBox_2和logo之间添加弹簧

        # 4. 设置logo大小和对齐方式
        self.label_logo.setFixedSize(110, 110)  # 设置固定大小
        self.label_logo.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # 5. 加载logo图片
        logo_path = os.path.join(os.getcwd(), "img", "logo.jpg")  # 使用os.path.join构建路径
        
        if os.path.exists(logo_path):
            try:
                pixmap = QPixmap(logo_path)
                self.label_logo.setPixmap(pixmap.scaled(
                    self.label_logo.width(),
                    self.label_logo.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                ))
            except Exception as e:
                print(f"加载logo图片出错: {e}")
                self.label_logo.setText("Logo")  # 图片加载失败时显示文字
        else:
            print(f"logo图片不存在: {logo_path}")
            self.label_logo.setText("Logo")  # 图片不存在时显示文字

    # 以下是功能函数部分
    def init_plots(self):
        """初始化所有8个图表"""
        self.plots = []
        plot_titles = [
            "FAM-1", "FAM-2", "FAM-3", "FAM-4",
            "VIC-1", "VIC-2", "VIC-3", "VIC-4"
        ]

        # 定义统一的图表尺寸（单位：英寸）
        PLOT_WIDTH = 6  # 宽度
        PLOT_HEIGHT = 6  # 高度

        for i in range(8):
            group_box = getattr(self, f"groupBox_plot{i + 1}")

            # 清除原有布局
            if group_box.layout():
                while group_box.layout().count():
                    item = group_box.layout().takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()

            # 创建新图表，使用统一尺寸
            fig = Figure(facecolor='white', figsize=(PLOT_WIDTH, PLOT_HEIGHT))
            canvas = FigureCanvas(fig)
            
            # 调整子图边距，最大化绘图区域
            fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.1)
            
            ax = fig.add_subplot(111)

            # 设置图表标题，使用更小的字号
            ax.set_title(plot_titles[i], fontsize=12, pad=2)

            # 设置轴刻度字号
            ax.tick_params(axis='both', which='both',
                direction='in',
                length=2,
                width=0.5,
                labelsize=8)

            ax.grid(True, which='major', linestyle='-', linewidth=0.8, color='#cccccc', alpha=1)

            # 设置坐标轴样式
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)

            # 存储绘图对象
            plot_obj = {
                'figure': fig,
                'canvas': canvas,
                'axes': ax,
                'lines': [],
                'x_data': [],
                'y_data': []
            }

            # 设置布局
            layout = QVBoxLayout(group_box)
            layout.setContentsMargins(2, 2, 2, 2)  # 减小边距
            layout.addWidget(canvas)

            self.plots.append(plot_obj)

    def update_time(self):
        """更新时间的槽函数"""
        self.seconds += 1
        mins, secs = divmod(self.seconds, 60)
        time_str = f"{mins}分{secs:02d}秒"
        self.label_time.setText(time_str)

    def show_rename_dialog(self):
        """显示重命名对话框"""
        initial_name = self.label_dataname.text()
        dialog = RenameDialog(initial_name, self)
        dialog.rename_accepted.connect(self.update_data_name)
        dialog.exec_()

    def center(self):
        """窗口居中显示"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def _optimize_for_touch(self):
        """触摸屏优化方法"""
        # 调整按钮大小
        for btn in self.findChildren(QPushButton):
            btn.setMinimumHeight(TOUCH_BUTTON_HEIGHT)
            btn.setMinimumWidth(TOUCH_BUTTON_MIN_WIDTH)
            btn.setStyleSheet(btn.styleSheet() + f"""
                font-size: {TOUCH_FONT_SIZE}px;
                padding: 10px 20px;
            """)

        # 调整输入控件
        for input_widget in self.findChildren((QLineEdit, QSpinBox)):
            input_widget.setMinimumHeight(TOUCH_INPUT_HEIGHT)
            input_widget.setStyleSheet(input_widget.styleSheet() + f"""
                font-size: {TOUCH_FONT_SIZE}px;
                min-height: {TOUCH_INPUT_HEIGHT}px;
            """)

        # 调整标签
        for label in self.findChildren(QLabel):
            label.setStyleSheet(label.styleSheet() + f"""
                font-size: {TOUCH_FONT_SIZE}px;
                min-height: {TOUCH_INPUT_HEIGHT}px;
            """)

        # 调整图表区域边距
        for i in range(1, 9):
            plot_box = getattr(self, f"groupBox_plot{i}")
            plot_box.layout().setContentsMargins(
                TOUCH_SPACING, TOUCH_SPACING,
                TOUCH_SPACING, TOUCH_SPACING
            )

    def handle_upload(self):
        """处理数据上传"""
        try:
            # 检查是否有数据可保存
            if not self.serial_manager or not self.serial_manager.raw_data_strings:
                self._show_custom_message("错误", "没有可保存的数据", QMessageBox.Critical)
                return
                
            # 创建 data 文件夹（如果不存在）
            data_dir = os.path.join(os.getcwd(), "data")
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            
            # 使用label_dataname的值作为文件名
            data_name = self.label_dataname.text()
            filename = os.path.join(data_dir, f"{data_name}.txt")
            
            # 直接保存原始数据序列，不做任何处理和排序
            with open(filename, 'w', encoding='utf-8') as f:
                for data_line in self.serial_manager.raw_data_strings:
                    f.write(data_line + "\n")
            
            # 调用上传逻辑
            self._start_loading_task(
                task_func=self._upload_task,
                finish_callback=self._show_upload_result
            )
            
            # 显示保存成功提示
            self._show_custom_message("成功", f"数据已保存到 {filename}", QMessageBox.Information)
            
        except Exception as e:
            # 输出错误详情便于调试
            import traceback
            print(f"保存数据失败: {str(e)}")
            print(traceback.format_exc())
            self._show_custom_message("错误", f"保存数据失败: {str(e)}", QMessageBox.Critical)

    def _upload_task(self):
        try:
            success, msg = self.validate_server_connection()
            return True, msg
        except Exception as e:
            return False, f"上传失败: {str(e)}"

    def _show_upload_result(self, success, message):
        self._show_custom_message(
            "上传结果",
            message,
            QMessageBox.Information if success else QMessageBox.Critical
        )

    def set_setting_ui_reference(self, setting_ui):
        """设置SettingUI的引用并连接信号"""
        self.setting_ui = setting_ui
        self.setting_ui.serial_status_changed.connect(self.update_serial_button_status)

    def set_serial_manager(self, serial_manager):
        """从 SettingUI 设置串口管理器"""
        self.serial_manager = serial_manager
        if serial_manager:
            self.serial_thread = SerialThread(serial_manager)
            # 连接信号槽
            self.serial_manager.data_received.connect(self.on_data_received)
            self.serial_manager.status_changed.connect(self.on_status_changed)
            self.serial_manager.error_occurred.connect(self.on_serial_error)

    def on_serial_error(self, title, message):
        """处理串口错误"""
        self._show_custom_message(title, message, QMessageBox.Critical)

    def update_serial_button_status(self, is_connected, port_name=""):
        """根据串口状态更新按钮"""
        if is_connected:
            self.pushButton_stm.setText(f"已连接")
            self.pushButton_stm.setStyleSheet("""
                QPushButton {
                    color: #71b362;
                    border: none;
                    background: transparent;
                    text-align: left; 
                    font:bold 25px "SimHei"; 
                    padding:0
                }
            """)
        else:
            self.pushButton_stm.setText("未连接")
            self.pushButton_stm.setStyleSheet("""
                QPushButton {
                    color: #db5860;
                    border: none;
                    background: transparent;
                    text-align: left; 
                    font:bold 25px "SimHei"; 
                    padding:0
                }
            """)

    def start_serial(self):
        """启动串口通信"""
        try:
            if not self.serial_manager or not self.serial_manager.serial_port or not self.serial_manager.serial_port.is_open:
                self._show_custom_message("错误", "串口未连接，请先在设置界面连接串口", QMessageBox.Warning)
                return

            # 清空所有图表数据
            for plot in self.plots:
                plot['x_data'] = []
                plot['y_data'] = []
                ax = plot['axes']  # 获取图表的axes对象
                ax.clear()
                ax.grid(True, which='major', linestyle='-', linewidth=0.8, color='#cccccc', alpha=1)
                ax.spines['right'].set_visible(False)
                ax.spines['top'].set_visible(False)
                # 不显示任何文本，保持图表空白整洁
                for line in plot['lines']:
                    try:
                        if line in ax.lines:  # 确认线条还在图表中
                            line.remove()
                    except Exception:
                        pass  # 忽略删除失败的情况
                plot['lines'] = []
                plot['canvas'].draw()

            # 初始化结果标签
            for label in self.result_labels:
                label.setText("-")
            for label in self.ct_labels:
                label.setText("-")

            # 重置数据存储
            self.data = {
                'channels': {i: {
                    'cycle': [], 
                    'fam': [], 
                    'vic': [],
                    'fam_processed': None,
                    'vic_processed': None
                } for i in range(4)}
            }
            
            # 标记所有通道都是第一次接收数据
            self.is_first_sample_per_channel = {i: True for i in range(4)}

            # 启动计时
            self.seconds = 0
            self.is_running = True
            self.label_time.setText("0分00秒")
            self.timer.start(1000)

            # 使用新格式的时间作为数据名称
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.label_dataname.setText(current_time)
            
            # 隐藏切换按钮
            self.toggle_button.hide()

            # 开始接收数据
            if self.serial_manager.start_receiving():
                # 启动读取线程
                if self.serial_thread and not self.serial_thread.isRunning():
                    self.serial_thread.start()

                # 更新按钮状态
                self.is_serial_running = True
                self.pushButton_start.setText("停止检测")
                self.pushButton_start.setStyleSheet(self.stop_style)

        except Exception as e:
            print("Serial error:", str(e))
            self._show_custom_message("错误", f"串口通信错误: {str(e)}", QMessageBox.Critical)

    def stop_serial(self):
        """停止串口通信"""
        print("停止串口被调用")  # 调试用

        # 停止计时
        if self.is_running:
            self.timer.stop()
            self.is_running = False

        # 停止串口通信
        if self.serial_manager:
            try:
                self.serial_manager.stop_receiving()
            except Exception as e:
                print(f"停止串口时出错: {e}")

        # 更新状态
        self.is_serial_running = False
        self.update_button_state()

        # 处理数据并更新显示
        self._process_and_display_results()
        
        # 显示切换按钮
        self.toggle_button.show()

    def update_button_state(self):
        """更新按钮状态"""
        if self.is_serial_running:
            self.pushButton_start.setText("停止检测")
            self.pushButton_start.setStyleSheet(self.stop_style)
        else:
            self.pushButton_start.setText("开始检测")
            self.pushButton_start.setStyleSheet(self.start_style)

    def on_data_received(self, data_str):
        try:
            # 解析数据字符串
            parts = data_str.split(';')
            data_dict = {}
            for part in parts:
                key, value = part.split('：')
                data_dict[key.strip()] = value.strip()

            # 提取关键数据
            sample_count = int(data_dict['采样次数'])
            channel = int(data_dict['孔位']) - 1  # 转换为0-3
            fam_value = int(data_dict['FAM'])
            vic_value = int(data_dict['VIC'])

            # 计算实际的FAM和VIC探头位置
            fam_channel = channel
            vic_channel = (channel - 1) % 4  # 计算VIC探头位置

            # 判断是否需要记录数据
            should_record_fam = True
            should_record_vic = True
            
            # 检测采样次数异常变量
            cycle_error_detected = False

            # 检查当前采样次数是否比通道中上一个数据的采样次数小，如果是则抛弃该数据
            # 但跳过每个通道的第一个数据，防止新一轮采集无法开始
            
            # 检查FAM通道数据
            if should_record_fam and not self.is_first_sample_per_channel[fam_channel] and len(self.data['channels'][fam_channel]['cycle']) > 0:
                last_cycle = self.data['channels'][fam_channel]['cycle'][-1]
                if sample_count < last_cycle:
                    print(f"抛弃FAM通道错误数据: 当前采样次数 {sample_count} 小于上一次 {last_cycle}")
                    should_record_fam = False
                    cycle_error_detected = True
            else:
                # 标记该通道不再是第一次接收数据
                self.is_first_sample_per_channel[fam_channel] = False
            
            # 检查VIC通道数据
            if should_record_vic and not self.is_first_sample_per_channel[vic_channel] and len(self.data['channels'][vic_channel]['cycle']) > 0:
                last_cycle = self.data['channels'][vic_channel]['cycle'][-1]
                if sample_count < last_cycle:
                    print(f"抛弃VIC通道错误数据: 当前采样次数 {sample_count} 小于上一次 {last_cycle}")
                    should_record_vic = False
                    cycle_error_detected = True
            else:
                # 标记该通道不再是第一次接收数据
                self.is_first_sample_per_channel[vic_channel] = False
            
            # 如果检测到采样次数异常，自动停止数据采集
            if cycle_error_detected:
                # 发送停止指令
                self.serial_manager.send_command("AA 55 00 06 00 09")
                # 停止计时
                self.timer.stop()
                self.is_running = False
                # 更新按钮状态
                self.is_serial_running = False
                self.update_button_state()
                # 处理数据并更新显示
                self._process_and_display_results()

                return
            
            # 如果两个通道数据都需要抛弃，则直接跳过处理
            if not should_record_fam and not should_record_vic:
                print(f"采样次数错误 ({sample_count})，抛弃此数据包")
                return

            # 第一组循环时，VIC探头在孔位外
            if sample_count == 1 and channel == 0:
                should_record_vic = False

            # 最后一组循环时，FAM探头在孔位外
            if sample_count == self.spinBox.value() and channel == 3:
                should_record_fam = False

            # 更新数据存储
            if should_record_fam:
                self.data['channels'][fam_channel]['cycle'].append(sample_count)
                self.data['channels'][fam_channel]['fam'].append(fam_value)

            if should_record_vic:
                self.data['channels'][vic_channel]['cycle'].append(sample_count)
                self.data['channels'][vic_channel]['vic'].append(vic_value)

            # 更新图表
            self._update_plot(channel, sample_count, fam_value, vic_value, should_record_fam, should_record_vic)

            # 更新界面显示
            self.label_hex.setText(f"{data_str}")

            # 检查是否达到自动停止条件
            if sample_count == self.spinBox.value() + 1:  # 当采集完最后一个cycle时
                # 发送停止指令
                self.serial_manager.send_command("AA 55 00 06 00 09")
                # 停止计时
                self.timer.stop()
                self.is_running = False
                # 更新按钮状态
                self.is_serial_running = False
                self.update_button_state()
                # 处理数据并更新显示
                self._process_and_display_results()
                # 显示完成提示
                self._show_custom_message("完成", f"已完成{self.spinBox.value()}次循环的数据采集", QMessageBox.Information)

        except BaseException as e:
            print(f"数据解析错误: {e}")

    def _update_plot(self, channel, x, fam_y, vic_y, should_record_fam, should_record_vic):
        """更新指定通道的图表"""
        # 计算实际的FAM和VIC探头位置
        fam_channel = channel
        vic_channel = (channel - 1) % 4

        # 更新FAM图表 (0-3)
        if should_record_fam:
            fam_plot = self.plots[fam_channel]
            self._update_single_plot(fam_plot, x, fam_y, 'FAM', fam_channel)
        
        # 更新VIC图表 (4-7)
        if should_record_vic:
            vic_plot = self.plots[vic_channel + 4]
            self._update_single_plot(vic_plot, x, vic_y, 'VIC', vic_channel)

    def _update_single_plot(self, plot, x, y, data_type, channel):
        """更新单个图表"""
        try:
            ax = plot['axes']
            
            # 添加新的数据点到图表的数据存储中
            if 'x_data' not in plot:
                plot['x_data'] = []
                plot['y_data'] = []
            
            plot['x_data'].append(x)
            plot['y_data'].append(y)
            
            # 清除当前图表
            ax.clear()
            
            # 设置图表样式
            ax.grid(True, which='major', linestyle='-', linewidth=0.8, color='#cccccc', alpha=1)
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.tick_params(axis='both', which='both', 
                          direction='in', 
                          length=2, 
                          width=0.5,
                          labelsize=8)
            
            # 绘制所有累积的数据点
            ax.plot(plot['x_data'], plot['y_data'], 
                   color=self.colors[channel], 
                   linewidth=1.2, 
                   alpha=0.8)
            
            # 设置标题
            ax.set_title(f'{data_type}-{channel+1}', fontsize=12, pad=2)
            
            # 设置y轴范围和刻度
            if len(plot['y_data']) > 1:
                ymin = min(plot['y_data'])
                ymax = max(plot['y_data'])
                margin = (ymax - ymin) * 0.1  # 10%的边距
                ax.set_ylim(ymin - margin, ymax + margin)
                
                # 确保至少显示5个刻度
                ax.yaxis.set_major_locator(plt.MaxNLocator(5))
            
            # 调整图表边距
            plot['figure'].subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.1)
            
            # 重绘图表
            plot['canvas'].draw()
        except Exception as e:
            print(f"更新图表时出错: {e}")

    def _process_and_display_results(self):
        """处理数据并更新显示"""

        self.toggle_button.show()

        # 处理所有通道的数据并更新结果
        for channel in range(4):
            # 获取原始数据
            fam_data = self.data['channels'][channel]['fam']
            vic_data = self.data['channels'][channel]['vic']

            # 打印数据长度信息，用于调试
            print(f"通道{channel+1} FAM数据长度: {len(fam_data)}, VIC数据长度: {len(vic_data)}")

            # 处理FAM数据
            if fam_data and len(fam_data) > 5:  # 确保有足够的数据点进行处理
                fam_processed = self.pcr_analyzer.process_data(fam_data)
                self.data['channels'][channel]['fam_processed'] = fam_processed
                print(f"通道{channel+1} FAM处理结果: 趋势长度={len(fam_processed['trend']) if fam_processed['trend'] is not None else 0}, 阳性={fam_processed['positive']}")
            else:
                fam_processed = {
                    'positive': False,
                    'ct_found': False,
                    'ct_value': 0.0,
                    'trend': None
                }
                self.data['channels'][channel]['fam_processed'] = fam_processed
            
            # 处理VIC数据
            if vic_data and len(vic_data) > 5:  # 确保有足够的数据点进行处理
                vic_processed = self.pcr_analyzer.process_data(vic_data)
                self.data['channels'][channel]['vic_processed'] = vic_processed
                print(f"通道{channel+1} VIC处理结果: 趋势长度={len(vic_processed['trend']) if vic_processed['trend'] is not None else 0}, 阳性={vic_processed['positive']}")
            else:
                vic_processed = {
                    'positive': False,
                    'ct_found': False,
                    'ct_value': 0.0,
                    'trend': None
                }
                self.data['channels'][channel]['vic_processed'] = vic_processed
            
            # 更新结果标签
            self._update_result_labels(channel, fam_processed, vic_processed)

            # 更新图表显示处理后的数据
            self._update_processed_plot(channel, None, fam_processed, vic_processed)
        
        # 输出处理完成信息
        print("数据处理完成")

    def _update_result_labels(self, channel, fam_processed, vic_processed):
        """更新结果标签"""
        # 更新FAM结果
        fam_result = "阳性" if fam_processed['positive'] else "阴性"
        fam_ct = f"{fam_processed['ct_value']:.1f}" if fam_processed['ct_found'] else "-"
        
        # 更新VIC结果
        vic_result = "阳性" if vic_processed['positive'] else "阴性"
        vic_ct = f"{vic_processed['ct_value']:.1f}" if vic_processed['ct_found'] else "-"
        
        # 更新结果标签（FAM和VIC结果显示在同一个标签中）
        self.result_labels[channel].setText(f"{fam_result}/{vic_result}")
        self.ct_labels[channel].setText(f"{fam_ct}/{vic_ct}")

    def on_status_changed(self, status_msg):
        """状态变化时的处理"""
        self.label_hex.setText(status_msg)

    def _update_processed_plot(self, channel, cycles, fam_processed, vic_processed):
        """更新处理后的数据到图表"""
        # 更新FAM图表 (0-3)
        fam_plot = self.plots[channel]
        self._update_single_processed_plot(fam_plot, fam_processed, 'FAM', channel)
        
        # 更新VIC图表 (4-7)
        vic_plot = self.plots[channel + 4]
        self._update_single_processed_plot(vic_plot, vic_processed, 'VIC', channel)

    def _update_single_processed_plot(self, plot, processed_data, data_type, channel):
        """更新单个处理后的数据图表"""
        ax = plot['axes']
        try:
            ax.clear()
            
            # 设置图表样式
            ax.grid(True, which='major', linestyle='-', linewidth=0.8, color='#cccccc', alpha=1)
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.tick_params(axis='both', which='both',
                direction='in',
                length=2,
                width=0.5,
                labelsize=10)
            
            # 检查是否有处理过的数据
            if processed_data['trend'] is not None and len(processed_data['trend']) > 0:
                # 创建x轴数据 (序号从1开始)
                x_data = np.arange(1, len(processed_data['trend']) + 1)
                
                # 绘制处理后的趋势线 - 只保留这一种处理曲线
                ax.plot(x_data, processed_data['trend'],
                       color=self.colors[channel],
                       linewidth=2)
                
                # 添加阈值线，但不添加文字
                ax.axhline(800.0, color='gray', linestyle=':', alpha=0.5)
                
                # 如果找到CT值，添加标记
                if processed_data['positive'] and processed_data['ct_found']:
                    ct_value = processed_data['ct_value']
                    if 1 <= ct_value <= len(processed_data['trend']):  # 确保CT值在x轴范围内
                        ax.axvline(ct_value,
                                  color='red',
                                  linestyle='--',
                                  alpha=0.7)
                        ax.text(ct_value,
                               800.0,
                               f"CT={ct_value:.1f}",
                               color='red',
                               ha='center',
                               fontsize=10)
            else:
                # 如果没有处理后的数据，保持图表空白
                pass
            
            # 设置标题和标签
            ax.set_title(f'{data_type}-{channel+1}')
            ax.grid(True, alpha=0.3)
            
            # 重绘图表
            plot['canvas'].draw()
        except Exception as e:
            print(f"更新图表时出错: {e}")

    def closeEvent(self, event):
        """窗口关闭事件"""
        # 停止串口通信
        if hasattr(self, 'serial_manager') and self.serial_manager:
            if hasattr(self.serial_manager, 'is_running') and self.serial_manager.is_running:
                self.serial_manager.stop_receiving()

            # 关闭串口
            self.serial_manager.close_port()

        # 等待线程结束
        if hasattr(self, 'serial_thread') and self.serial_thread and self.serial_thread.isRunning():
            self.serial_thread.quit()
            self.serial_thread.wait()

        super().closeEvent(event)

    @pyqtSlot(str)
    def update_data_name(self, new_name):
        """更新数据名称"""
        self.label_dataname.setText(new_name)

    def create_toggle_button(self):
        """创建数据显示切换按钮"""
        self.toggle_button = QPushButton("显示原始数据", self.groupBox_plot)
        self.toggle_button.setObjectName("pushButton_toggle")
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #71b362;
                color: white;
                border: none;
                border-radius: 4px;
                font: bold 30px "SimHei";
                min-height: 30px;
                max-width: 200px;
                padding: 5px 15px;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #85c177;
            }
        """)
        
        # 创建水平布局来实现居中
        hbox = QHBoxLayout()
        hbox.addStretch()  # 左侧弹簧
        hbox.addWidget(self.toggle_button)
        hbox.addStretch()  # 右侧弹簧
        
        # 添加到label_hex下方的位置
        self.gridLayout_2.addLayout(hbox, 1, 0, 1, 4)
        
        # 连接切换按钮事件
        self.toggle_button.clicked.connect(self.toggle_display_mode)
        
        # 初始时按钮隐藏
        self.toggle_button.hide()
        
    def toggle_display_mode(self):
        """切换数据显示模式"""
        if self.display_mode == "analysis":
            self.display_mode = "raw"
            self.toggle_button.setText("显示分析数据")
            self.toggle_button.setStyleSheet("""
                QPushButton {
                    background-color: #409EFF;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font: bold 30px "SimHei";
                    min-height: 30px;
                    max-width: 200px;
                    padding: 5px 15px;
                    margin-top: 5px;
                }
                QPushButton:hover {
                    background-color: #66B1FF;
                }
            """)
            # 显示原始数据
            self.show_raw_data()
        else:
            self.display_mode = "analysis"
            self.toggle_button.setText("显示原始数据")
            self.toggle_button.setStyleSheet("""
                QPushButton {
                    background-color: #71b362;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font: bold 30px "SimHei";
                    min-height: 30px;
                    max-width: 200px;
                    padding: 5px 15px;
                    margin-top: 5px;
                }
                QPushButton:hover {
                    background-color: #85c177;
                }
            """)
            # 显示分析数据
            self.show_analysis_data()

    def show_raw_data(self):
        """显示原始数据"""
        for channel in range(4):
            channel_data = self.data['channels'][channel]
            if len(channel_data['fam']) > 0:
                # 更新FAM图表 (0-3)
                fam_plot = self.plots[channel]
                ax = fam_plot['axes']
                ax.clear()
                
                # 设置图表样式
                ax.grid(True, which='major', linestyle='-', linewidth=0.8, color='#cccccc', alpha=1)
                ax.spines['right'].set_visible(False)
                ax.spines['top'].set_visible(False)

                ax.tick_params(axis='both', which='both',
                    direction='in',
                    length=2,
                    width=0.5,
                    labelsize=10)
                
                # 绘制原始数据
                ax.plot(range(1, len(channel_data['fam']) + 1), channel_data['fam'], 
                       color=self.colors[channel], 
                       linewidth=1.2, 
                       alpha=0.8)
                
                # 设置标题和轴标签
                ax.set_title(f'FAM-{channel+1}', fontsize=12, pad=2)
                fam_plot['canvas'].draw()

                # 更新VIC图表 (4-7)
                vic_plot = self.plots[channel + 4]
                ax = vic_plot['axes']
                ax.clear()
                
                # 设置图表样式
                ax.grid(True, which='major', linestyle='-', linewidth=0.8, color='#cccccc', alpha=1)
                ax.spines['right'].set_visible(False)
                ax.spines['top'].set_visible(False)

                
                # 绘制原始数据
                ax.plot(range(1, len(channel_data['vic']) + 1), channel_data['vic'], 
                       color=self.colors[channel], 
                       linewidth=1.2, 
                       alpha=0.8)
                
                # 设置标题和轴标签
                ax.set_title(f'VIC-{channel+1}', fontsize=12, pad=2)
                vic_plot['canvas'].draw()

    def show_analysis_data(self):
        """显示分析数据"""
        for channel in range(4):
            channel_data = self.data['channels'][channel]
            if channel_data['fam_processed'] is not None:
                # 更新FAM图表 (0-3)
                fam_plot = self.plots[channel]
                ax = fam_plot['axes']
                ax.clear()
                
                # 设置图表样式
                ax.grid(True, which='major', linestyle='-', linewidth=0.8, color='#cccccc', alpha=1)
                ax.spines['right'].set_visible(False)
                ax.spines['top'].set_visible(False)
                ax.tick_params(axis='both', which='both',
                    direction='in',
                    length=2,
                    width=0.5,
                    labelsize=10)
                
                # 绘制处理后的数据 - 使用trend数据
                if channel_data['fam_processed']['trend'] is not None:
                    trend_data = channel_data['fam_processed']['trend']
                    x_data = np.arange(1, len(trend_data) + 1)
                    ax.plot(x_data, trend_data, 
                           color=self.colors[channel], 
                           linewidth=2)
                    
                    # 添加阈值线
                    ax.axhline(800.0, color='gray', linestyle=':', alpha=0.5)
                    
                    # 如果找到CT值，添加标记
                    if channel_data['fam_processed']['positive'] and channel_data['fam_processed']['ct_found']:
                        ct_value = channel_data['fam_processed']['ct_value']
                        if 1 <= ct_value <= len(trend_data):  # 确保CT值在x轴范围内
                            ax.axvline(ct_value,
                                     color='red',
                                     linestyle='--',
                                     alpha=0.7)
                            ax.text(ct_value,
                                  800.0,
                                  f"CT={ct_value:.1f}",
                                  color='red',
                                  ha='center',
                                  fontsize=10)
                
                # 设置标题
                ax.set_title(f'FAM-{channel+1}', fontsize=12, pad=2)
                
                # 调整图表边距
                fam_plot['figure'].subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.1)
                fam_plot['canvas'].draw()

                # 更新VIC图表 (4-7)
                vic_plot = self.plots[channel + 4]
                ax = vic_plot['axes']
                ax.clear()
                
                # 设置图表样式
                ax.grid(True, which='major', linestyle='-', linewidth=0.8, color='#cccccc', alpha=1)
                ax.spines['right'].set_visible(False)
                ax.spines['top'].set_visible(False)
                ax.tick_params(axis='both', which='both',
                    direction='in',
                    length=2,
                    width=0.5,
                    labelsize=10)
                
                # 绘制处理后的数据 - 使用trend数据
                if channel_data['vic_processed'] is not None and channel_data['vic_processed']['trend'] is not None:
                    trend_data = channel_data['vic_processed']['trend']
                    x_data = np.arange(1, len(trend_data) + 1)
                    ax.plot(x_data, trend_data, 
                           color=self.colors[channel], 
                           linewidth=2)
                    
                    # 添加阈值线
                    ax.axhline(800.0, color='gray', linestyle=':', alpha=0.5)
                    
                    # 如果找到CT值，添加标记
                    if channel_data['vic_processed']['positive'] and channel_data['vic_processed']['ct_found']:
                        ct_value = channel_data['vic_processed']['ct_value']
                        if 1 <= ct_value <= len(trend_data):  # 确保CT值在x轴范围内
                            ax.axvline(ct_value,
                                     color='red',
                                     linestyle='--',
                                     alpha=0.7)
                            ax.text(ct_value,
                                  800.0,
                                  f"CT={ct_value:.1f}",
                                  color='red',
                                  ha='center',
                                  fontsize=10)
                
                # 设置标题
                ax.set_title(f'VIC-{channel+1}', fontsize=12, pad=2)
                
                # 调整图表边距
                vic_plot['figure'].subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.1)
                vic_plot['canvas'].draw()

    def handle_error(self, error_msg, error_title="错误"):
        """统一的错误处理方法"""
        QMessageBox.critical(self, error_title, error_msg)
        
    def start_experiment(self):
        """开始新实验"""
        try:
            # 重置数据结构
            self.reset_data()
            
            # 初始化串口通信
            if not self.serial_manager or not self.serial_manager.is_open():
                raise Exception("串口未连接")
                
            # 开始数据采集
            self.is_running = True
            self.timer.start(1000)  # 启动计时器
            self.toggle_button.show()  # 显示切换按钮
            
        except Exception as e:
            self.handle_error(f"启动实验失败: {str(e)}")
            self.is_running = False
            self.timer.stop()
            
    def process_data(self, channel, data_type, value):
        """处理接收到的数据"""
        try:
            if channel not in self.data['channels']:
                raise ValueError(f"无效的通道号: {channel}")
                
            channel_data = self.data['channels'][channel]
            
            # 添加数据
            if data_type == 'fam':
                channel_data['fam'].append(value)
            elif data_type == 'vic':
                channel_data['vic'].append(value)
            else:
                raise ValueError(f"无效的数据类型: {data_type}")
                
            # 更新显示
            if self.display_mode == "raw":
                self.show_raw_data()
            else:
                # 处理数据
                if len(channel_data['fam']) > 0:
                    channel_data['fam_processed'] = self.pcr_analyzer.process_data(channel_data['fam'])
                if len(channel_data['vic']) > 0:
                    channel_data['vic_processed'] = self.pcr_analyzer.process_data(channel_data['vic'])
                self.show_analysis_data()
                
        except Exception as e:
            self.handle_error(f"数据处理错误: {str(e)}")
            
    def stop_experiment(self):
        """停止实验"""
        try:
            self.is_running = False
            self.timer.stop()
            
            # 停止串口通信
            if self.serial_manager:
                self.serial_manager.stop_receiving()
                
            # 保存数据
            self.save_experiment_data()
            
        except Exception as e:
            self.handle_error(f"停止实验失败: {str(e)}")
            
    def save_experiment_data(self):
        """保存实验数据"""
        try:
            # 获取当前时间作为文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pcr_data_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                for channel in range(4):
                    channel_data = self.data['channels'][channel]
                    for i in range(len(channel_data['fam'])):
                        f.write(f"cycle:{i};channel:{channel};"
                               f"fam:{channel_data['fam'][i]};"
                               f"vic:{channel_data['vic'][i]}\n")
                               
            QMessageBox.information(self, "保存成功", f"数据已保存至文件: {filename}")
            
        except Exception as e:
            self.handle_error(f"保存数据失败: {str(e)}")


class RenameDialog(QDialog):
    rename_accepted = pyqtSignal(str)

    def __init__(self, current_name, parent=None):
        super().__init__(parent)
        self.setObjectName("RenameDialog")
        self.resize(resize_data[0], resize_data[1])
        self.initial_name = current_name
        self.setup_ui(current_name)

    def setup_ui(self, current_name):

        self.setStyleSheet("""
            QDialog#RenameDialog {
                background-color: white;
            }
            QDialog#RenameDialog QWidget {
                background-color: white;
            }
            QDialog#RenameDialog QLabel {
                color: #cdcdcd;
                font-size: 32px;
            }
        """)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 100)
        main_layout.setSpacing(10)  # 减少组件间垂直间距

        # 顶部栏
        top_bar = QWidget(self)
        top_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # 返回按钮
        self.back_btn = QPushButton("←返回", self)
        self.back_btn.setMinimumSize(60, 30)
        self.back_btn.setStyleSheet("""
            QPushButton {
                font: 35px "黑体";
                color: #2979ff;
                background: transparent;
                border: none;
                padding: 0;
                height: 100px;
            }
            QPushButton:hover {
                color: #2979ff;
            }
        """)
        self.back_btn.clicked.connect(self.close)
        top_layout.addWidget(self.back_btn)
        top_layout.addStretch()

        main_layout.addWidget(top_bar, stretch=0)

        # 输入框（设置初始值）
        self.input_box = QLineEdit(current_name, self)
        self.input_box.setMaxLength(20)  # 限制最多 20 个字符
        self.input_box.setStyleSheet("""
            QLineEdit {
                font-size: 38px;
                border: 3px solid #2979ff;
                border-radius: 10px;
                padding: 25px;
                min-height: 30px;
                max-height: 30px;
            }
        """)
        main_layout.addWidget(self.input_box)


        self.label_warning = QLabel("最多输入 20 个字符", self)
        self.label_warning.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.label_warning.setStyleSheet("""
            QLabel {
                color: #cdcdcd;
                font: 30px "黑体";
                qproperty-alignment: AlignCenter;
                min-height: 30px;
                max-height: 30px;
            }
        """)
        main_layout.addWidget(self.label_warning)

        # 按钮区域
        btn_widget = QWidget(self)
        btn_layout = QHBoxLayout(btn_widget)
        btn_widget.setFixedHeight(70)  # 设置固定高度200px
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(70)  # 按钮间水平间距
        btn_layout.addStretch()

        self.ok_btn = QPushButton("确定", self)
        self.ok_btn.setStyleSheet("""
            QPushButton {
                font: bold 30px "黑体";
                color: white;
                background-color: #2979ff;
                border: none;
                border-radius: 4px;
                padding: 15px 24px;
                min-height: 30px;
                max-height: 30px;
            }
            QPushButton:hover {
                background-color: #1a68e6;
            }
            QPushButton:pressed {
                background-color: #0d5cd8;
            }
        """)
        self.cancel_btn = QPushButton("重置", self)  # 改为"重置"
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                font: bold 30px "黑体";
                color: #333333;
                background-color: #f0f0f0;
                border: none;
                border-radius: 4px;
                padding: 15px 24px;
                min-height: 30px;
                max-height: 30px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addStretch()

        main_layout.addWidget(btn_widget)

        self.blank_label = QLabel(self)
        self.blank_label.setFixedHeight(10)  # 设置固定高度200px
        self.blank_label.setStyleSheet("background-color: transparent;")  # 透明背景
        btn_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.blank_label)

        # 虚拟键盘
        self.keyboard = VirtualKeyboard(self)
        main_layout.addWidget(self.keyboard)

        # 信号连接
        self.ok_btn.clicked.connect(self.on_accept)
        self.cancel_btn.clicked.connect(self.on_reset)
        self.input_box.setFocus()

    def on_accept(self):
        """确定按钮点击事件"""
        new_name = self.input_box.text()
        self.rename_accepted.emit(new_name)  # 发射信号
        self.accept()

    def on_reset(self):
        """重置按钮点击事件"""
        self.input_box.setText(self.initial_name)  # 重置为初始值


class VirtualKeyboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("VirtualKeyboard")
        self.caps_lock = False
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
            QWidget#VirtualKeyboard QPushButton {
                font-size: 30px;
                min-height: 85px;
                min-height: 85px;
                margin: 0 5px;
                background-color: #409eff;
                border: none;
                color: white;
                qproperty-alignment: AlignRight;
            }
            QWidget#VirtualKeyboard QPushButton:pressed {
                background-color: #f0f0f0;
                color: #f0f0f0;
            }
            QWidget#VirtualKeyboard QPushButton[specialkey="true"] {
                -color: #f0f0f0;
            }
            QWidget#VirtualKeyboard QPushButton[shiftkey="true"] {
                background-color: #f0f0f0;
                color: #585858;
            }
            QWidget#VirtualKeyboard QPushButton[shiftkey="true"][active="true"] {
                background-color: #f0f0f0;
                color: #409eff;
            }
        """)
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # 移除外部边距
        layout.setHorizontalSpacing(5)         # 水平间距5像素
        layout.setVerticalSpacing(10)          # 行间距固定为10像素

        # 键盘按键布局
        self.keys = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '<-'],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
            ['↑', 'z', 'x', 'c', 'v', 'b', 'n', 'm', '_']
        ]

        # 创建按键
        self.buttons = []
        for row, row_keys in enumerate(self.keys):
            button_row = []
            for col, key in enumerate(row_keys):
                btn = self.create_key_button(key)
                if key == '↑':
                    btn.clicked.connect(self.toggle_caps)
                else:
                    btn.clicked.connect(lambda _, k=key: self.on_key_pressed(k))
                layout.addWidget(btn, row, col)
                button_row.append(btn)
            self.buttons.append(button_row)

        self.setLayout(layout)

    def create_key_button(self, text):
        """创建键盘按钮"""
        btn = QPushButton(text.upper() if self.caps_lock and text.isalpha() else text)
        btn.setProperty("shiftkey", text == '↑')

        # 特殊样式处理
        if text == '↑':
            self.shift_button = btn
            btn.setProperty("active", self.caps_lock)
        return btn


    def toggle_caps(self):
        """切换大小写状态"""
        self.caps_lock = not self.caps_lock

        # 更新Shift键样式
        if self.shift_button:
            self.shift_button.setProperty("active", self.caps_lock)
            self.shift_button.style().polish(self.shift_button)

        # 更新所有字母键的显示
        for row in range(1, 4):  # 只更新字母行
            for col in range(len(self.buttons[row])):
                btn = self.buttons[row][col]
                text = self.keys[row][col]
                if text.isalpha():
                    btn.setText(text.upper() if self.caps_lock else text.lower())

    def on_key_pressed(self, key):
        """处理按键点击"""
        parent_dialog = self.parent()
        if isinstance(parent_dialog, RenameDialog):
            input_box = parent_dialog.input_box
            if key == '<-':
                input_box.backspace()
            else:
                # 根据大小写状态插入字符
                char = key.upper() if self.caps_lock and key.isalpha() else key
                input_box.insert(char)


class WifiSelectionDialog(QDialog):
    def __init__(self, parent=None, wifi_list=None):
        super().__init__(parent)
        self.parent_ui = parent
        if parent:
            self.setup_background_blur()
        self.setMinimumSize(700, 900)
        # 移除标题栏但保留边框
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setup_ui()

        self.setWindowTitle("SearchWifi")
        self.setWindowIcon(QIcon("img/logo.ico"))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)  # 移除标题栏问号
        self.setMinimumSize(700, 900)
        self.setContentsMargins(20, 20, 20, 40)

        self.wifi_list_data = wifi_list
        # 初始加载WiFi列表
        self.refresh_wifi_list()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
        """)

        self.info_label = QLabel("正在搜索WiFi网络...")
        self.info_label.setStyleSheet("""
            QLabel {
                font-size: 25px; 
                font-weight: bold;
                padding: 10px 0;
                color: #333333;
            }
        """)
        layout.addWidget(self.info_label)

        self.wifi_list = QListWidget()
        self.wifi_list.setStyleSheet("""
            QListWidget {
                font-size: 25px;
                border: 1px solid #DCDFE6;
                border-radius: 10px;
                background-color: white;
            }
            QListWidget::item {
                padding: 15px;
            }
            QListWidget::item:selected {
                background-color: #409EFF;
                color: white;
            }
        """)
        layout.addWidget(self.wifi_list)

        # 底部按钮
        button_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("关闭")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #fe2b1a;
                color: white;
                min-width: 100px;
                min-height: 65px;
            }
            QPushButton:hover {
                background-color: #fb6c37;
            }
        """)
        self.refresh_btn.clicked.connect(self.close)

        self.confirm_btn = QPushButton("确认")
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #409EFF;
                color: white;
                min-width: 100px;
                min-height: 65px;
            }
            QPushButton:hover {
                background-color: #66B1FF;
            }
        """)
        self.confirm_btn.clicked.connect(self.confirm_selection)

        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.confirm_btn)
        button_layout.setContentsMargins(0, 20, 0, 0)
        layout.addLayout(button_layout)


    def refresh_wifi_list(self):
        """直接使用预加载数据"""
        self.wifi_list.clear()

        if not self.wifi_list_data:
            self.info_label.setText("无可用网络数据")
            return

        self.info_label.setText(f"发现 {len(self.wifi_list_data)} 个网络，请点击下方选择")
        for i, name in enumerate(self.wifi_list_data, 1):
            self.wifi_list.addItem(f"{i}. {name}")

    def confirm_selection(self):
        """确认选择"""
        selected_item = self.wifi_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "警告", "请先选择一个WiFi网络")
            return

        # 提取WiFi名称（去掉前面的序号）
        wifi_name = selected_item.text().split('. ', 1)[1]
        self.parent_ui.lineEdit_wifi_name.setText(wifi_name)

        # 先删除 overlay，再 accept()
        if hasattr(self, 'overlay'):
            self.overlay.deleteLater()
        self.accept()  # 关闭对话框并返回 Accepted

    def setup_background_blur(self):
        """设置背景虚化效果"""
        # 创建半透明覆盖层
        self.overlay = QWidget(self.parent_ui)
        self.overlay.setStyleSheet("background: rgba(0, 0, 0, 0.5);")
        self.overlay.setGeometry(self.parent_ui.rect())
        self.overlay.show()

        # 动画效果
        self.animation = QPropertyAnimation(self.overlay, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def closeEvent(self, event):
        if hasattr(self, 'overlay'):
            self.overlay.deleteLater()
        super().closeEvent(event)


class LoginUI(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        self.setupUi(self)
        self.setObjectName("LoginUI")
        self.resize(resize_data[0], resize_data[1])
        self.setup_style()

        self.label.setPixmap(QPixmap("img/login.png").scaled(770, 1080))
        self.label.setScaledContents(True)

        # 设置控件属性
        self.lineEdit_user.setPlaceholderText("请输入账号名称")
        self.lineEdit_pwd.setPlaceholderText("请输入账号密码")
        self.lineEdit_pwd.setEchoMode(QLineEdit.Password)
        self.checkBox.setChecked(True)

        # 设置按钮输入
        self.pushButton_user.clicked.connect(
            lambda: self.show_rename_dialog(self.lineEdit_user))
        self.pushButton_pwd.clicked.connect(
            lambda: self.show_rename_dialog(self.lineEdit_pwd))

        self.gridLayout.addWidget(self.label_user, 0, 0, 1, 1, alignment=Qt.AlignVCenter)
        self.gridLayout.addWidget(self.lineEdit_user, 0, 1, 1, 1, alignment=Qt.AlignVCenter)
        self.gridLayout.addWidget(self.pushButton_user, 0, 2, 1, 1, alignment=Qt.AlignVCenter)
        self.gridLayout.addWidget(self.label_pwd, 1, 0, 1, 1, alignment=Qt.AlignVCenter)
        self.gridLayout.addWidget(self.lineEdit_pwd, 1, 1, 1, 1, alignment=Qt.AlignVCenter)
        self.gridLayout.addWidget(self.pushButton_pwd, 1, 2, 1, 1, alignment=Qt.AlignVCenter)


    def show_rename_dialog(self, edit_widget):
        # 保存当前正在编辑的控件引用
        self.current_edit_widget = edit_widget

        # 获取当前控件的文本作为初始值
        initial_text = edit_widget.text()

        # 创建并显示对话框
        dialog = RenameDialog(initial_text, self)
        dialog.rename_accepted.connect(self.update_edit_widget)
        dialog.exec_()

    @pyqtSlot(str)
    def update_edit_widget(self, new_text):
        if self.current_edit_widget is not None:
            if isinstance(self.current_edit_widget, (QLineEdit, QLabel)):
                self.current_edit_widget.setText(new_text)
            self.current_edit_widget = None  # 重置当前编辑控件


    def setup_style(self):
        # 调整后的样式设置
        self.setStyleSheet("""
            QWidget#LoginUI,
            QWidget#LoginUI #groupBox_2{
                background-color: white;
            }

            QWidget#LoginUI #groupBox_2 * {
                font: 26px "黑体";
            }
            
            QLabel#label_user,
            QLabel#label_pwd {
                min-width: 90px;
                max-width: 90px;
            }
            QWidget#LoginUI QLineEdit {
                border: 1px solid #dcdfe6;
                border-radius: 10px;
                padding: 25px;
                min-height: 30px;
                max-height: 30px;
            }
            QWidget#LoginUI QLineEdit#lineEdit_pwd {
                font-size: 20px;
            }
            QPushButton#pushButton_user, 
            QPushButton#pushButton_pwd {
                border: none;
                background-color: #409EFF;
                color: white;
                border-radius: 10px;
                margin-left: 50px;
                padding: 20px 0;
                min-width: 120px;
                min-height: 45px;
                max-height: 45px;
                
            }
            
            QPushButton#pushButton_forget {
                max-width: 80px;
                background-color: red;
            }
            
            QPushButton#pushButton_login {
                border: none;
                background-color: #409EFF;
                color: white;
                border-radius: 4px;
                margin-top: 120px;
                padding: 20px 0;
            }
            QPushButton#pushButton_login:hover,
            QPushButton#pushButton_user:hover,
            QPushButton#pushButton_pwd:hover
             {
                background-color: #66B1FF;
            }
            QPushButton#pushButton_forget {
                text-align: right;
                color: #409EFF;
                border: none;
                padding: 0;
            }
            QPushButton#pushButton_forge:hover {
                background-color: #66B1FF;
            }
            QCheckBox {
                color: #606266;
            }
            QCheckBox:checked {
                color: #409eff;
                }
        """)

    # 窗口居中显示
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class SettingUI(QWidget, Setting_Ui_Form, BaseWindow):
    serial_status_changed = pyqtSignal(bool, str)  # True=已连接, False=已断开

    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        self.setupUi(self)
        self.setObjectName("SettingUI")
        self.resize(resize_data[0], resize_data[1])
        self.setup_style()
        self.background = QPixmap("img/setting.png")
        self.lineEdit_wifi_name.setPlaceholderText("点击上方按钮搜索")

        # 存储当前正在编辑的控件引用
        self.current_edit_widget = None

        # 设置按钮连接
        self.pushButton_input_wifipwd.clicked.connect(
            lambda: self.show_rename_dialog(self.lineEdit_wifi_pwd))
        self.pushButton_input_did.clicked.connect(
            lambda: self.show_rename_dialog(self.lineEdit_did))
        self.pushButton_input_ip.clicked.connect(
            lambda: self.show_rename_dialog(self.lineEdit_ip))
        self.pushButton_input_port.clicked.connect(
            lambda: self.show_rename_dialog(self.lineEdit_port))


        # 新增配置初始化
        self.settings = QSettings("MyApp", "WiFiConfig")
        self.load_wifi_config()
        # 串口相关初始化
        self.serial_manager = None
        self.is_serial_connected = False
        self.check_linux_permissions()
        self.main_window = None

        #连接按钮点击事件
        self.pushButton_wifi_find.clicked.connect(self.show_wifi_selection_dialog)
        self.pushButton_connect_wifi.clicked.connect(self.connect_to_wifi)
        self.pushButton_server.clicked.connect(self.connect_to_server)
        self.pushButton_refresh.clicked.connect(self.refresh_serial_ports)
        self.pushButton_stm.clicked.connect(self.connect_serial)
        QTimer.singleShot(100, self.refresh_serial_ports)

    def setup_layout(self):
        for groupbox in [
            self.groupBox_wifi,
            self.groupBox_server,
            self.groupBox_interface
        ]:
            groupbox.setSizePolicy(
                QSizePolicy.Preferred,
                QSizePolicy.Preferred
            )

        self.horizontalLayout_3.setStretch(0, 1)
        self.horizontalLayout_3.setStretch(1, 1)
        self.horizontalLayout_3.setStretch(2, 1)

    def setup_style(self):
        uniform_height = "75px"

        self.setStyleSheet(f"""
            #SettingUI QWidget {{
                font: 30px "黑体";
            }}

            SettingUI QGroupBox {{
                border: 2px solid #e2e2e2;
                padding: 0px 15px;
                margin: 0px !important;
                background-color: white;
            }}

            #SettingUI QLabel, SettingUI QLineEdit, SettingUI QPushButton {{
                min-height: {uniform_height};
                max-height: {uniform_height};
            }}

            SettingUI QLabel {{
                font: bold 25px "黑体";
                padding: 0 10px;
                qproperty-alignment: 'AlignVCenter|AlignLeft';
                min-height: 60px;
                max-height: 60px;
                padding-top: 40px;
            }}

            SettingUI QLineEdit {{
                border: 1px solid #DCDFE6;
                border-radius: 4px;
                padding: 0 15px;
                margin: 0;
            }}

            SettingUI QPushButton {{
                border: none;
                background-color: #409EFF;
                color: white;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
                padding: 0 10px;
                margin: 0;
            }}

            SettingUI QPushButton:hover {{
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(64, 158, 255, 0.8),
                    stop:1 rgba(64, 158, 255, 1)
                );
            }}

            #groupBox_interface #label_interface1_2 {{
                padding-bottom: 10px;
            }}

            #comboBox_stm {{
                border: 1px solid #DCDFE6;
                border-radius: 4px;
                padding: 0 15px;
                margin: 0;
                min-height: 70px;
                margin-top: 40px;
            }}
            #comboBox_stm::drop-down {{
                width: 60px;          /* 下拉按钮宽度 */
                border-left: 1px solid #ccc;  /* 左侧分割线 */
            }}
            #comboBox_stm::down-arrow {{
                width: 40px;          /* 箭头图标大小 */
                height: 40px;
            }}
            #comboBox_stm QAbstractItemView {{
                font-size: 25px;
            }}

            #pushButton_stm {{
                background-color: #71b362;
            }}


            /* 特定按钮样式 - 需要单独定义hover */
            #groupBox_interface #pushButton_refresh {{
                min-height: 70px;
                max-height: 70px;
                margin-bottom: 20px;
            }}


            QPushButton#pushButton_quit {{
                margin-top: 60px;
                background-color: #db5860;
            }}
            QPushButton#pushButton_quit:hover {{
                background-color: #db5860;
            }}

            QPushButton#pushButton_wifi_find,
            QPushButton#pushButton_stm{{
                background-color: #71b362;
            }}
            QPushButton#pushButton_wifi_find:hover,
            QPushButton#pushButton_stm:hover{{
                background-color: #85c177;
            }}

            #pushButton_connect_wifi {{
                margin-top: 40px;
            }}

            /* 组框标题样式 */
            #label_wifi_title,
            #label_server_title,
            #label_interface_title {{
                color: #409eff;
                font: bold 30px "黑体";
                min-height: 50px;
                max-height: 50px;
                qproperty-alignment: 'AlignCenter';
            }}
        """)

        for groupbox in [self.groupBox_wifi, self.groupBox_server, self.groupBox_interface]:
            layout = groupbox.layout()
            layout.setSpacing(10)  # 设置元素间间距
            layout.setContentsMargins(15, 15, 15, 15)  # 设置布局边距
        # 获取当前窗口宽度
        window_width = self.width()
        # 计算每个 groupBox 的理想宽度（减去布局边距）
        groupbox_width = int(window_width / 3) - 20  # 20 是边距调整值

        # 设置三个 groupBox 的固定宽度
        self.groupBox_wifi.setFixedWidth(groupbox_width)
        self.groupBox_server.setFixedWidth(groupbox_width)
        self.groupBox_interface.setFixedWidth(groupbox_width)

    def show_wifi_selection_dialog(self):
        try:
            def finish_callback(success, result):
                self.loading_dialog.close()

                if not success:
                    self._show_custom_message("错误", result, QMessageBox.Critical)
                    return

                try:
                    dialog = WifiSelectionDialog(self, wifi_list=result)
                    dialog.exec_()
                except Exception as e:
                    print(f"Error: {str(e)}")

            self._start_loading_task(
                task_func=self.get_wifi_list_async,
                finish_callback=finish_callback
            )

        except Exception as e:
            print(f"Error: {str(e)}")

    def get_wifi_list_async(self):
        system = platform.system()

        if system == "Windows":
            wifi_list, error = self.get_wifi_list_windows()
        elif system == "Linux":
            wifi_list, error = self.get_wifi_list_linux()
        else:
            error = f"Unsupported OS: {system}"
            wifi_list = None

        if error or not wifi_list:
            return (False, error or "未找到可用网络")
        return (True, wifi_list)

    def _get_wifi_list_task(self):
        try:
            dialog = WifiSelectionDialog(self)
            dialog.exec_()
        except BaseException as e:
            print(str(e))

    def _show_wifi_dialog(self, success, result):
        """显示WiFi选择对话框"""
        wifi_list, error = result if success else (None, result)
        dialog = WifiSelectionDialog(self, wifi_list, error)
        dialog.exec_()

    def get_wifi_list_windows(self):
        """Windows系统获取WiFi列表"""
        try:
            # 使用PowerShell命令获取WiFi列表
            command = """
            $Result = netsh wlan show networks | Where-Object { 
                $_ -match '^\s*SSID\s+\d+\s*:\s*(.+)$' 
            }
            $wifiList = @()
            $Result | ForEach-Object { 
                if($_ -match '^\s*SSID\s+\d+\s*:\s*(.+)$') { 
                    $ssid = $Matches[1].Trim()
                    if(-not [string]::IsNullOrEmpty($ssid)) {
                        $wifiList += $ssid
                    }
                }
            }
            $wifiList
            """

            # 跨平台运行命令
            kwargs = {
                'capture_output': True,
                'text': True,
                'encoding': 'utf-8',
                'errors': 'replace',
            }
            
            # 仅在Windows下添加创建无窗口标志
            if platform.system() == 'Windows':
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
                
            result = subprocess.run(
                ['powershell', '-command', command],
                **kwargs
            )

            if result.returncode != 0:
                return None, "无法获取WiFi列表，请确保WiFi已开启"

            # 处理输出
            wifi_list = [line.strip() for line in result.stdout.split('\n') if line.strip()]
            return wifi_list, None

        except Exception as e:
            return None, f"获取WiFi列表时出错: {str(e)}"

    def get_wifi_list_linux(self):
        """Ubuntu系统获取WiFi列表"""
        try:
            # 使用nmcli命令获取WiFi列表
            result = subprocess.run(['nmcli', '-t', '-f', 'SSID', 'dev', 'wifi'],
                                    capture_output=True, text=True)

            if result.returncode != 0:
                return None, "无法获取WiFi列表，请确保WiFi已开启"

            wifi_list = []
            for line in result.stdout.split('\n'):
                wifi_name = line.strip()
                if wifi_name:  # 过滤空行
                    wifi_list.append(wifi_name)
            return wifi_list, None
        except FileNotFoundError:
            return None, "未找到nmcli命令，请确保NetworkManager已安装"
        except Exception as e:
            return None, f"获取WiFi列表时出错: {str(e)}"

    def show_rename_dialog(self, edit_widget):
        # 保存当前正在编辑的控件引用
        self.current_edit_widget = edit_widget

        # 获取当前控件的文本作为初始值
        initial_text = edit_widget.text()

        # 创建并显示对话框
        dialog = RenameDialog(initial_text, self)
        dialog.rename_accepted.connect(self.update_edit_widget)
        dialog.exec_()

    def load_wifi_config(self):
        self.lineEdit_wifi_name.setText(self.settings.value("wifi/name", ""))
        self.lineEdit_wifi_pwd.setText(self.settings.value("wifi/password", ""))

        # 服务器配置
        self.lineEdit_ip.setText(self.settings.value("server/ip", ""))
        self.lineEdit_port.setText(self.settings.value("server/port", ""))
        self.lineEdit_did.setText(self.settings.value("server/did", ""))

    def save_wifi_config(self):
        self.settings.setValue("wifi/name", self.lineEdit_wifi_name.text())
        self.settings.setValue("wifi/password", self.lineEdit_wifi_pwd.text())

        self.settings.sync()  # 强制写入磁盘

        # 调试输出验证保存值
        print(f"[Debug] 保存配置: name={self.lineEdit_wifi_name.text()}, pwd={self.lineEdit_wifi_pwd.text()}")

    def connect_to_wifi(self):
        self._start_loading_task(
            task_func=self._connect_wifi_task,
            finish_callback=self._show_wifi_connect_result,
        )

    def _connect_wifi_task(self):
        try:
            wifi_name = self.lineEdit_wifi_name.text()
            wifi_pwd = self.lineEdit_wifi_pwd.text()

            if not wifi_name or not wifi_pwd:
                self._show_custom_message("连接失败",
                                          f"错误原因：WiFi名称和密码不能为空",
                                          QMessageBox.Critical)
                return

            # 禁用按钮防止重复点击
            self.pushButton_connect_wifi.setEnabled(False)
            self.pushButton_connect_wifi.setText("连接中...")

            # 跨平台连接
            system = platform.system()
            if system == "Windows":
                success, message = self.connect_windows(wifi_name, wifi_pwd)
            elif system == "Linux":
                success, message = self.connect_linux(wifi_name, wifi_pwd)
            else:
                success, message = False, f"不支持的操作系统: {system}"

            self.pushButton_connect_wifi.setEnabled(True)
            self.save_wifi_config()

            return success, message
        except Exception as e:
            return False, f"上传失败: {str(e)}"

    def _show_wifi_connect_result(self, success, message):
        self._show_custom_message(
            "WiFi连接结果",
            message,
            QMessageBox.Information if success else QMessageBox.Critical
        )

    ###### Windows连接方法 ######
    def connect_windows(self, ssid, password):
        try:
            from xml.sax.saxutils import escape

            # 编码特殊字符
            escaped_ssid = escape(ssid)
            escaped_password = escape(password)

            # 生成严格符合规范的XML
            xml_config = f"""<?xml version="1.0" encoding="UTF-8"?>
    <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{escaped_ssid}</name>
    <SSIDConfig>
    <SSID>
    <name>{escaped_ssid}</name>
    </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
    <security>
    <authEncryption>
    <authentication>WPA2PSK</authentication>
    <encryption>AES</encryption>
    <useOneX>false</useOneX>
    </authEncryption>
    <sharedKey>
    <keyType>passPhrase</keyType>
    <protected>false</protected>
    <keyMaterial>{escaped_password}</keyMaterial>
    </sharedKey>
    </security>
    </MSM>
    </WLANProfile>"""

            temp_file = os.path.join(tempfile.gettempdir(), f"{ssid}.xml")

            # 写入UTF-8 with BOM（Windows兼容）
            with open(temp_file, "w", encoding="utf-8-sig") as f:
                f.write(xml_config)

            # 检查管理员权限（仅限Windows）
            if platform.system() == 'Windows':
                try:
                    if not ctypes.windll.shell32.IsUserAnAdmin():
                        return False, "需要管理员权限运行程序"
                except Exception as e:
                    print(f"检查管理员权限时出错: {e}")
                    # 继续执行，不中断

            # 执行命令并捕获完整输出
            commands = [
                f'netsh wlan add profile filename="{temp_file}"',
                f'netsh wlan connect name="{ssid}"'
            ]

            full_output = []
            for cmd in commands:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,  # 合并输出流
                    encoding="gbk",
                    timeout=10  # 防止卡死
                )
                full_output.append(f"[CMD] {cmd}\n{result.stdout}")
                if result.returncode != 0:
                    return False, "\n".join(full_output)

            return True, ""

        except Exception as e:
            return False, f"Windows连接异常：{str(e)}"
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    ###### Linux连接方法 ######
    def connect_linux(self, ssid, password):
        try:
            # 检查是否有NetworkManager或wpa_supplicant命令
            nm_exists = subprocess.run(['which', 'nmcli'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0
            wpa_exists = subprocess.run(['which', 'wpa_cli'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0
            
            if nm_exists:
                # 使用NetworkManager方法
                print("使用NetworkManager连接WiFi")
                result = subprocess.run(
                    ['nmcli', 'device', 'wifi', 'connect', ssid, 'password', password],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                if result.returncode != 0:
                    error = result.stderr or result.stdout
                    return False, f"Linux连接失败(NetworkManager): {error.strip()}"
                return True, "已成功使用NetworkManager连接WiFi"
                
            elif wpa_exists:
                # 使用wpa_supplicant方法
                print("使用wpa_supplicant连接WiFi")
                
                # 生成wpa_supplicant配置
                config = f"""
                network={{
                    ssid="{ssid}"
                    psk="{password}"
                    key_mgmt=WPA-PSK
                }}"""
                
                # 寻找可能的配置文件路径
                conf_paths = [
                    "/etc/wpa_supplicant/wpa_supplicant.conf",
                    "/etc/wpa_supplicant.conf"
                ]
                
                # 寻找可能的无线接口
                interfaces = ["wlan0", "wlp2s0", "wlp3s0", "wlp4s0"]
                interface = None
                
                # 查找活跃的无线接口
                try:
                    result = subprocess.run(['ip', 'link', 'show'], stdout=subprocess.PIPE, text=True)
                    for line in result.stdout.splitlines():
                        for iface in interfaces:
                            if iface in line and "state UP" in line:
                                interface = iface
                                break
                        if interface:
                            break
                except Exception:
                    pass
                
                if not interface:
                    interface = "wlan0"  # 默认接口
                
                # 使用临时文件存储配置
                temp_path = os.path.join(tempfile.gettempdir(), "wpa_supplicant.conf")
                with open(temp_path, 'w') as f:
                    f.write(config)
                
                try:
                    # 尝试连接
                    commands = [
                        f"sudo wpa_supplicant -B -i {interface} -c {temp_path}",
                        f"sudo dhclient {interface}"
                    ]
                    
                    for cmd in commands:
                        result = subprocess.run(
                            cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                        if result.returncode != 0:
                            error = result.stderr or result.stdout
                            return False, f"Linux连接失败(wpa_supplicant): {error.strip()}"
                    
                    return True, "已成功使用wpa_supplicant连接WiFi"
                finally:
                    # 清理临时文件
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            else:
                return False, "Linux系统未找到NetworkManager或wpa_supplicant，无法连接WiFi"

        except Exception as e:
            return False, f"Linux连接异常：{str(e)}"

    def connect_to_server(self):
        self._start_loading_task(
            task_func=self._connect_server_task,
            finish_callback=self._show_server_connect_result,
        )

    def _connect_server_task(self):
        try:
            success, msg = self.validate_server_connection()
            self.save_server_config()
            return True, msg
        except Exception as e:
            return False, f"上传失败: {str(e)}"

    def _show_server_connect_result(self, success, message):
        self._show_custom_message(
            "上传结果",
            message,
            QMessageBox.Information if success else QMessageBox.Critical
        )

    def save_server_config(self):
        self.settings.setValue("server/ip", self.lineEdit_ip.text())
        self.settings.setValue("server/port", self.lineEdit_port.text())
        self.settings.setValue("server/did", self.lineEdit_did.text())

        self.settings.sync()

    def check_linux_permissions(self):
        """检查Linux系统下的串口访问权限"""
        if sys.platform == 'linux':
            test_ports = ["/dev/ttyS0", "/dev/ttyUSB0", "/dev/ttyACM0"]
            for port in test_ports:
                if os.path.exists(port) and not os.access(port, os.R_OK | os.W_OK):
                    self._show_custom_message(
                        "权限警告",
                        f"当前用户无权限访问 {port}\n\n请执行以下命令后重新登录:\nsudo usermod -aG dialout $USER",
                        QMessageBox.Warning
                    )
                    break

    def set_main_window(self, main_window):
        """设置 MainWindow 引用"""
        self.main_window = main_window

    def refresh_serial_ports(self):
        """跨平台获取可用串口"""
        self.comboBox_stm.clear()

        try:
            ports = sorted(serial.tools.list_ports.comports())
            available_ports = []

            for port in ports:
                try:
                    # 尝试快速打开关闭端口验证可用性
                    with serial.Serial(port.device, timeout=0.1) as s:
                        if s.is_open:
                            available_ports.append(port.device)
                except (serial.SerialException, OSError) as e:
                    continue

            if available_ports:
                self.comboBox_stm.addItems(available_ports)
                # 自动选择第一个可用端口
                self.comboBox_stm.setCurrentIndex(0)
            else:
                self.comboBox_stm.addItem("未检测到可用串口")
                self._show_custom_message(
                    "串口检测",
                    "未找到任何可用串口设备\n\n请检查:\n1. 设备是否已连接\n2. 驱动程序是否安装",
                    QMessageBox.Information
                )

        except Exception as e:
            self.comboBox_stm.addItem("检测串口失败")
            self._show_custom_message(
                "检测错误",
                f"扫描串口时发生错误:\n\n{str(e)}",
                QMessageBox.Critical
            )

    def connect_serial(self):
        """连接/断开串口"""
        if self.is_serial_connected:  # 使用状态标志判断
            self._disconnect_serial()
            self.serial_status_changed.emit(False, "")
            print("已断开")
            return

        port = self.comboBox_stm.currentText()
        if not port or port.startswith(("未检测", "检测失败")):
            self._show_custom_message("连接错误", "请先选择有效的串口", QMessageBox.Warning)
            return

        try:
            self.serial_manager = SerialManager(port, 115200)
            if self.serial_manager.open_port():
                self.is_serial_connected = True  # 更新状态标志
                self._set_button_connected_style()
                self.serial_status_changed.emit(True, port)

                if self.main_window:
                    self.main_window.set_serial_manager(self.serial_manager)
        except Exception as e:
            self._show_custom_message("连接失败", f"连接串口失败:\n\n{str(e)}", QMessageBox.Critical)

    def _disconnect_serial(self):
        """断开串口连接"""
        if self.serial_manager:
            self.serial_manager.close_port()  # 确保调用正确的关闭方法
            self.serial_manager = None

        self.is_serial_connected = False  # 更新状态标志
        self._set_button_disconnected_style()
        # self._show_custom_message("已断开", "串口连接已断开", QMessageBox.Information)

    def _set_button_connected_style(self):
        """设置已连接状态样式（红色）"""
        self.pushButton_stm.setText("断开连接")
        self.pushButton_stm.setStyleSheet("""
            QPushButton {
                background-color: #db5860;
            }
            QPushButton:hover {
                background-color: #c04a50;
            }
        """)
        self.pushButton_refresh.setEnabled(False)


    def _set_button_disconnected_style(self):
        """设置断开状态样式（绿色）"""
        self.pushButton_stm.setText("连接串口")
        self.pushButton_stm.setStyleSheet("""
            QPushButton {
                background-color: #71b362;
            }
            QPushButton:hover {
                background-color: #5d9c4f;
            }
        """)
        self.pushButton_refresh.setEnabled(True)

    @pyqtSlot(str)
    def update_edit_widget(self, new_text):
        """
        更新编辑控件的文本
        :param new_text: 新的文本内容
        """
        if self.current_edit_widget is not None:
            if isinstance(self.current_edit_widget, (QLineEdit, QLabel)):
                self.current_edit_widget.setText(new_text)
            self.current_edit_widget = None  # 重置当前编辑控件

    # 窗口居中显示
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class PCRAnalyzer:
    def __init__(self):
        self.base_point_count = 15  # 与C#版本保持一致
        self.threshold = 800.0  # 与C#版本保持一致
        self.channel_colors = ['#FF0000', '#00AA00', '#0000FF', '#FF00FF']
        self.marker_styles = ['o', 's', '^', 'v']

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
        try:
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
                print(f"数据点太少({size}个)，无法进行有效处理")
                return result
                
            # 寻找曲线起始点
            result['positive'], result['curve_start'] = self.find_curve(data, size, 3)
            
            # 计算基线
            base_points = min(self.base_point_count, size // 3)  # 使用数据前1/3或固定点数
            baseline_data = data[:base_points]
            result['baseline'] = np.mean(baseline_data)
            
            # 扣除基线
            data = data - result['baseline']
            
            # 中值滤波
            window_size = min(5, size // 2 * 2 - 1)  # 确保窗口大小为奇数且不超过数据长度一半
            if window_size < 3:
                window_size = 3
            filtered = self.median_filter(data, window_size)
            
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
                for i in range(min(5, size)):
                    scaled_data[i] *= 0.1 * i
                    
                # 寻找CT值
                for i in range(1, len(scaled_data)):
                    if not result['ct_found'] and scaled_data[i-1] < 800.0 and scaled_data[i] >= 800.0:
                        # 线性插值计算CT值
                        slope = scaled_data[i] - scaled_data[i-1]
                        if slope > 0:  # 避免除以0或负值
                            frac = (800.0 - scaled_data[i-1]) / slope
                            ct = (i-1) + frac
                            result['ct_value'] = ct
                            result['ct_found'] = True
                            break
                        
            return result
            
        except Exception as e:
            print(f"PCR数据处理错误: {str(e)}")
            # 出错时返回初始结果
            return {
                'raw': np.array([]),
                'baseline': 0.0,
                'positive': False,
                'ct_value': 0.0,
                'ct_found': False,
                'data_size': 0,
                'curve_start': 15,
                'smoothed': None,
                'trend': None
            }


if __name__ == '__main__':
    app = QApplication(sys.argv)

    MainWindow = MainWindow()
    LoginWidget = LoginUI()
    SettingWidget = SettingUI()

    apply_stylesheet(app, theme='light_blue.xml')

    # 相互设置引用
    MainWindow.set_setting_ui_reference(SettingWidget)
    SettingWidget.set_main_window(MainWindow)


    MainWindow.pushButton_person.clicked.connect(LoginWidget.show)
    MainWindow.pushButton_person.clicked.connect(LoginWidget.raise_)
    MainWindow.pushButton_person.clicked.connect(LoginWidget.center)
    MainWindow.pushButton_person.clicked.connect(MainWindow.hide)

    LoginWidget.pushButton_login.clicked.connect(MainWindow.show)
    LoginWidget.pushButton_login.clicked.connect(MainWindow.raise_)
    LoginWidget.pushButton_login.clicked.connect(MainWindow.center)
    LoginWidget.pushButton_login.clicked.connect(LoginWidget.hide)

    MainWindow.pushButton_setting.clicked.connect(SettingWidget.show)
    MainWindow.pushButton_setting.clicked.connect(SettingWidget.raise_)
    MainWindow.pushButton_setting.clicked.connect(SettingWidget.center)
    MainWindow.pushButton_setting.clicked.connect(MainWindow.hide)

    SettingWidget.pushButton_quit.clicked.connect(MainWindow.show)
    SettingWidget.pushButton_quit.clicked.connect(MainWindow.raise_)
    SettingWidget.pushButton_quit.clicked.connect(MainWindow.center)
    SettingWidget.pushButton_quit.clicked.connect(SettingWidget.hide)

    MainWindow.show()

    sys.exit(app.exec_())