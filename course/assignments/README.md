# 作业：原题、配套手册与本地做法

以下保留 Spring 2023 题目，不提供答案。历史截止日期和提交系统不再使用；题目中的机器假设仍是解题规则。建议在每章学完后先独立完成相应题目，再用讨论题和试卷查漏。

按具体题号开始请看 **[逐题覆盖表与原题核对](coverage.md)**；每讲读完先做 [逐讲导读](../notes/lectures/README.md) 中的三道基础自检，再尝试对应小问。选做补缺题安排在实践后，不必把整套导读读完才开始 HW1。

| 作业 | 主题 | 必需配套资料 | 建议开始点 |
|---|---|---|---|
| [HW1](../originals/sp23/homework/hw01.pdf) | ISA 比较、微码、6 级流水线、性能公式 | [总线式 RISC-V 手册](../originals/sp23/handouts/hw01-handout.pdf) | L01–L05 后；按题目的 datapath、编码和计时规则推演 |
| [HW2](../originals/sp23/homework/hw02.pdf) | cache 访问时间、循环次序、microtag、victim cache、3C 与层次性能 | [缓存实现手册](../originals/sp23/handouts/hw02-handout.pdf) | L06–L08 后；地址单位和题目参数优先 |
| [HW3](../originals/sp23/homework/hw03.pdf) | 乱序调度、物理寄存器、分支预测、访存推测 | 原题中的参数和模型说明 | L11–L15 后分段完成，不跳过就绪和恢复时序 |
| [HW4](../originals/sp23/homework/hw04.pdf) | trace scheduling、VLIW、向量、多线程 | 原题的功能单元、lane/chaining 假设 | L14、L16–L19 后；纸面旧模型与现代 Lab4 分开 |
| [HW5](../originals/sp23/homework/hw05.pdf) | 一致性、内存顺序、原子操作与锁性能 | [目录协议手册](../originals/sp23/handouts/hw05-handout.pdf)、[MBus 五状态 snoopy 手册](../originals/sp23/handouts/hw05-handout2.pdf) | L21–L23 后；按每题协议推状态，不能把 MBus 状态表替换成 MSI |

这是主题层面的映射，不把后期源码配置或本地测量结果当成作业标准答案。遇到原题与本地工具不一致时，书面题按原题建模，实验报告按实际运行模型记录，两种结果不混用。

## 自己保存什么

可以在 `work/` 下按 `hw01`、`lab01` 建自己的目录；不要直接改原始 PDF。每道题保留：题号、采用的假设、推导、单位、自查过程和仍不理解的部分。学校成绩或自动评分不在本分支内，本地没有官方评分器。

- [文本自测题](self-checks.md)：本地补充，不冒充官方题。
- [报告模板](report-template.md)：可复制填写。
- [讨论题和考试原件索引](../originals/README.md)：只收题目，不含解答；disc13 为扫描版。

## 两次阶段检查

1. 流水线与内存部分结束后，用第一份期中题闭卷检查，并把错误分类为概念、模型假设或计算错误。
2. 乱序和向量部分后，再做第二份期中题；最后做期末题。考试是练习素材，不代表当前学期的考试范围或评分要求。
