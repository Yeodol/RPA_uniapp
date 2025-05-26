"use weex:vue";

if (typeof Promise !== 'undefined' && !Promise.prototype.finally) {
  Promise.prototype.finally = function(callback) {
    const promise = this.constructor
    return this.then(
      value => promise.resolve(callback()).then(() => value),
      reason => promise.resolve(callback()).then(() => {
        throw reason
      })
    )
  }
};

if (typeof uni !== 'undefined' && uni && uni.requireGlobal) {
  const global = uni.requireGlobal()
  ArrayBuffer = global.ArrayBuffer
  Int8Array = global.Int8Array
  Uint8Array = global.Uint8Array
  Uint8ClampedArray = global.Uint8ClampedArray
  Int16Array = global.Int16Array
  Uint16Array = global.Uint16Array
  Int32Array = global.Int32Array
  Uint32Array = global.Uint32Array
  Float32Array = global.Float32Array
  Float64Array = global.Float64Array
  BigInt64Array = global.BigInt64Array
  BigUint64Array = global.BigUint64Array
};


(()=>{var x=Object.create;var c=Object.defineProperty;var f=Object.getOwnPropertyDescriptor;var b=Object.getOwnPropertyNames;var _=Object.getPrototypeOf,v=Object.prototype.hasOwnProperty;var h=(o,t)=>()=>(t||o((t={exports:{}}).exports,t),t.exports);var w=(o,t,n,a)=>{if(t&&typeof t=="object"||typeof t=="function")for(let r of b(t))!v.call(o,r)&&r!==n&&c(o,r,{get:()=>t[r],enumerable:!(a=f(t,r))||a.enumerable});return o};var y=(o,t,n)=>(n=o!=null?x(_(o)):{},w(t||!o||!o.__esModule?c(n,"default",{value:o,enumerable:!0}):n,o));var d=h((R,u)=>{u.exports=Vue});var e=y(d());var g=(o,t)=>{let n=o.__vccOpts||o;for(let[a,r]of t)n[a]=r;return n};var B="/static/templateIndex.png",T={"uni-container":{"":{paddingTop:"20rpx",paddingRight:"20rpx",paddingBottom:"20rpx",paddingLeft:"20rpx"}},"uni-header-logo":{"":{paddingTop:"30rpx",paddingRight:"30rpx",paddingBottom:"30rpx",paddingLeft:"30rpx",display:"flex",flexDirection:"column",alignItems:"center",marginBottom:"30rpx"}},"uni-header-image":{"":{width:"200rpx",height:"200rpx"}},"menu-list":{"":{backgroundColor:"#ffffff",borderRadius:"12rpx",overflow:"hidden"}},"menu-item":{"":{display:"flex",flexDirection:"row",alignItems:"center",paddingTop:"30rpx",paddingRight:"30rpx",paddingBottom:"30rpx",paddingLeft:"30rpx",borderBottomWidth:"1rpx",borderBottomStyle:"solid",borderBottomColor:"#eeeeee","borderBottomWidth:last-child":0,"borderBottomColor:last-child":"#000000"}},"menu-text":{"":{flex:1,fontSize:"32rpx",color:"#333333"}},"menu-icon":{"":{fontFamily:"uniicons",fontSize:"32rpx",color:"#bbbbbb"}},"logout-section":{"":{marginTop:"60rpx",paddingTop:0,paddingRight:"30rpx",paddingBottom:0,paddingLeft:"30rpx"}},"logout-btn":{"":{backgroundColor:"#ff3b30",color:"#ffffff",borderRadius:"44rpx",height:"88rpx",lineHeight:"88rpx"}}},C={data(){return{}},methods:{navigateTo(o){uni.navigateTo({url:o})},logout(){uni.showModal({title:"\u63D0\u793A",content:"\u786E\u5B9A\u8981\u9000\u51FA\u767B\u5F55\u5417\uFF1F",success:o=>{o.confirm&&(uni.clearStorage(),uni.reLaunch({url:"/pages/login/login"}))}})}}};function k(o,t,n,a,r,i){let m=(0,e.resolveComponent)("button");return(0,e.openBlock)(),(0,e.createElementBlock)("scroll-view",{scrollY:!0,showScrollbar:!0,enableBackToTop:!0,bubble:"true",style:{flexDirection:"column"}},[(0,e.createElementVNode)("view",{class:"uni-container"},[(0,e.createElementVNode)("view",{class:"uni-header-logo"},[(0,e.createElementVNode)("u-image",{class:"uni-header-image",src:B})]),(0,e.createElementVNode)("view",{class:"menu-list"},[(0,e.createElementVNode)("view",{class:"menu-item",onClick:t[0]||(t[0]=p=>i.navigateTo("/pages/template/company/company"))},[(0,e.createElementVNode)("u-text",{class:"menu-text"},"\u516C\u53F8\u7B80\u4ECB"),(0,e.createElementVNode)("u-text",{class:"menu-icon"},"\uE470")]),(0,e.createElementVNode)("view",{class:"menu-item",onClick:t[1]||(t[1]=p=>i.navigateTo("/pages/template/database/database"))},[(0,e.createElementVNode)("u-text",{class:"menu-text"},"\u6570\u636E\u5E93\u8BBE\u7F6E"),(0,e.createElementVNode)("u-text",{class:"menu-icon"},"\uE470")]),(0,e.createElementVNode)("view",{class:"menu-item",onClick:t[2]||(t[2]=p=>i.navigateTo("/pages/template/account/account"))},[(0,e.createElementVNode)("u-text",{class:"menu-text"},"\u8D26\u53F7\u8BBE\u7F6E"),(0,e.createElementVNode)("u-text",{class:"menu-icon"},"\uE470")])]),(0,e.createElementVNode)("view",{class:"logout-section"},[(0,e.createVNode)(m,{class:"logout-btn",onClick:i.logout},{default:(0,e.withCtx)(()=>[(0,e.createTextVNode)("\u9000\u51FA\u767B\u5F55")]),_:1},8,["onClick"])])])])}var l=g(C,[["render",k],["styles",[T]]]);var s=plus.webview.currentWebview();if(s){let o=parseInt(s.id),t="pages/tabBar/template/template",n={};try{n=JSON.parse(s.__query__)}catch(r){}l.mpType="page";let a=Vue.createPageApp(l,{$store:getApp({allowDefault:!0}).$store,__pageId:o,__pagePath:t,__pageQuery:n});a.provide("__globalStyles",Vue.useCssStyles([...__uniConfig.styles,...l.styles||[]])),a.mount("#root")}})();
