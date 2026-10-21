# CS152 仓库导航

**日常只需要打开 [ijpq/architecture_riscv](https://github.com/ijpq/architecture_riscv) 的 `main` 分支。**

从 [学习进度](../PROGRESS.md) 继续上次的任务，再进入 [课程资料](../course/README.md)。讲义、作业、实验指南和个人报告都从主仓库导航，平时不用在多个源码仓库之间寻找进度。

## 每个仓库做什么

| 仓库 | 用途 | 日常是否需要打开 |
|---|---|---|
| [architecture_riscv](https://github.com/ijpq/architecture_riscv) | 主学习仓库：进度、课程导航、个人报告、本地工具与源码快照 | **需要，固定入口** |
| [chipyard-cs152-sp23](https://github.com/ijpq/chipyard-cs152-sp23) | 原 Lab1 的课程 Chipyard；`lab1` 分支保存个人修改 | 维护或追溯底层源码时 |
| [riscv-sodor](https://github.com/ijpq/riscv-sodor) | Lab1 的 Sodor 核心与个人 trace 统计修改，是课程 Chipyard 的依赖 | 单独开发核心时 |
| [public-chipyard](https://github.com/ijpq/public-chipyard) | 早期通用 Chipyard 环境来源；主仓库历史子模块仍引用它 | 回查旧环境时 |
| [ucb_sp20_cs152_lab](https://github.com/ijpq/ucb_sp20_cs152_lab) | 2020 年课程的旧 fork；核查时与上游一致，当前学习路线没有引用 | 历史参考，可另行备份清理 |

本次整理没有删除或归档上述仓库。仓库保留的用途与“个人已经完成哪些实验”分别记录。

## 旧名字不是另一份仓库

GitHub 会将以下旧地址跳转到现名：

| 旧名字 | 当前名字 |
|---|---|
| `MyCS152` | `architecture_riscv` |
| `mychipyard` | `public-chipyard` |
| `mycs152-chipyard` | `chipyard-cs152-sp23` |

因此按这些名字搜索时，不要把旧地址再算作一份独立学习项目。当前主仓库的本地 `origin` 也使用现名。

## 分支怎样选择

- **`main`**：日常浏览、记录学习进度和后续学习提交。
- **`learn/cs152-complete`**：保留本次完整课程整理的版本，供回查和恢复。首次同步时与 `main` 内容相同；以后日常记录继续放在 `main`。
- **其他源码仓库的 `lab1` 等分支**：保存底层实验修改，不作为学习进度首页。

## 换电脑学习

先克隆主仓库，再按 [源码恢复说明](../course/SOURCES.md) 恢复必要实验目录。恢复器使用主仓库里的六个源码快照，不要求递归拉取顶层历史子模块。

源码快照含必要源码及钉定版本，不含所有开发历史、工具链安装目录和构建缓存。若今后要删除独立源码仓库，应另行保存其完整历史并处理旧引用。
