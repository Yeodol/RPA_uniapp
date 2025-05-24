<template>
	<view class="container">
		<view class="database-settings">
			<view class="input-item">
				<text class="input-label">IP地址：</text>
				<input class="uni-input" v-model="dbConfig.ip" placeholder="请输入IP地址"/>
			</view>
			<view class="input-item">
				<text class="input-label">端口号：</text>
				<input class="uni-input" v-model="dbConfig.port" placeholder="请输入端口号"/>
			</view>
			<view class="input-item">
				<text class="input-label">数据库账号：</text>
				<input class="uni-input" v-model="dbConfig.username" placeholder="请输入数据库账号"/>
			</view>
			<view class="input-item">
				<text class="input-label">数据库密码：</text>
				<input class="uni-input" type="password" v-model="dbConfig.password" placeholder="请输入数据库密码"/>
			</view>
			<button class="save-btn" @click="saveDbConfig">保存设置</button>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			dbConfig: {
				ip: '',
				port: '',
				username: '',
				password: ''
			}
		}
	},
	methods: {
		saveDbConfig() {
			// 保存数据库配置
			uni.showToast({
				title: '保存成功',
				icon: 'success'
			});
		}
	}
}
</script>

<style lang="scss">
.container {
	padding: 30rpx;
	background-color: #fff;
}

.input-item {
	margin-bottom: 30rpx;
}

.input-label {
	font-size: 28rpx;
	color: #333;
	margin-bottom: 10rpx;
	display: block;
}

.uni-input {
	height: 80rpx;
	border: 1rpx solid #eee;
	border-radius: 8rpx;
	padding: 0 20rpx;
	font-size: 28rpx;
	width: 100%;
	box-sizing: border-box;
}

.save-btn {
	margin-top: 50rpx;
	background-color: #007AFF;
	color: #fff;
	width: 100%;
	height: 88rpx;
	line-height: 88rpx;
	border-radius: 44rpx;
}
</style> 