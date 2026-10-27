# CS152 学习进度

日常入口：[architecture_riscv 的 main 分支](https://github.com/ijpq/architecture_riscv/tree/main)。本页记录自己学到哪里，课程资料和实验环境分别见 [学习路线](course/ROADMAP.md) 与 [环境指南](docs/LOCAL_ENVIRONMENT.md)。

学习记录更新日期：2026-10-28。讲解过的内容与独立完成的练习分别记录。

完整笔记：[仓库正文](notes/CS152.md)、[Notion 页面](https://app.notion.com/p/4056a691a12d814ebc07c97c6ff28576)。个人笔记双向同步；本页是上述日期的学习摘要，维护时根据新笔记更新，规则见 [同步说明](docs/NOTION_SYNC.md)。

## 下次从这里继续

**当前实践：HW1 第一题 1.A–1.C 已自己尝试并讨论，正在订正 1.C 的字节数与动态访存统计。讲义位置仍登记为 L02 第 25 页。**

1. 对照 [本轮学习笔记](notes/CS152.md) 的 HW1 记录，自己订正 1.A–1.C 草稿；已有反馈不等于已经独立复算。
2. 1.C 补齐 done 标签，保持循环入口 `[x,n]`；复算静态 34 B、动态取指 149 B、数据读/写 84/44 B，再独立开始 1.D。
3. 回到讲义时用 [L02 导读](course/notes/lectures/L02.md) 复述 IF，再继续 ALU/LW。整份 HW1 和本轮 Lab1 均未标为完成。

旧的 [2025-07-23 Lab1 记录](https://github.com/ijpq/architecture_riscv/commit/b53fcf75716d0f7fa31d2f6910edc8b7b3515d2d) 和 [个人报告](lab1.report.md) 保留作历史学习证据，不作为本轮完成情况，也未重新验收整份报告。

## 课程进度

“未登记”表示当前没有在这里确认完成情况，不能据此判断以前是否学过。只有自己完成并留下推导、代码或报告后，才标为“完成”。

| 项目 | 当前记录 | 资料与成果 |
|---|---|---|
| L01 | 已讨论课程背景、ISA/微架构与 IBM 360；未作逐页验收 | [本轮笔记](notes/CS152.md) |
| L02 | 学习中，到第 25 页取指；控制信号待独立复述 | [本轮笔记](notes/CS152.md) |
| L03–L26 与缺失材料补课 | 本轮进度未登记 | [逐讲路线](course/ROADMAP.md)、[中文导读](course/notes/README.md) |
| HW1 | 进行中：第一题 1.A–1.C 已尝试并讨论；1.C 栈逻辑核对通过，统计与草稿订正待复算；1.D 未登记开始 | [本轮作业笔记](notes/CS152.md)、[原题与手册](course/assignments/README.md) |
| HW2 | 未登记 | [原题与手册](course/assignments/README.md) |
| HW3 | 未登记 | [原题与手册](course/assignments/README.md) |
| HW4 | 未登记 | [原题与手册](course/assignments/README.md) |
| HW5 | 未登记 | [原题与手册](course/assignments/README.md) |
| Lab1 | 本轮未重做；旧报告记录到第二轮 §3.7 | [个人报告](lab1.report.md)、[实验指南](course/labs/lab1.md) |
| Lab2 | 完成情况未登记 | [实验指南](course/labs/lab2.md) |
| Lab3 | 完成情况未登记 | [实验指南](course/labs/lab3.md) |
| Lab4-modern | 完成情况未登记；采用 RVV 1.0/gem5 | [实验指南](course/labs/lab4.md) |
| Lab5 | 完成情况未登记；保留已有个人代码 | [实验指南](course/labs/lab5.md) |

## 每次学习后更新

在上表更新当前小节和成果链接，再在下表追加一行。日常把记录提交到主仓库的 `main` 分支；其他源码仓库的用途见 [仓库导航](docs/REPOSITORIES.md)。

| 日期 | 学习项目 | 本次留下的成果 | 下次继续的位置 |
|---|---|---|---|
| 2025-07-23 | Lab1 第二轮，§3.4–§3.7 | [已有报告与测量记录](lab1.report.md) | 复核 §3.7 的推导和后续实验要求 |
| 2026-10-26 | 从头重学，L01 与 L02 到第 25 页 IF | [ISA、微架构、微码与取指笔记](notes/CS152.md) | 独立复述 MA/A/PC 与控制信号，再继续取指和 ALU 微程序 |
| 2026-10-27 | 讨论学习方法，技术位置仍为 L02 第 25 页 | [先建立框架、最小推演、练习检验与回查的方法](notes/CS152.md) | 手推一次取指，再继续 ALU/LW；将缺失的实现前提单独标记 |
| 2026-10-27 | 补充学习导航，技术位置不变 | [逐讲重点页与分层自检](course/notes/lectures/README.md)、[HW 逐题覆盖](course/assignments/coverage.md) | 使用 L02 三道基础检查后进入相应微码练习，选做题按薄弱项补 |
| 2026-10-28 | HW1 第一题 1.A–1.C：立即数/访存、test/ZF、指令长度/标签、栈不变量和动态计数 | [讨论与核对笔记](notes/CS152.md)；已修复 1.C 回环前缺少 n 的问题，其他订正仍待回填 | 自己订正、复算 1.A–1.C 后开始 1.D；不自动推进讲义页码 |

可把后续笔记放到 `work/hw01/`、`work/lab01/` 等目录，并从这里链接到实际文件。没有记录的题目保持“未登记”，不要仅根据环境通过就勾选完成。

## 环境准备记录

2026-10-21 的环境核查：21 项原课程 RTL 与 11 项现代 Lab4 检查通过；课程及工具测试共 66 项通过，六个源码快照校验通过。详见 [验收记录](specs/verifications/COURSE_BRANCH_VERIFY.md)。

这些是环境与工具的结果。Lab4-modern 使用 RVV 1.0/gem5，原版 RVV 0.10 的 DLEN/chaining 定量题仍有限制；学生练习的完成情况以上面的个人记录为准。
