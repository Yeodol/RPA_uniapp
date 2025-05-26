import { a as appConfig, f as formatAppLog, _ as _imports_0, b as _imports_1 } from "../../../shanchu.js";
import { resolveComponent, openBlock, createElementBlock, createElementVNode, createVNode, withCtx, toDisplayString, createCommentVNode, Fragment, renderList, normalizeClass } from "vue";
import { _ as _export_sfc } from "../../../_plugin-vue_export-helper.js";
const _style_0 = { "uni-icon": { "": { "fontFamily": "uniicons", "fontWeight": "normal" } }, "uni-container": { "": { "paddingTop": 15, "paddingRight": 15, "paddingBottom": 15, "paddingLeft": 15, "backgroundColor": "#F5F5F5", "flex": 1 } }, "uni-header-logo": { "": { "paddingTop": 15, "paddingRight": 15, "paddingBottom": 15, "paddingLeft": 15, "flexDirection": "column", "justifyContent": "center", "alignItems": "center", "marginTop": "10rpx" } }, "uni-header-image": { "": { "width": 80, "height": 80 } }, "uni-hello-text": { "": { "marginBottom": 20 } }, "hello-text": { "": { "color": "#7A7E83", "fontSize": 14, "lineHeight": 20 } }, "hello-link": { "": { "color": "#7A7E83", "fontSize": 14, "lineHeight": 20 } }, "uni-panel": { "": { "marginBottom": 12 } }, "uni-panel-h": { "": { "backgroundColor": "#ffffff", "!flexDirection": "row", "!alignItems": "center", "paddingTop": 12, "paddingRight": 12, "paddingBottom": 12, "paddingLeft": 12 } }, "uni-panel-h-on": { "": { "backgroundColor": "#f0f0f0" } }, "uni-panel-text": { "": { "flex": 1, "color": "#000000", "fontSize": 14, "fontWeight": "normal" } }, "uni-panel-icon": { "": { "marginLeft": 15, "color": "#999999", "fontSize": 14, "fontWeight": "normal", "transform": "rotate(0deg)", "transitionDuration": 0, "transitionProperty": "transform" } }, "uni-panel-icon-on": { "": { "transform": "rotate(180deg)" } }, "uni-navigate-item": { "": { "flexDirection": "row", "alignItems": "center", "backgroundColor": "#FFFFFF", "borderTopStyle": "solid", "borderTopColor": "#f0f0f0", "borderTopWidth": 1, "paddingTop": 12, "paddingRight": 12, "paddingBottom": 12, "paddingLeft": 12, "backgroundColor:active": "#f8f8f8" } }, "uni-navigate-text": { "": { "flex": 1, "color": "#000000", "fontSize": 14, "fontWeight": "normal" } }, "uni-navigate-icon": { "": { "marginLeft": 15, "color": "#999999", "fontSize": 14, "fontWeight": "normal" } }, "filter-container": { "": { "backgroundColor": "#FFFFFF", "borderRadius": 8, "paddingTop": 12, "paddingRight": 12, "paddingBottom": 12, "paddingLeft": 12, "marginBottom": 10 } }, "search-box": { "": { "flexDirection": "row", "alignItems": "center", "borderWidth": 1, "borderStyle": "solid", "borderColor": "#E0E0E0", "borderRadius": 4, "paddingTop": 0, "paddingRight": 10, "paddingBottom": 0, "paddingLeft": 10, "marginBottom": 10 } }, "search-input": { "": { "flex": 1, "height": 36, "fontSize": 14 } }, "search-btn": { "": { "width": 36, "height": 36, "justifyContent": "center", "alignItems": "center" } }, "search-icon": { "": { "width": 20, "height": 20 } }, "filter-options": { "": { "flexDirection": "row", "flexWrap": "wrap" } }, "filter-item": { "": { "flexDirection": "row", "alignItems": "center", "marginRight": 15, "marginBottom": 10 } }, "filter-label": { "": { "fontSize": 13, "color": "#333333", "marginRight": 5 } }, "filter-picker": { "": { "width": 120 } }, "picker-view": { "": { "height": 30, "borderWidth": 1, "borderStyle": "solid", "borderColor": "#E0E0E0", "borderRadius": 4, "paddingTop": 0, "paddingRight": 8, "paddingBottom": 0, "paddingLeft": 8, "justifyContent": "center" } }, "picker-text": { "": { "fontSize": 13, "color": "#666666" } }, "filter-actions": { "": { "flexDirection": "row", "justifyContent": "center", "marginTop": 10, "width": 100 } }, "filter-btn": { "": { "paddingTop": 6, "paddingRight": 15, "paddingBottom": 6, "paddingLeft": 15, "borderRadius": 4, "marginTop": 0, "marginRight": 10, "marginBottom": 0, "marginLeft": 10, "alignItems": "center", "justifyContent": "center" } }, "filter-btn-text": { "": { "fontSize": 14 }, ".refresh-btn ": { "color": "#FFFFFF" }, ".reset-btn ": { "color": "#666666" }, ".apply-btn ": { "!color": "#FFFFFF" } }, "refresh-btn": { "": { "backgroundColor": "#1E90FF", "borderWidth": 1, "borderStyle": "solid", "borderColor": "#1E90FF" } }, "reset-btn": { "": { "backgroundColor": "#F5F5F5", "borderWidth": 1, "borderStyle": "solid", "borderColor": "#DDDDDD" } }, "apply-btn": { "": { "backgroundColor": "#2871FA", "borderWidth": 1, "borderStyle": "solid", "borderColor": "#2871FA" } }, "current-filters": { "": { "backgroundColor": "#F0F8FF", "borderRadius": 4, "paddingTop": 8, "paddingRight": 12, "paddingBottom": 8, "paddingLeft": 12, "flexDirection": "row", "flexWrap": "wrap", "marginBottom": 10 } }, "current-filters-text": { "": { "fontSize": 12, "color": "#666666" } }, "current-filters-value": { "": { "fontSize": 12, "color": "#2871FA", "marginRight": 8 } }, "records-list": { "": { "flexDirection": "column" } }, "record-item": { "": { "flexDirection": "row", "backgroundColor": "#FFFFFF", "borderRadius": 8, "marginBottom": 10, "overflow": "hidden" } }, "record-left-border": { "": { "width": 8, "backgroundColor": "#2871FA" } }, "record-content": { "": { "flex": 1, "paddingTop": 12, "paddingRight": 12, "paddingBottom": 12, "paddingLeft": 12 } }, "record-header": { "": { "flexDirection": "row", "alignItems": "center" } }, "record-info": { "": { "flex": 1 } }, "record-row": { "": { "flexDirection": "row", "alignItems": "center", "marginBottom": 4 } }, "record-label": { "": { "color": "#333333", "fontSize": 13, "marginRight": 5, "width": 70 } }, "record-value": { "": { "color": "#666666", "fontSize": 13, "flex": 1 } }, "record-actions": { "": { "flexDirection": "row", "alignItems": "center" } }, "action-btn": { "": { "width": 28, "height": 28, "borderRadius": 14, "alignItems": "center", "justifyContent": "center", "marginLeft": 8 } }, "action-img": { "": { "width": 16, "height": 16 } }, "view-btn": { "": { "backgroundColor": "#2871FA" } }, "delete-btn": { "": { "backgroundColor": "#FF5252" } }, "no-data": { "": { "paddingTop": 30, "paddingRight": 0, "paddingBottom": 30, "paddingLeft": 0, "alignItems": "center", "justifyContent": "center" } }, "no-data-text": { "": { "color": "#999999", "fontSize": 14 } }, "pagination": { "": { "flexDirection": "row", "justifyContent": "center", "alignItems": "center", "flexWrap": "wrap", "marginTop": 15, "paddingTop": 10, "paddingRight": 0, "paddingBottom": 10, "paddingLeft": 0 } }, "pagination-btn": { "": { "backgroundColor": "#2871FA", "paddingTop": 6, "paddingRight": 15, "paddingBottom": 6, "paddingLeft": 15, "borderRadius": 4, "marginTop": 0, "marginRight": 5, "marginBottom": 0, "marginLeft": 5 }, ".disabled": { "backgroundColor": "#CCCCCC", "opacity": 0.6 } }, "pagination-info": { "": { "paddingTop": 5, "paddingRight": 10, "paddingBottom": 5, "paddingLeft": 10 } }, "pagination-text": { "": { "color": "#FFFFFF", "fontSize": 14 }, ".pagination-info ": { "color": "#333333" } }, "pagination-jump": { "": { "flexDirection": "row", "alignItems": "center", "marginLeft": 10, "marginTop": 8 } }, "jump-label": { "": { "color": "#333333", "fontSize": 14, "marginTop": 0, "marginRight": 5, "marginBottom": 0, "marginLeft": 5 } }, "jump-input": { "": { "width": 50, "height": 30, "borderWidth": 1, "borderStyle": "solid", "borderColor": "#E0E0E0", "borderRadius": 4, "fontSize": 14, "textAlign": "center", "backgroundColor": "#FFFFFF" } }, "jump-btn": { "": { "marginLeft": 5, "paddingTop": 6, "paddingRight": 10, "paddingBottom": 6, "paddingLeft": 10 } }, "@TRANSITION": { "uni-panel-icon": { "duration": 0, "property": "transform" } } };
const _sfc_main = {
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
      reports: [],
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
      sortOptions: ["按时间倒序", "按时间正序"]
    };
  },
  computed: {
    apiReportsUrl() {
      return `${this.config.apiBaseUrl}/api/reports/list`;
    },
    apiReportDeleteUrl() {
      return `${this.config.apiBaseUrl}/api/reports/delete`;
    },
    hasActiveFilters() {
      return this.searchKeyword || this.sortIndex !== 0 || this.startDate || this.endDate;
    },
    filteredRecords() {
      let result = [...this.reports];
      if (this.searchKeyword.trim()) {
        const keyword = this.searchKeyword.trim().toLowerCase();
        result = result.filter(
          (item) => item.report_name && item.report_name.toLowerCase().includes(keyword)
        );
      }
      if (this.startDate || this.endDate) {
        result = result.filter((item) => {
          if (!item.report_time)
            return false;
          const itemDate = new Date(item.report_time);
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
        const dateA = new Date(a.report_time || 0);
        const dateB = new Date(b.report_time || 0);
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
      path: "/pages/tabBar/component/component"
    };
  },
  onNavigationBarButtonTap(e) {
    uni.navigateTo({
      url: "/pages/about/about"
    });
  },
  onLoad() {
    uni.setNavigationBarTitle({
      title: "报告管理"
    });
    this.fetchReports();
  },
  onPullDownRefresh() {
    this.fetchReports();
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
      this.fetchReports();
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
    fetchReports() {
      uni.showLoading({
        title: "加载中"
      });
      uni.request({
        url: this.apiReportsUrl,
        method: "GET",
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            formatAppLog("log", "at pages/tabBar/component/component.nvue:390", `成功获取报告：${res.data.length}条`);
            this.reports = res.data;
            this.resetFilters();
          } else {
            uni.showToast({
              title: "获取报告列表失败",
              icon: "none"
            });
          }
        },
        fail: (err) => {
          formatAppLog("error", "at pages/tabBar/component/component.nvue:403", "请求失败:", err);
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
    viewReport(item) {
      uni.showLoading({ title: "加载报告中..." });
      uni.request({
        url: `${this.config.apiBaseUrl}/api/reports/view/${encodeURIComponent(item.report_name)}`,
        method: "GET",
        success: (res) => {
          uni.hideLoading();
          if (res.statusCode === 200 && res.data.success) {
            formatAppLog("log", "at pages/tabBar/component/component.nvue:425", "成功获取报告内容，内容长度:", res.data.content ? res.data.content.length : 0);
            const downloadUrl = res.data.download_url || "";
            uni.navigateTo({
              url: `/pages/pdf-viewer?pdf=${encodeURIComponent(res.data.content)}&filename=${encodeURIComponent(res.data.filename)}&downloadUrl=${encodeURIComponent(downloadUrl)}`,
              fail: (err) => {
                formatAppLog("error", "at pages/tabBar/component/component.nvue:432", "跳转到PDF查看器失败:", err);
                if (downloadUrl) {
                  formatAppLog("log", "at pages/tabBar/component/component.nvue:435", "尝试直接下载PDF");
                  const fullUrl = `${this.config.apiBaseUrl}${downloadUrl}`;
                  try {
                    const systemInfo = uni.getSystemInfoSync();
                    if (systemInfo.platform === "android" || systemInfo.platform === "ios") {
                      plus.runtime.openURL(fullUrl);
                    } else {
                      window.open(fullUrl, "_blank");
                    }
                  } catch (e) {
                    try {
                      window.open(fullUrl, "_blank");
                    } catch (e2) {
                      uni.showToast({
                        title: "无法打开PDF，请稍后再试",
                        icon: "none"
                      });
                    }
                  }
                } else {
                  uni.showToast({
                    title: "无法打开PDF查看器",
                    icon: "none"
                  });
                }
              }
            });
          } else {
            formatAppLog("error", "at pages/tabBar/component/component.nvue:467", "获取报告失败:", res);
            uni.showToast({
              title: res.data && res.data.error ? res.data.error : "获取报告失败",
              icon: "none"
            });
          }
        },
        fail: (err) => {
          uni.hideLoading();
          formatAppLog("error", "at pages/tabBar/component/component.nvue:476", "下载报告失败:", err);
          uni.showToast({
            title: "网络请求失败",
            icon: "none"
          });
        }
      });
    },
    deleteReport(item) {
      uni.showModal({
        title: "提示",
        content: "确定要删除报告 " + item.report_name + " 吗？",
        success: (res) => {
          if (res.confirm) {
            uni.showLoading({
              title: "删除中..."
            });
            uni.request({
              url: this.apiReportDeleteUrl,
              method: "POST",
              data: { filename: item.report_name },
              success: (res2) => {
                if (res2.statusCode === 200 && res2.data.success) {
                  const index = this.reports.findIndex((report) => report.report_name === item.report_name);
                  if (index !== -1) {
                    this.reports.splice(index, 1);
                  }
                  uni.showToast({
                    title: "报告已删除",
                    icon: "success"
                  });
                } else {
                  uni.showToast({
                    title: "删除报告失败",
                    icon: "none"
                  });
                  formatAppLog("error", "at pages/tabBar/component/component.nvue:516", "删除报告失败:", res2.data);
                }
              },
              fail: (err) => {
                uni.showToast({
                  title: "网络请求失败",
                  icon: "none"
                });
                formatAppLog("error", "at pages/tabBar/component/component.nvue:524", "网络请求失败:", err);
              },
              complete: () => {
                uni.hideLoading();
              }
            });
          }
        }
      });
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
            placeholder: "搜索报告"
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
                    createElementVNode("u-text", { class: "record-label" }, "报告名称:"),
                    createElementVNode("u-text", { class: "record-value" }, toDisplayString(item.report_name), 1)
                  ]),
                  createElementVNode("view", { class: "record-row" }, [
                    createElementVNode("u-text", { class: "record-label" }, "生成时间:"),
                    createElementVNode("u-text", { class: "record-value" }, toDisplayString($options.formatDate(item.report_time)), 1)
                  ])
                ]),
                createElementVNode("view", { class: "record-actions" }, [
                  createElementVNode("view", {
                    class: "action-btn view-btn",
                    onClick: ($event) => $options.viewReport(item)
                  }, [
                    createElementVNode("u-image", {
                      class: "action-img",
                      src: _imports_0
                    })
                  ], 8, ["onClick"]),
                  createElementVNode("view", {
                    class: "action-btn delete-btn",
                    onClick: ($event) => $options.deleteReport(item)
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
          createElementVNode("u-text", { class: "no-data-text" }, "暂无符合条件的报告")
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
      ])) : createCommentVNode("", true)
    ])
  ]);
}
const component = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", _sfc_render], ["styles", [_style_0]]]);
export {
  component as default
};
