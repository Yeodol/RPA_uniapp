<template>
	<view class="container">
		<view class="version-info">
			<text class="version-title">当前版本</text>
			<text class="version-number">v1.0.0</text>
		</view>
		<button class="check-btn" @click="checkVersion">检查更新</button>
	</view>
</template>

<script>
export default {
	data() {
		return {
			currentVersion: 'v1.0.0'
		}
	},
	methods: {
		checkVersion() {
			uni.showLoading({
				title: '检查中...'
			});
			
			// 模拟检查更新
			setTimeout(() => {
				uni.hideLoading();
				uni.showModal({
					title: '版本信息',
					content: '当前已是最新版本',
					showCancel: false
				});
			}, 1500);
		}
	}
}
</script>

<style>
.container {
	padding: 20px;
}

.version-info {
	display: flex;
	flex-direction: column;
	align-items: center;
	margin: 50px 0;
}

.version-title {
	font-size: 16px;
	color: #666;
	margin-bottom: 10px;
}

.version-number {
	font-size: 24px;
	color: #333;
	font-weight: bold;
}

.check-btn {
	width: 80%;
	height: 44px;
	line-height: 44px;
	background-color: #007AFF;
	color: #FFFFFF;
	border-radius: 5px;
	margin-top: 30px;
}
</style> 