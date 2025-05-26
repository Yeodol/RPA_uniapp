import { r as resolveEasycom, a as appConfig, f as formatAppLog, _ as _imports_0, b as _imports_1 } from "../../../shanchu.js";
import { openBlock, createElementBlock, createElementVNode, toDisplayString, resolveDynamicComponent, resolveComponent, createVNode, withCtx, createTextVNode, createCommentVNode, Fragment, renderList, normalizeClass } from "vue";
import { _ as _export_sfc } from "../../../_plugin-vue_export-helper.js";
const _sfc_main$2 = {
  name: "page-head",
  props: {
    title: {
      type: String,
      default: ""
    }
  }
};
function _sfc_render$2(_ctx, _cache, $props, $setup, $data, $options) {
  return openBlock(), createElementBlock("view", {
    class: "common-page-head",
    renderWhole: true
  }, [
    createElementVNode("view", { class: "common-page-head-title" }, [
      createElementVNode("u-text", null, toDisplayString($props.title), 1)
    ])
  ]);
}
const __easycom_0 = /* @__PURE__ */ _export_sfc(_sfc_main$2, [["render", _sfc_render$2]]);
const _style_0$1 = { "button": { "": { "marginTop": "30rpx", "marginLeft": 0, "marginRight": 0 } }, "btn-area": { "": { "paddingTop": "30rpx" } } };
const _sfc_main$1 = {
  data() {
    return {
      title: "tababr",
      hasSetTabBarBadge: false,
      hasShownTabBarRedDot: false,
      hasCustomedStyle: false,
      hasCustomedItem: false,
      hasHiddenTabBar: false
    };
  },
  destroyed() {
    if (this.hasSetTabBarBadge) {
      uni.removeTabBarBadge({
        index: 1
      });
    }
    if (this.hasShownTabBarRedDot) {
      uni.hideTabBarRedDot({
        index: 1
      });
    }
    if (this.hasHiddenTabBar) {
      uni.showTabBar();
    }
    if (this.hasCustomedStyle) {
      uni.setTabBarStyle({
        color: "#7A7E83",
        selectedColor: "#007AFF",
        backgroundColor: "#F8F8F8",
        borderStyle: "black"
      });
    }
    if (this.hasCustomedItem) {
      let tabBarOptions = {
        index: 1,
        text: "接口",
        iconPath: "/static/api.png",
        selectedIconPath: "/static/apiHL.png"
      };
      uni.setTabBarItem(tabBarOptions);
    }
  },
  methods: {
    navigateBack() {
      this.$emit("unmount");
    },
    setTabBarBadge() {
      if (this.hasShownTabBarRedDot) {
        uni.hideTabBarRedDot({
          index: 1
        });
        this.hasShownTabBarRedDot = !this.hasShownTabBarRedDot;
      }
      if (!this.hasSetTabBarBadge) {
        uni.setTabBarBadge({
          index: 1,
          text: "1"
        });
      } else {
        uni.removeTabBarBadge({
          index: 1
        });
      }
      this.hasSetTabBarBadge = !this.hasSetTabBarBadge;
    },
    showTabBarRedDot() {
      if (this.hasSetTabBarBadge) {
        uni.removeTabBarBadge({
          index: 1
        });
        this.hasSetTabBarBadge = !this.hasSetTabBarBadge;
      }
      if (!this.hasShownTabBarRedDot) {
        uni.showTabBarRedDot({
          index: 1
        });
      } else {
        uni.hideTabBarRedDot({
          index: 1
        });
      }
      this.hasShownTabBarRedDot = !this.hasShownTabBarRedDot;
    },
    hideTabBar() {
      if (!this.hasHiddenTabBar) {
        uni.hideTabBar();
      } else {
        uni.showTabBar();
      }
      this.hasHiddenTabBar = !this.hasHiddenTabBar;
    },
    customStyle() {
      if (this.hasCustomedStyle) {
        uni.setTabBarStyle({
          color: "#7A7E83",
          selectedColor: "#007AFF",
          backgroundColor: "#F8F8F8",
          borderStyle: "black"
        });
      } else {
        uni.setTabBarStyle({
          color: "#FFF",
          selectedColor: "#007AFF",
          backgroundColor: "#000000",
          borderStyle: "black"
        });
      }
      this.hasCustomedStyle = !this.hasCustomedStyle;
    },
    customItem() {
      let tabBarOptions = {
        index: 1,
        text: "接口",
        iconPath: "/static/api.png",
        selectedIconPath: "/static/apiHL.png"
      };
      if (this.hasCustomedItem) {
        uni.setTabBarItem(tabBarOptions);
      } else {
        tabBarOptions.text = "API";
        uni.setTabBarItem(tabBarOptions);
      }
      this.hasCustomedItem = !this.hasCustomedItem;
    }
  }
};
function _sfc_render$1(_ctx, _cache, $props, $setup, $data, $options) {
  const _component_page_head = resolveEasycom(resolveDynamicComponent("page-head"), __easycom_0);
  const _component_button = resolveComponent("button");
  return openBlock(), createElementBlock("view", {
    class: "uni-padding-wrap",
    renderWhole: true
  }, [
    createVNode(_component_page_head, { title: $data.title }, null, 8, ["title"]),
    createVNode(_component_button, {
      class: "button",
      onClick: $options.setTabBarBadge
    }, {
      default: withCtx(() => [
        createTextVNode(toDisplayString(!$data.hasSetTabBarBadge ? "设置tab徽标" : "移除tab徽标"), 1)
      ]),
      _: 1
    }, 8, ["onClick"]),
    createVNode(_component_button, {
      class: "button",
      onClick: $options.showTabBarRedDot
    }, {
      default: withCtx(() => [
        createTextVNode(toDisplayString(!$data.hasShownTabBarRedDot ? "显示红点" : "移除红点"), 1)
      ]),
      _: 1
    }, 8, ["onClick"]),
    createVNode(_component_button, {
      class: "button",
      onClick: $options.customStyle
    }, {
      default: withCtx(() => [
        createTextVNode(toDisplayString(!$data.hasCustomedStyle ? "自定义Tab样式" : "移除自定义样式"), 1)
      ]),
      _: 1
    }, 8, ["onClick"]),
    createVNode(_component_button, {
      class: "button",
      onClick: $options.customItem
    }, {
      default: withCtx(() => [
        createTextVNode(toDisplayString(!$data.hasCustomedItem ? "自定义Tab信息" : "移除自定义信息"), 1)
      ]),
      _: 1
    }, 8, ["onClick"]),
    createVNode(_component_button, {
      class: "button",
      onClick: $options.hideTabBar
    }, {
      default: withCtx(() => [
        createTextVNode(toDisplayString(!$data.hasHiddenTabBar ? "隐藏TabBar" : "显示TabBar"), 1)
      ]),
      _: 1
    }, 8, ["onClick"]),
    createElementVNode("view", { class: "btn-area" }, [
      createVNode(_component_button, {
        class: "button",
        type: "primary",
        onClick: $options.navigateBack
      }, {
        default: withCtx(() => [
          createTextVNode("返回上一级")
        ]),
        _: 1
      }, 8, ["onClick"])
    ])
  ]);
}
const setTabBar = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["render", _sfc_render$1], ["styles", [_style_0$1]]]);
const _style_0 = { "uni-icon": { "": { "fontFamily": "uniicons", "fontWeight": "normal" } }, "uni-container": { "": { "paddingTop": 15, "paddingRight": 15, "paddingBottom": 15, "paddingLeft": 15, "backgroundColor": "#F5F5F5", "flex": 1 } }, "uni-header-logo": { "": { "paddingTop": 15, "paddingRight": 15, "paddingBottom": 15, "paddingLeft": 15, "flexDirection": "column", "justifyContent": "center", "alignItems": "center", "marginTop": "10rpx" } }, "uni-header-image": { "": { "width": 80, "height": 80 } }, "uni-hello-text": { "": { "marginBottom": 20 } }, "hello-text": { "": { "color": "#7A7E83", "fontSize": 14, "lineHeight": 20 } }, "hello-link": { "": { "color": "#7A7E83", "fontSize": 14, "lineHeight": 20 } }, "uni-panel": { "": { "marginBottom": 12 } }, "uni-panel-h": { "": { "backgroundColor": "#ffffff", "!flexDirection": "row", "!alignItems": "center", "paddingTop": 12, "paddingRight": 12, "paddingBottom": 12, "paddingLeft": 12 } }, "uni-panel-h-on": { "": { "backgroundColor": "#f0f0f0" } }, "uni-panel-text": { "": { "flex": 1, "color": "#000000", "fontSize": 14, "fontWeight": "normal" } }, "uni-panel-icon": { "": { "marginLeft": 15, "color": "#999999", "fontSize": 14, "fontWeight": "normal", "transform": "rotate(0deg)", "transitionDuration": 0, "transitionProperty": "transform" } }, "uni-panel-icon-on": { "": { "transform": "rotate(180deg)" } }, "uni-navigate-item": { "": { "flexDirection": "row", "alignItems": "center", "backgroundColor": "#FFFFFF", "borderTopStyle": "solid", "borderTopColor": "#f0f0f0", "borderTopWidth": 1, "paddingTop": 12, "paddingRight": 12, "paddingBottom": 12, "paddingLeft": 12, "backgroundColor:active": "#f8f8f8" } }, "uni-navigate-text": { "": { "flex": 1, "color": "#000000", "fontSize": 14, "fontWeight": "normal" } }, "uni-navigate-icon": { "": { "marginLeft": 15, "color": "#999999", "fontSize": 14, "fontWeight": "normal" } }, "filter-container": { "": { "backgroundColor": "#FFFFFF", "borderRadius": 8, "paddingTop": 12, "paddingRight": 12, "paddingBottom": 12, "paddingLeft": 12, "marginBottom": 10 } }, "search-box": { "": { "flexDirection": "row", "alignItems": "center", "borderWidth": 1, "borderStyle": "solid", "borderColor": "#E0E0E0", "borderRadius": 4, "paddingTop": 0, "paddingRight": 10, "paddingBottom": 0, "paddingLeft": 10, "marginBottom": 10 } }, "search-input": { "": { "flex": 1, "height": 36, "fontSize": 14 } }, "search-btn": { "": { "width": 36, "height": 36, "justifyContent": "center", "alignItems": "center" } }, "search-icon": { "": { "width": 20, "height": 20 } }, "filter-options": { "": { "flexDirection": "row", "flexWrap": "wrap" } }, "filter-item": { "": { "flexDirection": "row", "alignItems": "center", "marginRight": 15, "marginBottom": 10 } }, "filter-label": { "": { "fontSize": 13, "color": "#333333", "marginRight": 5 } }, "filter-picker": { "": { "width": 120 } }, "picker-view": { "": { "height": 30, "borderWidth": 1, "borderStyle": "solid", "borderColor": "#E0E0E0", "borderRadius": 4, "paddingTop": 0, "paddingRight": 8, "paddingBottom": 0, "paddingLeft": 8, "justifyContent": "center" } }, "picker-text": { "": { "fontSize": 13, "color": "#666666" } }, "filter-actions": { "": { "flexDirection": "row", "justifyContent": "center", "marginTop": 10, "width": 100 } }, "filter-btn": { "": { "paddingTop": 6, "paddingRight": 15, "paddingBottom": 6, "paddingLeft": 15, "borderRadius": 4, "marginTop": 0, "marginRight": 10, "marginBottom": 0, "marginLeft": 10, "alignItems": "center", "justifyContent": "center" } }, "filter-btn-text": { "": { "fontSize": 14 }, ".refresh-btn ": { "color": "#FFFFFF" }, ".reset-btn ": { "color": "#666666" }, ".apply-btn ": { "!color": "#FFFFFF" } }, "refresh-btn": { "": { "backgroundColor": "#1E90FF", "borderWidth": 1, "borderStyle": "solid", "borderColor": "#1E90FF" } }, "reset-btn": { "": { "backgroundColor": "#F5F5F5", "borderWidth": 1, "borderStyle": "solid", "borderColor": "#DDDDDD" } }, "apply-btn": { "": { "backgroundColor": "#2871FA", "borderWidth": 1, "borderStyle": "solid", "borderColor": "#2871FA" } }, "current-filters": { "": { "backgroundColor": "#F0F8FF", "borderRadius": 4, "paddingTop": 8, "paddingRight": 12, "paddingBottom": 8, "paddingLeft": 12, "flexDirection": "row", "flexWrap": "wrap", "marginBottom": 10 } }, "current-filters-text": { "": { "fontSize": 12, "color": "#666666" } }, "current-filters-value": { "": { "fontSize": 12, "color": "#2871FA", "marginRight": 8 } }, "records-list": { "": { "flexDirection": "column" } }, "record-item": { "": { "flexDirection": "row", "backgroundColor": "#FFFFFF", "borderRadius": 8, "marginBottom": 10, "overflow": "hidden" } }, "record-left-border": { "": { "width": 8, "backgroundColor": "#2871FA" } }, "record-content": { "": { "flex": 1, "paddingTop": 12, "paddingRight": 12, "paddingBottom": 12, "paddingLeft": 12 } }, "record-header": { "": { "flexDirection": "row", "alignItems": "center" } }, "record-info": { "": { "flex": 1 } }, "record-row": { "": { "flexDirection": "row", "alignItems": "center", "marginBottom": 4 } }, "record-label": { "": { "color": "#333333", "fontSize": 13, "marginRight": 5, "width": 70 } }, "record-value": { "": { "color": "#666666", "fontSize": 13, "flex": 1 } }, "record-actions": { "": { "flexDirection": "row", "alignItems": "center" } }, "action-btn": { "": { "width": 28, "height": 28, "borderRadius": 14, "alignItems": "center", "justifyContent": "center", "marginLeft": 8 } }, "action-img": { "": { "width": 16, "height": 16 } }, "view-btn": { "": { "backgroundColor": "#2871FA" } }, "delete-btn": { "": { "backgroundColor": "#FF5252" } }, "no-data": { "": { "paddingTop": 30, "paddingRight": 0, "paddingBottom": 30, "paddingLeft": 0, "alignItems": "center", "justifyContent": "center" } }, "no-data-text": { "": { "color": "#999999", "fontSize": 14 } }, "pagination": { "": { "flexDirection": "row", "justifyContent": "center", "alignItems": "center", "flexWrap": "wrap", "marginTop": 15, "paddingTop": 10, "paddingRight": 0, "paddingBottom": 10, "paddingLeft": 0 } }, "pagination-btn": { "": { "backgroundColor": "#2871FA", "paddingTop": 6, "paddingRight": 15, "paddingBottom": 6, "paddingLeft": 15, "borderRadius": 4, "marginTop": 0, "marginRight": 5, "marginBottom": 0, "marginLeft": 5 }, ".disabled": { "backgroundColor": "#CCCCCC", "opacity": 0.6 } }, "pagination-info": { "": { "paddingTop": 5, "paddingRight": 10, "paddingBottom": 5, "paddingLeft": 10 } }, "pagination-text": { "": { "color": "#FFFFFF", "fontSize": 14 }, ".pagination-info ": { "color": "#333333" } }, "pagination-jump": { "": { "flexDirection": "row", "alignItems": "center", "marginLeft": 10, "marginTop": 8 } }, "jump-label": { "": { "color": "#333333", "fontSize": 14, "marginTop": 0, "marginRight": 5, "marginBottom": 0, "marginLeft": 5 } }, "jump-input": { "": { "width": 50, "height": 30, "borderWidth": 1, "borderStyle": "solid", "borderColor": "#E0E0E0", "borderRadius": 4, "fontSize": 14, "textAlign": "center", "backgroundColor": "#FFFFFF" } }, "jump-btn": { "": { "marginLeft": 5, "paddingTop": 6, "paddingRight": 10, "paddingBottom": 6, "paddingLeft": 10 } }, "file-modal": { "": { "position": "fixed", "top": 0, "left": 0, "right": 0, "bottom": 0, "zIndex": 999 } }, "modal-mask": { "": { "position": "absolute", "top": 0, "left": 0, "right": 0, "bottom": 0, "backgroundColor": "rgba(0,0,0,0.5)" } }, "modal-content": { "": { "position": "absolute", "top": 50, "left": 50, "transform": "translate(-50%, -50%)", "width": 80, "maxWidth": "600px", "backgroundColor": "#FFFFFF", "borderRadius": 8, "overflow": "hidden" } }, "modal-header": { "": { "flexDirection": "row", "justifyContent": "space-between", "alignItems": "center", "paddingTop": 15, "paddingRight": 15, "paddingBottom": 15, "paddingLeft": 15, "borderBottomWidth": 1, "borderBottomColor": "#EEEEEE" } }, "modal-title": { "": { "fontSize": 16, "color": "#333333", "fontWeight": "bold" } }, "modal-close": { "": { "width": 30, "height": 30, "alignItems": "center", "justifyContent": "center" } }, "close-icon": { "": { "fontSize": 24, "color": "#999999" } }, "modal-body": { "": { "paddingTop": 15, "paddingRight": 15, "paddingBottom": 15, "paddingLeft": 15, "maxHeight": 60 } }, "file-content": { "": { "fontSize": 14, "color": "#333333", "lineHeight": 1.5 } }, "@TRANSITION": { "uni-panel-icon": { "duration": 0, "property": "transform" } } };
const _sfc_main = {
  components: {
    setTabBar
  },
  props: {
    hasLeftWin: {
      type: Boolean
    },
    leftWinActive: {
      type: String
    }
  },
  data() {
    return {
      records: [],
      config: appConfig,
      currentPage: 1,
      pageSize: 10,
      jumpPage: "",
      // 实际应用的筛选条件
      searchKeyword: "",
      sortIndex: 0,
      startDate: "",
      endDate: "",
      // 临时筛选条件（确认前）
      tempSearchKeyword: "",
      tempSortIndex: 0,
      tempStartDate: "",
      tempEndDate: "",
      sortOptions: ["按时间倒序", "按时间正序"],
      // 文件内容相关
      showFileContent: false,
      fileContent: "",
      currentFileName: ""
    };
  },
  computed: {
    apiDataUrl() {
      return `${this.config.apiBaseUrl}${this.config.apiPaths.dataList}`;
    },
    apiDeleteUrl() {
      return `${this.config.apiBaseUrl}${this.config.apiPaths.dataDelete}`;
    },
    dbConfig() {
      return this.config.database;
    },
    hasActiveFilters() {
      return this.searchKeyword || this.sortIndex !== 0 || this.startDate || this.endDate;
    },
    filteredRecords() {
      let result = [...this.records];
      if (this.searchKeyword.trim()) {
        const keyword = this.searchKeyword.trim().toLowerCase();
        result = result.filter(
          (item) => item.data_name && item.data_name.toLowerCase().includes(keyword)
        );
      }
      if (this.startDate || this.endDate) {
        result = result.filter((item) => {
          if (!item.data_update)
            return false;
          const itemDate = new Date(item.data_update);
          if (this.startDate) {
            const startDate = new Date(this.startDate);
            startDate.setHours(0, 0, 0, 0);
            if (itemDate < startDate)
              return false;
          }
          if (this.endDate) {
            const endDate = new Date(this.endDate);
            endDate.setHours(23, 59, 59, 999);
            if (itemDate > endDate)
              return false;
          }
          return true;
        });
      }
      result.sort((a, b) => {
        const dateA = new Date(a.data_update || 0);
        const dateB = new Date(b.data_update || 0);
        return this.sortIndex === 0 ? dateB - dateA : dateA - dateB;
      });
      return result;
    },
    totalPages() {
      return Math.max(1, Math.ceil(this.filteredRecords.length / this.pageSize));
    },
    currentPageRecords() {
      const start = (this.currentPage - 1) * this.pageSize;
      const end = start + this.pageSize;
      return this.filteredRecords.slice(start, end);
    }
  },
  watch: {
    filteredRecords() {
      this.currentPage = 1;
    }
  },
  onShareAppMessage() {
    return {
      title: "欢迎体验uni-app",
      path: "/pages/tabBar/API/API"
    };
  },
  onNavigationBarButtonTap(e) {
    uni.navigateTo({
      url: "/pages/about/about"
    });
  },
  onLoad() {
    uni.setNavigationBarTitle({
      title: "主页"
    });
    this.fetchRecords();
  },
  onReady() {
  },
  onShow() {
    this.navigateFlag = false;
  },
  onHide() {
  },
  onPullDownRefresh() {
    this.fetchRecords();
  },
  methods: {
    formatDate(dateString) {
      if (!dateString)
        return "";
      const date = new Date(dateString);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, "0");
      const day = String(date.getDate()).padStart(2, "0");
      const hours = String(date.getHours()).padStart(2, "0");
      const minutes = String(date.getMinutes()).padStart(2, "0");
      return `${year}-${month}-${day} ${hours}:${minutes}`;
    },
    formatSimpleDate(dateString) {
      if (!dateString)
        return "";
      const date = new Date(dateString);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, "0");
      const day = String(date.getDate()).padStart(2, "0");
      return `${year}-${month}-${day}`;
    },
    handleSortChange(e) {
      this.tempSortIndex = parseInt(e.detail.value);
    },
    handleStartDateChange(e) {
      this.tempStartDate = e.detail.value;
      if (this.tempEndDate && this.tempStartDate > this.tempEndDate) {
        this.tempEndDate = this.tempStartDate;
      }
    },
    handleEndDateChange(e) {
      this.tempEndDate = e.detail.value;
      if (this.tempStartDate && this.tempEndDate < this.tempStartDate) {
        this.tempStartDate = this.tempEndDate;
      }
    },
    resetFilters() {
      this.tempSearchKeyword = "";
      this.tempSortIndex = 0;
      this.tempStartDate = "";
      this.tempEndDate = "";
      this.searchKeyword = "";
      this.sortIndex = 0;
      this.startDate = "";
      this.endDate = "";
      this.currentPage = 1;
    },
    applyFilters() {
      this.searchKeyword = this.tempSearchKeyword;
      this.sortIndex = this.tempSortIndex;
      this.startDate = this.tempStartDate;
      this.endDate = this.tempEndDate;
      this.currentPage = 1;
      uni.showToast({
        title: "筛选已应用",
        icon: "success",
        duration: 1500
      });
    },
    refreshData() {
      uni.showLoading({
        title: "刷新中..."
      });
      this.fetchRecords();
      uni.showToast({
        title: "数据已刷新",
        icon: "success",
        duration: 1500
      });
    },
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
      }
    },
    handleJumpBlur() {
      if (this.jumpPage) {
        const page = parseInt(this.jumpPage);
        if (isNaN(page) || page < 1 || page > this.totalPages) {
          uni.showToast({
            title: "页码无效",
            icon: "none"
          });
          this.jumpPage = "";
        }
      }
    },
    jumpToPage() {
      if (this.jumpPage) {
        const page = parseInt(this.jumpPage);
        if (!isNaN(page) && page >= 1 && page <= this.totalPages) {
          this.currentPage = page;
        } else {
          uni.showToast({
            title: "页码无效",
            icon: "none"
          });
        }
        this.jumpPage = "";
      }
    },
    fetchRecords() {
      uni.showLoading({
        title: "加载中"
      });
      uni.request({
        url: this.apiDataUrl,
        method: "POST",
        data: this.dbConfig,
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            if (Array.isArray(res.data)) {
              formatAppLog("log", "at pages/tabBar/API/API.nvue:428", `成功获取记录：${res.data.length}条`);
              if (res.data.length > 0) {
                const firstRecord = res.data[0];
                formatAppLog("log", "at pages/tabBar/API/API.nvue:433", "记录结构示例:", firstRecord);
                if (!("data_id" in firstRecord)) {
                  formatAppLog("warn", "at pages/tabBar/API/API.nvue:437", "警告：记录缺少data_id字段");
                } else {
                  formatAppLog("log", "at pages/tabBar/API/API.nvue:439", "使用data_id作为记录唯一标识");
                }
              }
            }
            this.records = res.data;
            this.resetFilters();
          } else {
            uni.showToast({
              title: "获取数据失败",
              icon: "none"
            });
          }
        },
        fail: (err) => {
          formatAppLog("error", "at pages/tabBar/API/API.nvue:456", "请求失败:", err);
          uni.showToast({
            title: "网络请求失败",
            icon: "none"
          });
        },
        complete: () => {
          uni.hideLoading();
          uni.stopPullDownRefresh();
        }
      });
    },
    viewRecord(item) {
      const fileName = item.data_name + ".txt";
      formatAppLog("log", "at pages/tabBar/API/API.nvue:471", `跳转到分析页面，文件名: ${fileName}`);
      uni.navigateTo({
        url: `/pages/analysis/analysis?filename=${encodeURIComponent(fileName)}`
      });
    },
    deleteRecord(item) {
      uni.showModal({
        title: "提示",
        content: "确定要删除记录 " + item.data_name + " 吗？\n此操作将同时删除数据库记录和对应的数据文件！",
        success: (res) => {
          if (res.confirm) {
            formatAppLog("log", "at pages/tabBar/API/API.nvue:485", "要删除的记录:", item);
            formatAppLog("log", "at pages/tabBar/API/API.nvue:486", "记录ID:", item.data_id);
            if (!item.data_id && item.data_id !== 0) {
              formatAppLog("error", "at pages/tabBar/API/API.nvue:490", "错误：记录缺少data_id字段");
              uni.showToast({
                title: "记录ID无效",
                icon: "none"
              });
              return;
            }
            const requestData = {
              ...this.dbConfig,
              id: item.data_id
              // 使用data_id作为记录的唯一标识
            };
            formatAppLog("log", "at pages/tabBar/API/API.nvue:503", "发送的请求数据:", requestData);
            uni.request({
              url: this.apiDeleteUrl,
              method: "POST",
              data: requestData,
              success: (res2) => {
                if (res2.statusCode === 200) {
                  const txtFileName = item.data_name + ".txt";
                  const deleteFileUrl = `${this.config.apiBaseUrl}/api/files/delete`;
                  uni.request({
                    url: deleteFileUrl,
                    method: "POST",
                    data: {
                      filename: txtFileName
                    },
                    success: (fileRes) => {
                      const index = this.records.findIndex((record) => record.data_id === item.data_id);
                      if (index !== -1) {
                        this.records.splice(index, 1);
                      }
                      if (fileRes.statusCode === 200) {
                        uni.showToast({
                          title: "记录和文件已删除",
                          icon: "success"
                        });
                      } else {
                        uni.showToast({
                          title: "记录已删除，但文件删除失败",
                          icon: "none"
                        });
                        formatAppLog("error", "at pages/tabBar/API/API.nvue:540", "文件删除失败:", fileRes.data);
                      }
                    },
                    fail: (fileErr) => {
                      const index = this.records.findIndex((record) => record.data_id === item.data_id);
                      if (index !== -1) {
                        this.records.splice(index, 1);
                      }
                      uni.showToast({
                        title: "记录已删除，但文件删除请求失败",
                        icon: "none"
                      });
                      formatAppLog("error", "at pages/tabBar/API/API.nvue:554", "文件删除请求失败:", fileErr);
                    }
                  });
                } else {
                  uni.showToast({
                    title: "删除记录失败",
                    icon: "none"
                  });
                  formatAppLog("error", "at pages/tabBar/API/API.nvue:562", "删除记录失败:", res2.data);
                }
              },
              fail: (err) => {
                uni.showToast({
                  title: "网络请求失败",
                  icon: "none"
                });
                formatAppLog("error", "at pages/tabBar/API/API.nvue:570", "网络请求失败:", err);
              }
            });
          }
        }
      });
    },
    closeFileContent() {
      this.showFileContent = false;
      this.fileContent = "";
      this.currentFileName = "";
    }
  }
};
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  const _component_picker = resolveComponent("picker");
  return openBlock(), createElementBlock("scroll-view", {
    scrollY: true,
    showScrollbar: true,
    enableBackToTop: true,
    bubble: "true",
    style: { flexDirection: "column" }
  }, [
    createElementVNode("view", { class: "uni-container" }, [
      createElementVNode("view", { class: "filter-container" }, [
        createElementVNode("view", { class: "search-box" }, [
          createElementVNode("u-input", {
            class: "search-input",
            modelValue: $data.searchKeyword,
            onInput: _cache[0] || (_cache[0] = ($event) => $data.searchKeyword = $event.detail.value),
            placeholder: "搜索数据"
          }, null, 40, ["modelValue"]),
          createElementVNode("view", { class: "search-btn" }, [
            createElementVNode("u-image", {
              class: "search-icon",
              src: _imports_0
            })
          ])
        ]),
        createElementVNode("view", { class: "filter-options" }, [
          createElementVNode("view", { class: "filter-item" }, [
            createElementVNode("u-text", { class: "filter-label" }, "排序方式:"),
            createVNode(_component_picker, {
              class: "filter-picker",
              onChange: $options.handleSortChange,
              value: $data.tempSortIndex,
              range: $data.sortOptions
            }, {
              default: withCtx(() => [
                createElementVNode("view", { class: "picker-view" }, [
                  createElementVNode("u-text", { class: "picker-text" }, toDisplayString($data.sortOptions[$data.tempSortIndex]), 1)
                ])
              ]),
              _: 1
            }, 8, ["onChange", "value", "range"])
          ]),
          createElementVNode("view", { class: "filter-item" }, [
            createElementVNode("u-text", { class: "filter-label" }, "起始日期:"),
            createVNode(_component_picker, {
              class: "filter-picker",
              mode: "date",
              value: $data.tempStartDate,
              onChange: $options.handleStartDateChange
            }, {
              default: withCtx(() => [
                createElementVNode("view", { class: "picker-view" }, [
                  createElementVNode("u-text", { class: "picker-text" }, toDisplayString($data.tempStartDate || "全部"), 1)
                ])
              ]),
              _: 1
            }, 8, ["value", "onChange"])
          ]),
          createElementVNode("view", { class: "filter-item" }, [
            createElementVNode("u-text", { class: "filter-label" }, "结束日期:"),
            createVNode(_component_picker, {
              class: "filter-picker",
              mode: "date",
              value: $data.tempEndDate,
              onChange: $options.handleEndDateChange
            }, {
              default: withCtx(() => [
                createElementVNode("view", { class: "picker-view" }, [
                  createElementVNode("u-text", { class: "picker-text" }, toDisplayString($data.tempEndDate || "全部"), 1)
                ])
              ]),
              _: 1
            }, 8, ["value", "onChange"])
          ]),
          createElementVNode("view", { class: "filter-actions" }, [
            createElementVNode("view", {
              class: "filter-btn refresh-btn",
              onClick: _cache[1] || (_cache[1] = (...args) => $options.refreshData && $options.refreshData(...args))
            }, [
              createElementVNode("u-text", { class: "filter-btn-text" }, "刷新")
            ]),
            createElementVNode("view", {
              class: "filter-btn reset-btn",
              onClick: _cache[2] || (_cache[2] = (...args) => $options.resetFilters && $options.resetFilters(...args))
            }, [
              createElementVNode("u-text", { class: "filter-btn-text" }, "重置")
            ]),
            createElementVNode("view", {
              class: "filter-btn apply-btn",
              onClick: _cache[3] || (_cache[3] = (...args) => $options.applyFilters && $options.applyFilters(...args))
            }, [
              createElementVNode("u-text", { class: "filter-btn-text" }, "确认筛选")
            ])
          ])
        ])
      ]),
      $options.hasActiveFilters ? (openBlock(), createElementBlock("view", {
        key: 0,
        class: "current-filters"
      }, [
        createElementVNode("u-text", { class: "current-filters-text" }, "当前筛选: "),
        $data.searchKeyword ? (openBlock(), createElementBlock("u-text", {
          key: 0,
          class: "current-filters-value"
        }, '关键词"' + toDisplayString($data.searchKeyword) + '" ', 1)) : createCommentVNode("", true),
        $data.sortIndex === 1 ? (openBlock(), createElementBlock("u-text", {
          key: 1,
          class: "current-filters-value"
        }, "时间正序 ")) : createCommentVNode("", true),
        $data.startDate || $data.endDate ? (openBlock(), createElementBlock("u-text", {
          key: 2,
          class: "current-filters-value"
        }, " 日期" + toDisplayString($data.startDate ? $options.formatSimpleDate($data.startDate) : "起始") + "至" + toDisplayString($data.endDate ? $options.formatSimpleDate($data.endDate) : "现在"), 1)) : createCommentVNode("", true)
      ])) : createCommentVNode("", true),
      createElementVNode("view", { class: "records-list" }, [
        (openBlock(true), createElementBlock(Fragment, null, renderList($options.currentPageRecords, (item, index) => {
          return openBlock(), createElementBlock("view", {
            class: "record-item",
            key: index
          }, [
            createElementVNode("view", { class: "record-left-border" }),
            createElementVNode("view", { class: "record-content" }, [
              createElementVNode("view", { class: "record-header" }, [
                createElementVNode("view", { class: "record-info" }, [
                  createElementVNode("view", { class: "record-row" }, [
                    createElementVNode("u-text", { class: "record-label" }, "数据名称:"),
                    createElementVNode("u-text", { class: "record-value" }, toDisplayString(item.data_name), 1)
                  ]),
                  createElementVNode("view", { class: "record-row" }, [
                    createElementVNode("u-text", { class: "record-label" }, "记录时间:"),
                    createElementVNode("u-text", { class: "record-value" }, toDisplayString($options.formatDate(item.data_update)), 1)
                  ])
                ]),
                createElementVNode("view", { class: "record-actions" }, [
                  createElementVNode("view", {
                    class: "action-btn view-btn",
                    onClick: ($event) => $options.viewRecord(item)
                  }, [
                    createElementVNode("u-image", {
                      class: "action-img",
                      src: _imports_0
                    })
                  ], 8, ["onClick"]),
                  createElementVNode("view", {
                    class: "action-btn delete-btn",
                    onClick: ($event) => $options.deleteRecord(item)
                  }, [
                    createElementVNode("u-image", {
                      class: "action-img",
                      src: _imports_1
                    })
                  ], 8, ["onClick"])
                ])
              ])
            ])
          ]);
        }), 128)),
        $options.filteredRecords.length === 0 ? (openBlock(), createElementBlock("view", {
          key: 0,
          class: "no-data"
        }, [
          createElementVNode("u-text", { class: "no-data-text" }, "暂无符合条件的数据")
        ])) : createCommentVNode("", true)
      ]),
      $options.totalPages > 0 ? (openBlock(), createElementBlock("view", {
        key: 1,
        class: "pagination"
      }, [
        createElementVNode("view", {
          class: normalizeClass(["pagination-btn", { disabled: $data.currentPage === 1 }]),
          onClick: _cache[4] || (_cache[4] = (...args) => $options.prevPage && $options.prevPage(...args))
        }, [
          createElementVNode("u-text", { class: "pagination-text" }, "上一页")
        ], 2),
        createElementVNode("view", { class: "pagination-info" }, [
          createElementVNode("u-text", { class: "pagination-text" }, toDisplayString($data.currentPage) + "/" + toDisplayString($options.totalPages), 1)
        ]),
        createElementVNode("view", {
          class: normalizeClass(["pagination-btn", { disabled: $data.currentPage === $options.totalPages }]),
          onClick: _cache[5] || (_cache[5] = (...args) => $options.nextPage && $options.nextPage(...args))
        }, [
          createElementVNode("u-text", { class: "pagination-text" }, "下一页")
        ], 2),
        createElementVNode("view", { class: "pagination-jump" }, [
          createElementVNode("u-text", { class: "pagination-text jump-label" }, "跳转到"),
          createElementVNode("u-input", {
            class: "jump-input",
            type: "number",
            modelValue: $data.jumpPage,
            onInput: _cache[6] || (_cache[6] = ($event) => $data.jumpPage = $event.detail.value),
            onBlur: _cache[7] || (_cache[7] = (...args) => $options.handleJumpBlur && $options.handleJumpBlur(...args)),
            onConfirm: _cache[8] || (_cache[8] = (...args) => $options.jumpToPage && $options.jumpToPage(...args))
          }, null, 40, ["modelValue"]),
          createElementVNode("u-text", { class: "pagination-text jump-label" }, "页"),
          createElementVNode("view", {
            class: "pagination-btn jump-btn",
            onClick: _cache[9] || (_cache[9] = (...args) => $options.jumpToPage && $options.jumpToPage(...args))
          }, [
            createElementVNode("u-text", { class: "pagination-text" }, "确定")
          ])
        ])
      ])) : createCommentVNode("", true),
      $data.showFileContent ? (openBlock(), createElementBlock("view", {
        key: 2,
        class: "file-modal"
      }, [
        createElementVNode("view", {
          class: "modal-mask",
          onClick: _cache[10] || (_cache[10] = (...args) => $options.closeFileContent && $options.closeFileContent(...args))
        }),
        createElementVNode("view", { class: "modal-content" }, [
          createElementVNode("view", { class: "modal-header" }, [
            createElementVNode("u-text", { class: "modal-title" }, toDisplayString($data.currentFileName), 1),
            createElementVNode("view", {
              class: "modal-close",
              onClick: _cache[11] || (_cache[11] = (...args) => $options.closeFileContent && $options.closeFileContent(...args))
            }, [
              createElementVNode("u-text", { class: "close-icon" }, "×")
            ])
          ]),
          createElementVNode("scroll-view", {
            class: "modal-body",
            scrollY: "true"
          }, [
            createElementVNode("u-text", { class: "file-content" }, toDisplayString($data.fileContent), 1)
          ])
        ])
      ])) : createCommentVNode("", true)
    ])
  ]);
}
const API = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render], ["styles", [_style_0]]]);
export {
  API as default
};
