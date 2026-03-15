# cjmb

财经慢报（Financial Express）频道内容展示项目原型。

## 当前能力
- 抓取 Telegram 公开频道页
- 提取最近消息为结构化 JSON
- 生成静态 HTML 页面
- 可通过 GitHub Actions 定时更新

## 本地使用
```bash
npm run update
```

## 数据来源
- `https://t.me/s/Financial_Express`

## 输出
- `data/messages.json`
- `docs/index.html`
