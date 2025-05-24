<template>
	<view class="container">
		<view class="account-list">
			<view class="account-item">
				<text class="item-label">账号名称</text>
				<text class="item-value">{{accountName}}</text>
			</view>
			<view class="account-item">
				<text class="item-label">注册时间</text>
				<text class="item-value">{{registerTime}}</text>
			</view>
			<view class="account-item" @click="goToPassword">
				<text class="item-label">修改密码</text>
				<text class="item-arrow">></text>
			</view>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			accountName: 'admin',
			registerTime: '2024-01-01'
		}
	},
	methods: {
		goToPassword() {
			uni.navigateTo({
				url: '/pages/template/account/password'
			});
		}
	}
}
</script>

<style lang="scss">
.container {
	padding: 20px;
}

.account-list {
	background-color: #FFFFFF;
	border-radius: 10px;
	padding: 0 15px;
}

.account-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	height: 50px;
	border-bottom: 1px solid #EEEEEE;
}

.account-item:last-child {
	border-bottom: none;
}

.item-label {
	font-size: 16px;
	color: #333333;
}

.item-value {
	font-size: 14px;
	color: #666666;
}

.item-arrow {
	font-size: 16px;
	color: #999999;
}
</style> 