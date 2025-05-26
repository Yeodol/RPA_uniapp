import os
import sys
import io
import base64
import datetime
from fpdf import FPDF
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from flask import send_file

class PCRReportGenerator:
    def __init__(self, reports_folder=None):
        # 设置报告保存目录
        self.reports_folder = reports_folder or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'RPA', 'data', 'reports')
        
        # 确保目录存在
        if not os.path.exists(self.reports_folder):
            os.makedirs(self.reports_folder)
            print(f"创建报告目录: {self.reports_folder}")
            
        # 报告模板信息
        self.template = {
            'company': '青岛英赛特生物科技有限公司',
            'title': 'PCR 检测',
            'work_time': '9：00-18：00',
            'address': '',
            'contact': '',
            'email': 'E-Mail: '
        }
        
        # 图表颜色映射
        self.channel_colors = {
            'FAM': '#FF0000',
            'VIC': '#00AA00'
        }
    
    def create_report(self, data):
        """创建PCR检测报告"""
        try:
            # 准备数据
            filename = data.get('filename', '未知文件')
            pdfname = data.get('pdfname', filename.replace('.txt', '.pdf'))
            results = data.get('results', [])
            chart_data = data.get('chart_data', [])
            
            # 创建PDF对象
            pdf = FPDF()
            pdf.add_page()
            
            # 设置中文字体
            pdf.add_font('simhei', '', 'C:\\Windows\\Fonts\\simhei.ttf', uni=True)
            pdf.set_font('simhei', '', 12)
            
            # 添加页眉
            self._add_header(pdf)
            
            # 添加样本信息部分
            self._add_sample_info(pdf, filename)
            
            # 添加图表部分标题
            pdf.ln(5)
            pdf.set_font('simhei', '', 14)
            pdf.ln(5)
            
            # 为每个通道生成图表
            if chart_data:
                chart_images = self._generate_chart_images(chart_data)
                self._add_charts_to_pdf(pdf, chart_images)
            
            # 添加结果表格
            pdf.ln(5)
            pdf.set_font('simhei', '', 14)
            pdf.ln(5)
            
            # 添加结果表格
            self._add_results_table(pdf, results)
            
            # 添加页脚
            pdf.ln(10)
            pdf.set_font('simhei', '', 12)
            pdf.cell(0, 10, '本次实验结果，只对当前样本负责！', 0, 1, 'C')
            
            # 保存PDF文件
            report_path = os.path.join(self.reports_folder, pdfname)
            pdf.output(report_path)
            
            print(f"报告生成成功: {report_path}")
            return {
                'success': True,
                'filename': pdfname,
                'path': report_path
            }
            
        except Exception as e:
            print(f"生成报告时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
    
    def _add_header(self, pdf):
        """添加报告页眉"""
        # 添加公司名称
        pdf.set_font('simhei', '', 16)
        pdf.cell(0, 10, self.template['company'], 0, 1, 'C')
        
        # 添加标题
        pdf.set_font('simhei', '', 14)
        pdf.cell(0, 10, self.template['title'], 0, 1, 'C')
        
        # 添加工作时间和地址
        pdf.set_font('simhei', '', 10)
        pdf.cell(90, 8, f"工作时间：{self.template['work_time']}", 0, 0, 'L')
        pdf.cell(90, 8, f"公司地址：{self.template['address']}", 0, 1, 'L')
        
        # 添加联系方式和邮箱
        pdf.cell(90, 8, f"联系方式：{self.template['contact']}", 0, 0, 'L')
        pdf.cell(90, 8, f"{self.template['email']}", 0, 1, 'L')
        
        # 添加分隔线
        pdf.ln(2)
        pdf.cell(0, 0, '', 'T', 1)
    
    def _add_sample_info(self, pdf, filename):
        """添加样本信息"""
        pdf.ln(5)
        pdf.set_font('simhei', '', 10)
        
        # 准备当前日期
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        
        # 文件名去掉.txt后缀
        sample_name = filename.replace('.txt', '')
        
        pdf.cell(0, 8, f'※ 实验时间：{current_date}', 0, 1, 'L')
        pdf.cell(0, 8, '※ 样本类型：', 0, 1, 'L')
        pdf.cell(0, 8, '※ 检测项目：', 0, 1, 'L')
    
    def _generate_chart_images(self, chart_data):
        """为每个通道生成图表图像"""
        images = []
        
        # 按通道分组和类型排序
        channels = sorted(set([item['channel'] for item in chart_data]))
        
        # 创建4个图表对（每个通道一对FAM和VIC）
        for channel in channels:
            # 获取当前通道的FAM和VIC数据
            fam_data = next((item for item in chart_data if item['channel'] == channel and item['type'] == 'FAM'), None)
            vic_data = next((item for item in chart_data if item['channel'] == channel and item['type'] == 'VIC'), None)
            
            # 生成对应的图片
            if fam_data:
                fam_img = self._create_chart_image(fam_data, f"Channel {channel} - FAM", '#FF0000')
                images.append({'channel': channel, 'type': 'FAM', 'image': fam_img})
            
            if vic_data:
                vic_img = self._create_chart_image(vic_data, f"Channel {channel} - VIC", '#00AA00')
                images.append({'channel': channel, 'type': 'VIC', 'image': vic_img})
        
        # 按通道和类型排序，以便正确的排列
        images.sort(key=lambda x: (x['channel'], 0 if x['type'] == 'FAM' else 1))
        
        return images
    
    def _create_chart_image(self, data, title, color):
        """创建单个图表图像，参考pcr_analyzer.py中的Smoothed Trend处理方式"""
        plt.figure(figsize=(8, 5), dpi=100)
        
        # 设置背景颜色和去除边框
        ax = plt.gca()
        ax.set_facecolor('#f8f9fa')
        
        # 删除所有边框
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        # 绘制网格线
        plt.grid(True, linestyle='--', alpha=0.3, color='#cccccc')
        
        # 获取数据
        raw_data = data.get('raw_data', [])
        baseline = data.get('baseline', 0)
        
        # 优先使用smoothed_data，如果不存在则使用trend_data
        smoothed_data = data.get('smoothed_data', [])
        trend_data = data.get('trend_data', []) if not smoothed_data else smoothed_data
        
        threshold = data.get('threshold', 800.0)
        ct_value = data.get('ct_value')
        positive = data.get('positive', False)
        
        if not raw_data or not trend_data:
            plt.text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=14)
        else:
            # 创建X轴数据
            cycles = np.arange(len(trend_data))
            
            # 绘制平滑处理后的趋势线
            plt.plot(cycles, trend_data, 
                     color=color, 
                     linewidth=2.5,
                     zorder=3)
            
            # 添加阈值线 - 与pcr_analyzer.py一致
            plt.axhline(y=threshold, color='gray', linestyle=':', alpha=0.5)
            plt.text(cycles[-1], threshold, 'threshold', ha='right', va='bottom', color='gray', fontsize=9)
            
            # 如果有CT值且为阳性，显示标记 - 与pcr_analyzer.py一致
            if positive and ct_value is not None:
                # 添加垂直CT线
                plt.axvline(x=ct_value, color='red', linestyle='--', alpha=0.7)
                # 添加CT值文本
                plt.text(ct_value, threshold, 
                         f"CT={ct_value:.1f}", 
                         color='red', 
                         ha='center')
        
        # 设置标题和标签 - 与pcr_analyzer.py一致
        plt.title(title, fontsize=14, pad=10)
        plt.xlabel('Cycle', fontsize=11)
        plt.ylabel('dRn', fontsize=11)
        
        # 设置刻度样式
        plt.tick_params(axis='both', which='both', length=0)
        
        # 使用整数刻度 - 与pcr_analyzer.py一致
        from matplotlib.ticker import MaxNLocator
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        
        # Y轴设置 - 完全参考pcr_analyzer.py中第三列
        # 注意：在pcr_analyzer.py中，没有特别设置Y轴范围，这里我们也不设置
        # 这样matplotlib会自动根据数据范围调整Y轴
        
        # 调整图形布局，确保所有元素可见
        plt.tight_layout()
        
        # 保存图像到内存
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', pad_inches=0.1, transparent=False)
        img_buffer.seek(0)
        
        # 关闭图表
        plt.close()
        
        return img_buffer
    
    def _add_charts_to_pdf(self, pdf, chart_images):
        """将图表添加到PDF中，按2x4布局排列（左FAM右VIC）"""
        # 设置固定宽度和间距
        chart_width = 90  # mm
        chart_height = 65  # 大致的图表高度，实际会根据图表比例调整
        margin = 10  # 图表之间的垂直间距
        
        # 提取图表信息
        types = [img_info['type'] for img_info in chart_images]
        channels = [img_info['channel'] for img_info in chart_images]
        images = [img_info['image'] for img_info in chart_images]
        
        # 找出所有唯一的通道号
        unique_channels = sorted(set(channels))
        
        # 对于每个通道绘制一行（包含FAM和VIC）
        for i, channel in enumerate(unique_channels):
            # 确定该通道的FAM和VIC图像索引
            fam_index = None
            vic_index = None
            
            for j, (ch, ty) in enumerate(zip(channels, types)):
                if ch == channel:
                    if ty == 'FAM':
                        fam_index = j
                    elif ty == 'VIC':
                        vic_index = j
            
            # 在新的一行开始前添加适当的间距
            if i > 0:
                pdf.ln(margin)  # 行间距
            
            # 记录当前行的起始Y位置
            row_start_y = pdf.get_y()
            
            # 临时保存左右两个图表
            temp_left_path = None
            temp_right_path = None
            
            # 准备FAM图像（左侧）
            if fam_index is not None:
                fam_img_buffer = images[fam_index]
                temp_left_path = os.path.join(self.reports_folder, f"temp_chart_fam_{channel}.png")
                
                # 转换为PIL图像并保存
                pil_img = Image.open(fam_img_buffer)
                pil_img.save(temp_left_path)
            
            # 准备VIC图像（右侧）
            if vic_index is not None:
                vic_img_buffer = images[vic_index]
                temp_right_path = os.path.join(self.reports_folder, f"temp_chart_vic_{channel}.png")
                
                # 转换为PIL图像并保存
                pil_img = Image.open(vic_img_buffer)
                pil_img.save(temp_right_path)
            
            # 设置标题的字体和样式
            pdf.set_font('simhei', '', 12)
            
            # 绘制通道标题
            pdf.cell(0, 8, f'Channel {channel}', 0, 1, 'C')
            
            # 更新当前行的起始Y位置（标题后）
            row_start_y = pdf.get_y()
            
            # 现在一起添加左右两个图表（如果存在），确保它们的Y坐标相同
            if temp_left_path:
                # 添加FAM图像
                pdf.image(temp_left_path, x=10, y=row_start_y, w=chart_width)
                
                # 删除临时文件
                os.remove(temp_left_path)
            
            if temp_right_path:
                # 添加VIC图像在同一行的右侧
                pdf.image(temp_right_path, x=110, y=row_start_y, w=chart_width)
                
                # 删除临时文件
                os.remove(temp_right_path)
            
            # 计算实际图表高度并移动到图表下方
            pdf.set_y(row_start_y + chart_height)
            
            # 绘制FAM和VIC的小标签
            pdf.set_font('simhei', '', 10)
            pdf.set_text_color(255, 0, 0)  # FAM红色
            pdf.set_xy(50, pdf.get_y())
            pdf.cell(20, 6, 'FAM', 0, 0, 'C')
            
            pdf.set_text_color(0, 170, 0)  # VIC绿色
            pdf.set_xy(150, pdf.get_y())
            pdf.cell(20, 6, 'VIC', 0, 1, 'C')
            
            # 重置文本颜色
            pdf.set_text_color(0, 0, 0)
        
        # 确保在所有图表绘制后有足够的垂直空间
        pdf.ln(5)
    
    def _add_results_table(self, pdf, results):
        """添加结果表格"""
        # 设置表格样式
        pdf.set_font('simhei', '', 12)
        
        # 表格头部
        col_width = 47
        row_height = 10
        
        # 添加表格头部
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(col_width, row_height, '通道', 1, 0, 'C', True)
        pdf.cell(col_width, row_height, '类型', 1, 0, 'C', True)
        pdf.cell(col_width, row_height, '结果', 1, 0, 'C', True)
        pdf.cell(col_width, row_height, 'CT值', 1, 1, 'C', True)
        
        # 添加表格内容
        pdf.set_fill_color(255, 255, 255)
        
        for result in results:
            channel = result.get('channel', '')
            type_name = result.get('type', '')
            positive = result.get('positive', False)
            ct_value = result.get('ct_value')
            
            result_text = '阳性' if positive else '阴性'
            ct_text = f"{ct_value:.1f}" if ct_value is not None else '-'
            
            pdf.cell(col_width, row_height, str(channel), 1, 0, 'C')
            pdf.cell(col_width, row_height, type_name, 1, 0, 'C')
            
            # 设置结果单元格颜色 - 阳性红色，阴性绿色
            if positive:
                pdf.set_text_color(255, 0, 0)  # 红色
            else:
                pdf.set_text_color(0, 170, 0)  # 绿色
                
            pdf.cell(col_width, row_height, result_text, 1, 0, 'C')
            
            # 重置文本颜色
            pdf.set_text_color(0, 0, 0)  # 黑色
            pdf.cell(col_width, row_height, ct_text, 1, 1, 'C')
    
    def check_report_exists(self, filename):
        """检查报告是否已存在"""
        report_path = os.path.join(self.reports_folder, filename)
        return os.path.exists(report_path)
    
    def get_report_list(self):
        """获取所有报告列表"""
        # 确保目录存在
        if not os.path.exists(self.reports_folder):
            return []
        
        # 获取所有PDF文件
        report_files = [f for f in os.listdir(self.reports_folder) if f.lower().endswith('.pdf')]
        
        # 为每个文件获取创建时间
        reports = []
        for filename in report_files:
            try:
                file_path = os.path.join(self.reports_folder, filename)
                creation_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
                
                reports.append({
                    'report_name': filename,
                    'report_time': creation_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'file_size': os.path.getsize(file_path)
                })
            except Exception as e:
                print(f"获取报告信息失败: {filename}, 错误: {str(e)}")
        
        # 按创建时间排序
        reports.sort(key=lambda x: x['report_time'], reverse=True)
        
        return reports
    
    def delete_report(self, filename):
        """删除报告"""
        try:
            report_path = os.path.join(self.reports_folder, filename)
            
            if not os.path.exists(report_path):
                return {'success': False, 'error': '报告文件不存在'}
                
            os.remove(report_path)
            return {'success': True, 'message': f'报告 {filename} 已成功删除'}
            
        except Exception as e:
            print(f"删除报告出错: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_report_file(self, filename):
        """获取报告文件"""
        try:
            report_path = os.path.join(self.reports_folder, filename)
            
            if not os.path.exists(report_path):
                return None
                
            return report_path
            
        except Exception as e:
            print(f"获取报告文件出错: {str(e)}")
            return None 