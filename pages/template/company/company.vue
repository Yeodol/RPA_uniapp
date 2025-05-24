<template>
	<view class="container">
		<view class="company-info">
			<view class="company-title">
				<text>青岛英赛特生物科技有限公司</text>
			</view>
			
			<view class="company-image">
				<image 
					:src="imageUrl" 
					mode="widthFix"
					@error="handleImageError"
					@load="handleImageLoad"
				></image>
			</view>
			
			<view class="company-content">
				<view class="section">
					<text class="section-text">成立于2015年05月25日，注册地位于山东省青岛市即墨区鳌山卫街道办事处梦海二路76号海科研发中心北1楼101室，法定代表人为沈巍。</text>
				</view>
				
				<view class="section">
					<text class="section-title">经营范围：</text>
					<text class="section-text">一般项目：生物基材料技术研发；技术服务、技术开发、技术咨询、技术交流、技术转让、技术推广；第一类医疗器械生产；第一类医疗器械销售；第二类医疗器械销售。（除依法须经批准的项目外，凭营业执照依法自主开展经营活动）</text>
				</view>
				
				<view class="section">
					<text class="section-title">许可项目：</text>
					<text class="section-text">货物进出口；技术进出口；第二类医疗器械生产；第三类医疗器械生产；第三类医疗器械经营。</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			imageUrl: '/static/image/Company.png',
			imageLoadError: false
		}
	},
	methods: {
		handleImageError(e) {
			console.error('图片加载失败:', e);
			this.imageLoadError = true;
		},
		handleImageLoad(e) {
			console.log('图片加载成功');
		}
	}
}
</script>

<style lang="scss">
.container {
	padding: 0;
	background-color: #fff;
}

.company-info {
	padding-top: 20rpx;
	
	.company-title {
		font-size: 40rpx;
		font-weight: bold;
		color: #333;
		text-align: center;
		margin: 30rpx 0;
		padding: 0 30rpx;
	}
	
	.company-image {
		width: 90%;
		margin: 0 auto;
		font-size: 0; // 消除图片底部间隙
		
		image {
			width: 100%;
			display: block; // 去除图片底部间隙
		}
	}
	
	.company-content {
		padding: 30rpx;
		
		.section {
			margin-bottom: 30rpx;
			
			.section-title {
				font-size: 32rpx;
				font-weight: bold;
				color: #333;
				margin-bottom: 16rpx;
				display: block;
			}
			
			.section-text {
				font-size: 28rpx;
				line-height: 1.8;
				color: #666;
			}
		}
	}
}
</style> 