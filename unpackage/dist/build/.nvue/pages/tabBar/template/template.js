import { resolveComponent, openBlock, createElementBlock, createElementVNode, createVNode, withCtx, createTextVNode } from "vue";
import { _ as _export_sfc } from "../../../_plugin-vue_export-helper.js";
const _imports_0 = "/static/templateIndex.png";
const _style_0 = { "uni-container": { "": { "paddingTop": "20rpx", "paddingRight": "20rpx", "paddingBottom": "20rpx", "paddingLeft": "20rpx" } }, "uni-header-logo": { "": { "paddingTop": "30rpx", "paddingRight": "30rpx", "paddingBottom": "30rpx", "paddingLeft": "30rpx", "display": "flex", "flexDirection": "column", "alignItems": "center", "marginBottom": "30rpx" } }, "uni-header-image": { "": { "width": "200rpx", "height": "200rpx" } }, "menu-list": { "": { "backgroundColor": "#ffffff", "borderRadius": "12rpx", "overflow": "hidden" } }, "menu-item": { "": { "display": "flex", "flexDirection": "row", "alignItems": "center", "paddingTop": "30rpx", "paddingRight": "30rpx", "paddingBottom": "30rpx", "paddingLeft": "30rpx", "borderBottomWidth": "1rpx", "borderBottomStyle": "solid", "borderBottomColor": "#eeeeee", "borderBottomWidth:last-child": 0, "borderBottomColor:last-child": "#000000" } }, "menu-text": { "": { "flex": 1, "fontSize": "32rpx", "color": "#333333" } }, "menu-icon": { "": { "fontFamily": "uniicons", "fontSize": "32rpx", "color": "#bbbbbb" } }, "logout-section": { "": { "marginTop": "60rpx", "paddingTop": 0, "paddingRight": "30rpx", "paddingBottom": 0, "paddingLeft": "30rpx" } }, "logout-btn": { "": { "backgroundColor": "#ff3b30", "color": "#ffffff", "borderRadius": "44rpx", "height": "88rpx", "lineHeight": "88rpx" } } };
const _sfc_main = {
  data() {
    return {};
  },
  methods: {
    navigateTo(url) {
      uni.navigateTo({
        url
      });
    },
    logout() {
      uni.showModal({
        title: "提示",
        content: "确定要退出登录吗？",
        success: (res) => {
          if (res.confirm) {
            uni.clearStorage();
            uni.reLaunch({
              url: "/pages/login/login"
            });
          }
        }
      });
    }
  }
};
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  const _component_button = resolveComponent("button");
  return openBlock(), createElementBlock("scroll-view", {
    scrollY: true,
    showScrollbar: true,
    enableBackToTop: true,
    bubble: "true",
    style: { flexDirection: "column" }
  }, [
    createElementVNode("view", { class: "uni-container" }, [
      createElementVNode("view", { class: "uni-header-logo" }, [
        createElementVNode("u-image", {
          class: "uni-header-image",
          src: _imports_0
        })
      ]),
      createElementVNode("view", { class: "menu-list" }, [
        createElementVNode("view", {
          class: "menu-item",
          onClick: _cache[0] || (_cache[0] = ($event) => $options.navigateTo("/pages/template/company/company"))
        }, [
          createElementVNode("u-text", { class: "menu-text" }, "公司简介"),
          createElementVNode("u-text", { class: "menu-icon" }, "")
        ]),
        createElementVNode("view", {
          class: "menu-item",
          onClick: _cache[1] || (_cache[1] = ($event) => $options.navigateTo("/pages/template/database/database"))
        }, [
          createElementVNode("u-text", { class: "menu-text" }, "数据库设置"),
          createElementVNode("u-text", { class: "menu-icon" }, "")
        ]),
        createElementVNode("view", {
          class: "menu-item",
          onClick: _cache[2] || (_cache[2] = ($event) => $options.navigateTo("/pages/template/account/account"))
        }, [
          createElementVNode("u-text", { class: "menu-text" }, "账号设置"),
          createElementVNode("u-text", { class: "menu-icon" }, "")
        ])
      ]),
      createElementVNode("view", { class: "logout-section" }, [
        createVNode(_component_button, {
          class: "logout-btn",
          onClick: $options.logout
        }, {
          default: withCtx(() => [
            createTextVNode("退出登录")
          ]),
          _: 1
        }, 8, ["onClick"])
      ])
    ])
  ]);
}
const template = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render], ["styles", [_style_0]]]);
export {
  template as default
};
