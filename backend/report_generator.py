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
            pdf.cell(0, 10, '***  qPCR/RPA 检测荧光图  ***', 0, 1, 'C')
            pdf.ln(5)
            
            # 为每个通道生成图表
            if chart_data:
                chart_images = self._generate_chart_images(chart_data)
                self._add_charts_to_pdf(pdf, chart_images)
            
            # 添加结果表格
            pdf.ln(5)
            pdf.set_font('simhei', '', 14)
            pdf.cell(0, 10, '***  报告结果  ***', 0, 1, 'C')
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
        
        pdf.cell(0, 8, '※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※', 0, 1, 'C')
        pdf.cell(0, 8, f'※ 实验对象：{sample_name}', 0, 1, 'L')
        pdf.cell(0, 8, f'※ 实验时间：{current_date}', 0, 1, 'L')
        pdf.cell(0, 8, '※ 样本类型：', 0, 1, 'L')
        pdf.cell(0, 8, '※ 检测项目：', 0, 1, 'L')
        pdf.cell(0, 8, '※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※', 0, 1, 'C')
    
    def _generate_chart_images(self, chart_data):
        """为每个通道生成图表图像"""
        images = []
        
        # 按通道分组
        channels = set([item['channel'] for item in chart_data])
        
        for channel in sorted(channels):
            # 获取当前通道的FAM和VIC数据
            fam_data = next((item for item in chart_data if item['channel'] == channel and item['type'] == 'FAM'), None)
            vic_data = next((item for item in chart_data if item['channel'] == channel and item['type'] == 'VIC'), None)
            
            # 创建通道图表
            if fam_data:
                fam_img = self._create_chart_image(fam_data, f"通道{channel} - FAM", '#FF0000')
                images.append(fam_img)
            
            if vic_data:
                vic_img = self._create_chart_image(vic_data, f"通道{channel} - VIC", '#00AA00')
                images.append(vic_img)
        
        return images
    
    def _create_chart_image(self, data, title, color):
        """创建单个图表图像"""
        plt.figure(figsize=(8, 5), dpi=100)
        
        # 设置背景颜色和去除边框
        ax = plt.gca()
        ax.set_facecolor('#f8f9fa')
        
        # 删除所有边框
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        # 绘制网格线
        plt.grid(True, linestyle='--', alpha=0.2, color='#cccccc')
        
        # 获取数据
        raw_data = data.get('raw_data', [])
        trend_data = data.get('trend_data', [])
        threshold = data.get('threshold', 800.0)
        ct_value = data.get('ct_value')
        
        if not raw_data:
            plt.text(0.5, 0.5, '无数据', ha='center', va='center', fontsize=14)
        else:
            # 绘制数据点
            x = range(1, len(raw_data) + 1)
            
            # 绘制原始数据点（半透明）
            plt.plot(x, raw_data, color=color, alpha=0.2, linewidth=1, label='原始数据')
            
            # 绘制趋势线
            if trend_data:
                plt.plot(range(1, len(trend_data) + 1), trend_data, color=color, linewidth=2.5, label='趋势', zorder=3)
                
                # 添加阈值线
                plt.axhline(y=threshold, color='#888888', linestyle='--', alpha=0.7, zorder=2)
                plt.text(len(trend_data)*0.95, threshold+30, f'阈值={threshold}', ha='right', fontsize=10, color='#666666')
                
                # 如果有CT值，显示标记
                if ct_value is not None:
                    # 添加垂直CT线
                    plt.axvline(x=ct_value, color='#33cc33', linestyle='--', alpha=0.7, zorder=2)
                    # 添加CT点
                    plt.scatter([ct_value], [threshold], color='#33cc33', s=80, zorder=4, edgecolor='white')
                    # 添加CT值文本
                    plt.text(ct_value, threshold+100, f'CT={ct_value:.1f}', ha='center', fontsize=12, color='#009900',
                         bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=3))
        
        # 设置标题和标签
        plt.title(title, fontsize=16, color=color, pad=20, fontweight='bold')
        plt.xlabel('循环次数', fontsize=12)
        plt.ylabel('荧光值', fontsize=12)
        
        # 设置刻度样式
        plt.tick_params(axis='both', which='both', length=0)
        
        # 设置图例
        plt.legend(loc='upper left', fontsize=10, frameon=False)
        
        # 确保Y轴从0开始
        bottom, top = plt.ylim()
        plt.ylim(0, max(top, 1000))
        
        # 保存图像到内存
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', pad_inches=0.1, transparent=False)
        img_buffer.seek(0)
        
        # 关闭图表
        plt.close()
        
        return img_buffer
    
    def _add_charts_to_pdf(self, pdf, chart_images):
        """将图表添加到PDF中"""
        # 每行放两张图
        chart_width = 90  # mm
        charts_per_row = 2
        
        for i, img_buffer in enumerate(chart_images):
            # 每两张图换行
            if i > 0 and i % charts_per_row == 0:
                pdf.ln()
            
            # 计算X位置
            x_pos = (i % charts_per_row) * chart_width
            
            # 将图像缓冲区转换为PIL图像
            image = Image.open(img_buffer)
            
            # 创建临时文件保存图像
            temp_img_path = os.path.join(self.reports_folder, f"temp_chart_{i}.png")
            image.save(temp_img_path)
            
            # 添加图像到PDF
            pdf.image(temp_img_path, x=x_pos, w=chart_width)
            
            # 删除临时文件
            os.remove(temp_img_path)
            
            # 如果是单数，确保添加足够的空间
            if i == len(chart_images) - 1 and (i % charts_per_row) == 0:
                pdf.ln(50)  # 添加空间以模拟两行高度
    
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