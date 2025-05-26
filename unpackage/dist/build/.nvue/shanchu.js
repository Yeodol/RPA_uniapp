import "vue";
function formatAppLog(type, filename, ...args) {
  if (uni.__log__) {
    uni.__log__(type, filename, ...args);
  } else {
    console[type].apply(console, [...args, filename]);
  }
}
function resolveEasycom(component, easycom) {
  return typeof component === "string" ? easycom : component;
}
const appConfig = {
  // 后端API基础地址
  // 格式: 'http://主机地址:端口号'
  // 例如: 'http://localhost:5032' 或 'http://1.95.90.167:5032'
  apiBaseUrl: "http://1.95.90.167:5032",
  // API路径配置
  apiPaths: {
    dataList: "/api/data",
    dataDelete: "/api/data/delete",
    files: "/api/files",
    txtData: "/data/txt",
    reports: {
      list: "/api/reports/list",
      generate: "/api/reports/generate",
      view: "/api/reports/view",
      delete: "/api/reports/delete",
      check: "/api/reports/check"
    }
  },
  // 数据库配置
  database: {
    username: "apppet",
    password: "apppet12345",
    database: "apppet",
    table: "data"
  },
  // 应用信息
  appInfo: {
    name: "数据管理系统",
    version: "1.0.0",
    company: "青岛英赛特生物科技有限公司",
    copyright: "© 2023 青岛英赛特生物科技有限公司. 保留所有权利."
  }
};
const _imports_0 = "/static/chazhao.png";
const _imports_1 = "/static/shanchu.png";
export {
  _imports_0 as _,
  appConfig as a,
  _imports_1 as b,
  formatAppLog as f,
  resolveEasycom as r
};
