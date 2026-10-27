# 个人学习笔记

- 仓库正文：[CS152 学习笔记](CS152.md)。
- Notion 正文：[CS152 学习笔记](https://app.notion.com/p/4056a691a12d814ebc07c97c6ff28576)。
- 当前摘要：[学习进度](../PROGRESS.md)。
- 同步方式：[Notion 双向同步说明](../docs/NOTION_SYNC.md)。

本轮从 L01 重新开始，当前讨论到 L02 第 25 页的取指微程序。记录“讨论过、待复述、已独立完成”等状态，保留旧报告作为历史证据。

`course/notes/` 提供 [逐讲页码导读与自检](../course/notes/lectures/README.md) 和按主题的复习说明，本目录是个人学习记录。当前自动同步只映射 `notes/CS152.md` 与上述 Notion 页面；课程导读通过笔记中的链接导航。

学习维护时，先检查两端是否有新内容，再更新个人笔记及必要的首页/进度摘要，最后运行：

```bash
python3 course/notion_sync.py sync
```

出现冲突时，先查看 `.local/notion-sync/conflicts/` 中保存的两份版本，合并后让两端内容一致，再运行同步。不要删除同步基线来强行覆盖另一端。
