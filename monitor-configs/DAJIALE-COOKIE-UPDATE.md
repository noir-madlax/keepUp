# 大嘉乐Cookie更新指南

## 问题说明

当前Cookie已失效，页面显示"登录显示"而不是实际的余额数值。

## Cookie更新步骤

### 1. 重新导出Cookie

1. 在浏览器中访问 [大嘉乐主界面](https://dajiala.com/main/interface?actnav=0)
2. 确认已登录，并能看到实际余额（例如：余额： 189.14）
3. 安装并使用 [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/) 浏览器扩展
4. 点击扩展图标，选择"导出"（Export）
5. 复制导出的JSON格式Cookie数据

### 2. 更新Cookie文件

将导出的Cookie数据保存到：
```
cookies-temp/dajiale
```

### 3. 更新数据库

运行更新脚本：
```bash
cd scripts
node update-dajiale-cookie.js
```

### 4. 测试抓取

运行抓取脚本验证：
```bash
node scrape-dajiale.js
```

## 验证登录状态

如果看到以下输出，说明Cookie有效：
```
提取的数据: {
  "balance": 189.14
}
```

如果看到以下输出，说明Cookie失效：
```
提取的数据: {
  "balance": null
}
```
或者页面显示"登录显示"。

## 常见问题

### Q: 为什么Cookie会失效？

A: Cookie有过期时间，或者网站的会话管理机制要求定期重新登录。

### Q: 多久需要更新一次Cookie？

A: 取决于网站的会话有效期。如果抓取失败，通常需要重新导出Cookie。

### Q: 如何确认Cookie是否包含所有必要信息？

A: 导出的Cookie应该包含以下类型的cookie（至少）：
- session cookies
- authentication tokens  
- user identification cookies

## 当前配置

- **网站**: 大嘉乐
- **URL**: https://dajiala.com/main/interface?actnav=0
- **目标数据**: 账户余额
- **选择器**: `div.yue span:last-child`
- **数据字段**: `balance`

