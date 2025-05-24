<script>
	import {
		mapMutations
	} from 'vuex'
	import {
		version
	} from './package.json'
	// #ifdef APP
	import checkUpdate from '@/uni_modules/uni-upgrade-center-app/utils/check-update';
	// #endif

	export default {
		onLaunch: function() {
			// #ifdef H5
			console.log(
				`%c hello uniapp %c v${version} `,
				'background:#35495e ; padding: 1px; border-radius: 3px 0 0 3px;  color: #fff',
				'background:#007aff ;padding: 1px; border-radius: 0 3px 3px 0;  color: #fff; font-weight: bold;'
			)
			// #endif
			// 线上示例使用
			console.log('App Launch');
			
			// 添加请求拦截器
			uni.addInterceptor('request', {
				invoke(args) {
					console.log('请求开始', args)
					// 添加公共请求头
					args.header = {
						...args.header,
						'Content-Type': 'application/json'
					}
					// 添加超时设置
					if (!args.timeout) {
						args.timeout = 15000  // 默认超时时间15秒
					}
					return args
				},
				success(args) {
					console.log('请求成功', args)
					return args
				},
				fail(err) {
					console.error('请求失败', err)
					// 统一处理网络错误
					if (err.errMsg.includes('timeout')) {
						uni.showToast({
							title: '请求超时，请检查网络连接',
							icon: 'none'
						})
					} else if (err.errMsg.includes('abort')) {
						uni.showToast({
							title: '请求被中断',
							icon: 'none'
						})
					} else if (err.errMsg.includes('fail')) {
						uni.showToast({
							title: '网络连接失败，请检查网络设置',
							icon: 'none'
						})
					}
					return err
				},
				complete(res) {
					// console.log('请求完成', res)
					return res
				}
			})
			
			// #ifdef H5 || APP-PLUS
			// 动态添加样式调整底部导航栏图标大小
			setTimeout(() => {
				const style = document.createElement('style');
				style.textContent = '.uni-tabbar-item .uni-tabbar__icon { width: 15px !important; height: 15px !important; }';
				document.head.appendChild(style);
			}, 300);
			// #endif
			
			// #ifdef APP-PLUS
			if (plus.runtime.appid !== 'HBuilder') { // 真机运行不需要检查更新，真机运行时appid固定为'HBuilder'，这是调试基座的appid
				checkUpdate()
			}

			// 一键登录预登陆，可以显著提高登录速度
			uni.preLogin({
				provider: 'univerify',
				success: (res) => {
					// 成功
					this.setUniverifyErrorMsg();
					console.log("preLogin success: ", res);
				},
				fail: (res) => {
					this.setUniverifyLogin(false);
					this.setUniverifyErrorMsg(res.errMsg);
					// 失败
					console.log("preLogin fail res: ", res);
				}
			})
			// #endif
		},
		onShow: function() {
			console.log('App Show')
		},
		onHide: function() {
			console.log('App Hide')
		},
		globalData: {
			test: ''
		},
		methods: {
			...mapMutations(['setUniverifyErrorMsg', 'setUniverifyLogin'])
		}
	}
</script>

<style lang="scss">
	@import '@/uni_modules/uni-scss/index.scss';
	/* #ifndef APP-PLUS-NVUE */
	/* uni.css - 通用组件、模板样式库，可以当作一套ui库应用 */
	@import './common/uni.css';
	@import '@/static/customicons.css';
	/* H5 兼容 pc 所需 */
	/* #ifdef H5 */
	@media screen and (min-width: 768px) {
		body {
			overflow-y: scroll;
		}
	}

	/* 顶栏通栏样式 */
	/* .uni-top-window {
	    left: 0;
	    right: 0;
	} */

	uni-page-body {
		background-color: #F5F5F5 !important;
		min-height: 100% !important;
		height: auto !important;
	}

	.uni-top-window uni-tabbar .uni-tabbar {
		background-color: #fff !important;
	}

	.uni-app--showleftwindow .hideOnPc {
		display: none !important;
	}
	
	/* 自定义底部导航栏图标大小 */
	.uni-tabbar-item .uni-tabbar__icon {
		width: 15px !important;
		height: 15px !important;
	}

	/* #endif */

	/* 以下样式用于 hello uni-app 演示所需 */
	page {
		background-color: #efeff4;
		height: 100%;
		font-size: 28rpx;
		/* line-height: 1.8; */
	}

	.fix-pc-padding {
		padding: 0 50px;
	}

	.uni-header-logo {
		padding: 30rpx;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		margin-top: 10rpx;
	}

	.uni-header-image {
		width: 100px;
		height: 100px;
	}

	.uni-hello-text {
		color: #7A7E83;
	}

	.uni-hello-addfile {
		text-align: center;
		line-height: 300rpx;
		background: #FFF;
		padding: 50rpx;
		margin-top: 10px;
		font-size: 38rpx;
		color: #808080;
	}
	/* #endif */
</style>
