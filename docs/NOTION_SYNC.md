# CS152 笔记与 Notion 双向同步

同步对象是 [notes/CS152.md](../notes/CS152.md) 与 [Notion「CS152 学习笔记」](https://app.notion.com/p/4056a691a12d814ebc07c97c6ff28576)。映射记录在 [notes/notion-sync.json](../notes/notion-sync.json)，其中只有文件路径和页面标识，不含凭据。

## 同步规则

- 只有仓库笔记变化：更新对应 Notion 页，回读核对成功后记录新基线。
- 只有 Notion 正文或标题变化：拉回对应 Markdown 文件。
- 两端都变化：保留冲突快照并停止，合并后内容相同即可接受新基线。
- 两端都没变化：不写任何笔记内容。
- 不完整页面、未知富文本或并发检测失败：停止并保留可恢复内容，不猜测转换。

同步器处理常用标题、段落、列表、复选框、粗体、行内代码、代码块、日期和仓库链接。Notion 的折叠块、复杂表格等新增富内容可能需要人工转换；相关原始内容会保存在冲突快照中。

`PROGRESS.md` 和 README 是学习摘要，由每次学习维护时同步更新；后台同步不推断新的完成状态。自动同步写入本地仓库工作区，Git 提交和推送按正常学习工作流进行。

## 当前 PC

用户级 `cs152-notion-sync.timer` 每五分钟检查一次。连接复用本机已授权的 Codex Notion MCP，不另存 Notion token，也不发送模型请求。

后台同步需要本机有正在运行、已启用 Notion MCP 的 HAPI/Codex 会话。暂时没有运行实例时会跳过，后续定时检查再重试。页面授权撤销、网络不可用或冲突时可查看日志。

```bash
systemctl --user status cs152-notion-sync.timer
systemctl --user list-timers cs152-notion-sync.timer
journalctl --user -u cs152-notion-sync.service -n 30 --no-pager
```

## 手工操作

从仓库根目录执行：

```bash
# 首次准备本地桥接依赖：
npm ci --prefix scripts/notion-sync --ignore-scripts --no-audit --no-fund

# 只检查哪一端变化：
python3 course/notion_sync.py status

# 执行安全双向同步：
python3 course/notion_sync.py sync
```

只有在一台新机器上已经配置并授权 Notion MCP、且两端正文一致时，才执行一次：

```bash
python3 course/notion_sync.py init
```

基线和锁在 `.local/notion-sync/`，不提交 Git。用共享文件锁串行化手工与定时同步；更新前再次读取相关内容，以发现同步期间的编辑。它是普通单用户笔记同步，不是 Notion 与本地文件之间的原子事务。

## 冲突处理

先停下同一笔记的编辑，查看 `.local/notion-sync/conflicts/`：

- `local.md`：当时的仓库版本。
- `notion.md`：可转换时的 Notion Markdown 版本。
- `notion.raw.md`：Notion 原始内容，包含无法自动转换的富文本。

人工合并并将结果应用到两端，再运行 `sync`。相同内容会被接受为新基线；同步器不提供默认强制覆盖方向。

## 维护与验证

```bash
python3 -m unittest discover -s course -p 'test_notion_sync.py' -v
systemctl --user disable --now cs152-notion-sync.timer  # 停用自动检查
```

用户服务启动脚本的完整路径可通过 `systemctl --user cat cs152-notion-sync.service` 查看。换电脑或移动仓库时重新设置该路径；不复制 OAuth 凭据，应在新机器上重新授权。
