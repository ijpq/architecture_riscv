# 一学期学习路线

这是自学顺序，不是 2023 年的官方课表或截止日期。每次学习都留下自己的推导、实验记录和未解问题。参考 [作业入口](assignments/README.md)、[实验入口](labs/README.md) 和 [报告模板](assignments/report-template.md)。

## 每个学习单元怎样完成

1. 先读下面对应的原讲义，再用 [中文概念导读](notes/README.md) 复述核心机制。
2. 独立做笔算、自测和作业；不要先搜索答案。
3. 需要实验时，先运行未修改的基线，再修改一处、重新构建、比较结果。
4. 报告必须同时记录配置、输入、正确性和性能指标，解释一个反例。

## 按原讲次逐项覆盖

| 原讲次 | 本地原件 / 替代材料 | 核心学习目标 | 建议实践 |
|---|---|---|---|
| L01 | [Intro](originals/sp23/lectures/L01-Intro.pdf) | 课程介绍、技术与历史背景；ISA 抽象和兼容产品族 | 区分 ISA 与微架构；性能公式作为补充复习 |
| L02 | [Simple implementations](originals/sp23/lectures/L02-SimpleImps.pdf) | ISA 契约、控制与数据通路、单总线微码 RISC-V | 画出 MA:=PC 与取指步骤的数据流和控制信号 |
| L03 | [Microcoding / pipelining](originals/sp23/lectures/L03-Microcoding-Pipelining.pdf) | 微码 ROM、控制存储编码、微程序组织与 RISC 设计取舍 | HW1 微码相关题；标准流水线从 L04 继续 |
| L04 | [Pipelining](originals/sp23/lectures/L04-Pipelining.pdf) | 数据相关、停顿与旁路 | HW1、Lab1 |
| L05 | [Pipelining II](originals/sp23/lectures/L05-PipeliningII.pdf) | 控制冒险、吞吐量与延迟 | HW1、Lab1 |
| L06 | [Memory](originals/sp23/lectures/L06-Memory.pdf) | 局部性、cache 结构与 AMAT | HW2、Lab2 open1 |
| L07 | [Memory II](originals/sp23/lectures/L07-MemoryII.pdf) | 写策略、缺失与存储层次 | HW2、Lab2 |
| L08 | [Memory III](originals/sp23/lectures/L08-MemoryIII-Guest_lecture.pdf) | 存储器实现的成本与瓶颈 | HW2，分开带宽与延迟 |
| L09 | [Address translation](originals/sp23/lectures/L09-AddressTranslation.pdf) | VA→PA、页表与 TLB | 画一次带缺失的地址访问 |
| L10 | [Virtual memory](originals/sp23/lectures/L10-VirtualMemory.pdf) | 保护、异常与地址空间 | 区分 cache miss / TLB miss / page fault |
| L11 | [Complex pipelines](originals/sp23/lectures/L11-ComplexPipes.pdf) | 多周期功能单元与相关 | HW3、Lab2 open2 |
| L12 | [Out-of-order](originals/sp23/lectures/L12-OutOfOrder.pdf) | 调度、重命名与精确状态 | HW3、Lab2 |
| L13 | [Out-of-order II](originals/sp23/lectures/L13-OutOfOrderII.pdf) | 推测、提交与访存次序 | HW3、Lab3 |
| L14 | [VLIW](originals/sp23/lectures/L14-VLIW.pdf) | 静态调度、软件流水与资源冲突 | HW4 |
| L15 | [Branch prediction](originals/sp23/lectures/L15-BranchPredictor-Guest_lecture.pdf) | 方向预测、目标预测与错误恢复 | HW3、Lab3 |
| L16 | [Multithreading](originals/sp23/lectures/L16-Multithread.pdf) | 线程如何隐藏停顿；SMT 资源竞争 | HW4 |
| L17 | [Vectors](originals/sp23/lectures/L17-Vectors.pdf) | 向量化、strip mining 与依赖 | HW4、Lab4-modern |
| L18 | [GPU](originals/sp23/lectures/L18-GPU.pdf) | SIMT、分歧与线程级并行 | HW4，比较 CPU / vector / GPU |
| L19 | [RISC-V vectors](originals/sp23/lectures/L19-RISCV-Vectors.pdf) | VL、SEW、LMUL 与可伸缩向量 | Lab4-modern；区分旧 RVV 与 RVV 1.0 |
| L20 槽位 | [本地补课](notes/20-local-bridge.md)；[2021 虚拟机讲义](originals/supplementary/sp21-L22-VirtualMachines.pdf) | 补上向量到多核的衔接和虚拟化复习 | 完成本地补课的自测；不声称是原 L20 |
| L21 | [Coherence](originals/sp23/lectures/L21-Coherence.pdf) | 单地址的一致性；snoopy / directory | HW5、Lab5 |
| L22 | [Memory consistency models](originals/sp23/lectures/L22-MCM.pdf) | 跨地址的可见顺序与合法执行 | HW5，独立分析 litmus test |
| L23 | [Synchronization](originals/sp23/lectures/L23-Synch.pdf) | 原子操作、锁与同步成本 | HW5、Lab5 |
| L24 | [Warehouse-scale computers](originals/sp23/lectures/L24-WSCs-CS152-CS252-2023-Guest_lecture.pdf) | 从处理器到数据中心的性能、能耗与尾延迟 | 写出单核指标不能回答的问题 |
| L25 | [Interconnects](originals/sp23/lectures/L25-Interconnects.pdf) | 拓扑、路由、带宽与竞争 | 关联多核通信和 Lab5 扩展性 |
| L26 | [Summary](originals/sp23/lectures/L26-Summary.pdf) | 把各机制连成一张性能 / 正确性地图 | 自测、discussion 与无答案试卷 |

原镜像缺 L20 与 discussion05；没有猜测原 L20 的标题。上表保证学习槽位有入口，不宣称找回了缺失原件。

## 约 14–16 周的安排

- **1–3 周**：L01–L05，HW1，Lab1。能手算依赖，能从 trace 找到停顿。
- **4–5 周**：L06–L10，HW2，Lab2 open1。能解释访问模式、缺失率与周期数之间的联系。
- **6–8 周**：L11–L13、L15，HW3，Lab2 open2 与 Lab3。能区分重命名、调度、提交与恢复。
- **9–11 周**：L14、L16–L19，HW4，Lab4-modern。先运行标量和课程向量示例，再自己写其余向量练习。
- **12–13 周**：本地补课、L21–L23，HW5，Lab5。先保证结果正确，再分析同步与内存竞争。
- **14–16 周**：L24–L26、discussion 复习、期中 / 期末自测。把弱项回填到自己的笔记。

每周约 8–12 小时只是安排建议，不是完成承诺。Lab3、向量汇编与 Lab5 可以多留一周。不要为了赶进度省略基线、重新构建或正确性检查。

## 完课标准

- [ ] 能独立解释原讲义覆盖的主要机制，并完成缺失材料的本地补课。
- [ ] HW1–HW5 都有自己的推导和未解问题清单。
- [ ] Lab1、Lab2、Lab3、Lab5 有自己的配置 / 修改 / 正确性 / 性能报告。
- [ ] Lab4-modern 的练习由自己完成；报告明确它不是原版 RVV 0.10 的复刻。
- [ ] 能解释现代 Lab4 不能回答哪些原实验问题，而不是把模型参数名称当成硬件等价证明。
- [ ] 使用无答案试卷做一次限时自测，并把错误追溯到机制，不只记最终答案。

工具验收通过不等于完成课程，更不代表学生练习已经写好。
