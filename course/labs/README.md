# 五个实验的本地学习入口

先阅读 [环境说明](../../docs/LOCAL_ENVIRONMENT.md)。资料以 Spring 2023 为基线，能运行的源码跨年份，因此下面逐项解释映射。不要在顶层执行 `git submodule update --init --recursive`：顶层历史 Gitlinks 不是这份学习分支的安装入口。

| 实验 | 原题 | 本地课 | 源码/替代路线 | 学习前置 |
|---|---|---|---|---|
| Lab1 | [sp23 PDF](../originals/sp23/labs/lab1.pdf) | [流水线](lab1.md) | `chipyard-cs152-sp23`，Sodor 1/3/5 级 | L01–L05，HW1 |
| Lab2 | [sp23 PDF](../originals/sp23/labs/lab2.pdf) | [缓存、Mystery、预取](lab2.md) | 2022 课程缓存环境 | L06–L10，HW2 |
| Lab3 | [sp23 PDF](../originals/sp23/labs/lab3.pdf) | [BOOM、预测与 Spectre](lab3.md) | 2022 课程 BOOM | L11–L16，HW3 |
| Lab4 | [sp23 PDF](../originals/sp23/labs/lab4.pdf) | [现代向量实验](lab4.md) | **独立 RVV 1.0/gem5 替代** | L14、L17–L19，HW4 |
| Lab5 | [sp23 PDF](../originals/sp23/labs/lab5.pdf) | [多核一致性](lab5.md) | 2021/2022 MESI/MSI/MI | L21–L23，HW5 |

当前机器已通过 **32/32 环境检查**（21 RTL + 11 现代 Lab4）。这只证明代表性基准、配置和接口可用，不表示你的作业、所有输入或所有配置组合都完成。换到新检出后没有构建物和运行证据，需要按 [分支恢复说明](../SOURCES.md) 准备、构建和重跑。

## 学习循环

1. 看原讲义和本地导读，先写下预测。
2. 做相关书面题；不确定时明确列出题目模型假设。
3. 从提供的最小基准开始，确认构建、正确性和统计口径。
4. 每次只做一项自己的改动，重编后比较同输入/同模型。
5. 保存源码差异、命令和独立日志，用 [报告模板](../assignments/report-template.md) 解释结果。

本分支不提供学生答案、Mystery 参数、Spectre 攻击实现或官方评分器。现代 Lab4 六组向量 TODO 未填写；Lab5 用户原有优化文件保留，不据此声称它们已正确。
