<template>
	<view class="container">
		<view class="password-form">
			<view class="input-item">
				<text class="input-label">原密码</text>
				<input class="uni-input" type="password" v-model="passwordForm.oldPassword" placeholder="请输入原密码"/>
			</view>
			<view class="input-item">
				<text class="input-label">新密码</text>
				<input class="uni-input" type="password" v-model="passwordForm.newPassword" placeholder="请输入新密码"/>
			</view>
			<view class="input-item">
				<text class="input-label">确认密码</text>
				<input class="uni-input" type="password" v-model="passwordForm.confirmPassword" placeholder="请再次输入新密码"/>
			</view>
		</view>
		<button class="submit-btn" @click="changePassword">确认修改</button>
	</view>
</template>

<script>
export default {
	data() {
		return {
			passwordForm: {
				oldPassword: '',
				newPassword: '',
				confirmPassword: ''
			}
		}
	},
	methods: {
		changePassword() {
			if (!this.passwordForm.oldPassword || !this.passwordForm.newPassword || !this.passwordForm.confirmPassword) {
				uni.showToast({
					title: '请填写完整信息',
					icon: 'none'
				});
				return;
			}
			
			if (this.passwordForm.newPassword !== this.passwordForm.confirmPassword) {
				uni.showToast({
					title: '两次密码输入不一致',
					icon: 'none'
				});
				return;
			}
			
			// 这里添加修改密码的接口调用
			uni.showLoading({
				title: '提交中...'
			});
			
			setTimeout(() => {
				uni.hideLoading();
				uni.showToast({
					title: '密码修改成功',
					icon: 'success',
					duration: 2000
				});
				
				setTimeout(() => {
					uni.navigateBack();
				}, 2000);
			}, 1500);
		}
	}
}
</script>

<style>
.container {
	padding: 20px;
}

.password-form {
	background-color: #FFFFFF;
	border-radius: 10px;
	padding: 0 15px;
}

.input-item {
	padding: 15px 0;
	border-bottom: 1px solid #EEEEEE;
}

.input-item:last-child {
	border-bottom: none;
}

.input-label {
	font-size: 16px;
	color: #333333;
	margin-bottom: 10px;
	display: block;
}

.uni-input {
	height: 40px;
	font-size: 14px;
	color: #333333;
}

.submit-btn {
	width: 90%;
	height: 44px;
	line-height: 44px;
	background-color: #007AFF;
	color: #FFFFFF;
	border-radius: 22px;
	margin-top: 40px;
}
</style> 