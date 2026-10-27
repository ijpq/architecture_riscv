# 一学期学习路线

这是自学顺序，不是 2023 年的官方课表或截止日期。每次学习都留下自己的推导、实验记录和未解问题。参考 [作业入口](assignments/README.md)、[实验入口](labs/README.md) 和 [报告模板](assignments/report-template.md)。

## 每个学习单元怎样完成

1. 从 [逐讲详细导读](notes/lectures/README.md) 找重点页和掌握标准，浏览框架，再对照原图走通一个小例子；[概念导读](notes/README.md) 用作阶段复习。
2. 做三道短基础自检后，按 [HW 逐题覆盖表](assignments/coverage.md) 开始对应小问。选做迁移题在实践后按缺口补，不作为所有实验的前置；不要先搜索原题答案。
3. 需要实验时，先运行未修改的基线，再修改一处、重新构建、比较结果。
4. 报告必须同时记录配置、输入、正确性和性能指标，解释一个反例。

## 按原讲次逐项覆盖

| 原讲次 | 本地原件 / 替代材料 | 核心学习目标 | 建议实践 |
|---|---|---|---|
| [L01 导读](notes/lectures/L01.md) | [Intro](originals/sp23/lectures/L01-Intro.pdf) | 课程/技术/历史背景；ISA 抽象与兼容产品族 | 三层关系图；HW1 P1/P4 的概念准备 |
| [L02 导读](notes/lectures/L02.md) | [Simple implementations](originals/sp23/lectures/L02-SimpleImps.pdf) | 单总线微码 RISC-V、控制信号与 IF/ALU/LW | 逐步记 PC/MA/A/IR；读 HW1 handout |
| [L03 导读](notes/lectures/L03.md) | [Microcoding / control store](originals/sp23/lectures/L03-Microcoding-Pipelining.pdf) | ROM 编码、微程序组织与 RISC 取舍 | HW1 P2/P4；标准流水线从 L04 开始 |
| [L04 导读](notes/lectures/L04.md) | [Pipelining](originals/sp23/lectures/L04-Pipelining.pdf) | 性能铁律、冒险、旁路、控制流与精确异常 | HW1 P3/P5；Lab1 |
| [L05 导读](notes/lectures/L05.md) | [Pipelining II](originals/sp23/lectures/L05-PipeliningII.pdf) | 深流水线、循环调度、解耦、复杂单元与 scoreboard | Lab1 对照；HW3 P1 前置 |
| [L06 导读](notes/lectures/L06.md) | [Memory](originals/sp23/lectures/L06-Memory.pdf) | DRAM、局部性、cache 放置与地址分解 | HW2 P1；Lab2 基线 |
| [L07 导读](notes/lectures/L07.md) | [Memory II](originals/sp23/lectures/L07-MemoryII.pdf) | 替换、AMAT/3C、写策略、多级统计与包含关系 | HW2 P1–3/P5–6；Lab2 |
| [L08 导读](notes/lectures/L08.md) | [Memory III](originals/sp23/lectures/L08-MemoryIII-Guest_lecture.pdf) | VC、way prediction、非阻塞、预取、循环变换 | HW2 P2/P4；Lab2 转置/预取 |
| [L09 导读](notes/lectures/L09.md) | [Address translation](originals/sp23/lectures/L09-AddressTranslation.pdf) | base/bound、分页、页表、TLB 与 refill | 无专门 HW；地址数值自检与流程图 |
| [L10 导读](notes/lectures/L10.md) | [Virtual memory](originals/sp23/lectures/L10-VirtualMemory.pdf) | 异常、ASID、VIVT/VIPT 与别名 | 无专门 HW；算 VIPT 约束 |
| [L11 导读](notes/lectures/L11.md) | [Complex pipelines](originals/sp23/lectures/L11-ComplexPipes.pdf) | 简化 scoreboard、乱序限制、重命名与提交动机 | HW3 P1 前置；Lab2 乱序基线 |
| [L12 导读](notes/lectures/L12.md) | [Out-of-order](originals/sp23/lectures/L12-OutOfOrder.pdf) | data-in-ROB、统一 PRF、回收与恢复 | HW3 P1/P2A–D |
| [L13 导读](notes/lectures/L13.md) | [Out-of-order II](originals/sp23/lectures/L13-OutOfOrderII.pdf) | 同拍重命名、LSQ、store 转发与地址推测 | HW3 P2E/P4 |
| [L14 导读](notes/lectures/L14.md) | [VLIW](originals/sp23/lectures/L14-VLIW.pdf) | 展开、软件流水、trace scheduling、静态调度局限 | HW4 P1–2 |
| [L15 导读](notes/lectures/L15.md) | [Branch prediction](originals/sp23/lectures/L15-BranchPredictor-Guest_lecture.pdf) | BHT/BTB、相关历史、RAS、恢复与取指 | HW3 P3/P5；Lab3 |
| [L16 导读](notes/lectures/L16.md) | [Multithreading](originals/sp23/lectures/L16-Multithread.pdf) | 交错/事件切换、SMT、吞吐与资源竞争 | HW4 P4–5 |
| [L17 导读](notes/lectures/L17.md) | [Vectors](originals/sp23/lectures/L17-Vectors.pdf) | lanes、startup、chaining、bank、向量化依赖 | HW4 P3；Lab4 模型阅读 |
| [L18 导读](notes/lectures/L18.md) | [GPU](originals/sp23/lectures/L18-GPU.pdf) | SIMT、warp/block、合并访存与分歧 | 无 GPU HW；小 warp 纸面自检 |
| [L19 导读](notes/lectures/L19.md) | [RISC-V vectors](originals/sp23/lectures/L19-RISCV-Vectors.pdf) | RVV 1.0 实际 VL、类型、分组、mask/tail 与混合宽度 | 现代 Lab4；HW4 不直接检查这些 ISA 语义 |
| [L20 槽位补课](notes/lectures/L20-supplement.md) | [系统衔接](notes/20-local-bridge.md)；[2021 虚拟机原件](originals/supplementary/sp21-L22-VirtualMachines.pdf) | ABI、解释/翻译、system VM 与两层地址映射 | 短自检；不声称是原 L20 |
| [L21 导读](notes/lectures/L21.md) | [Coherence](originals/sp23/lectures/L21-Coherence.pdf) | MSI/MESI、伪共享、目录与在途消息 | HW5 P4–6；MBus 手册另按五状态推；Lab5 |
| [L22 导读](notes/lectures/L22.md) | [Memory consistency models](originals/sp23/lectures/L22-MCM.pdf) | SC/TSO、写缓冲、fence、MCA 与语言模型 | HW5 P1/P3/P5A/D；跨地址 litmus 自检 |
| [L23 导读](notes/lectures/L23.md) | [Synchronization](originals/sp23/lectures/L23-Synch.pdf) | 原子性、aq/rl、CAS、LR/SC、进度与锁成本 | HW5 P2/P4；Lab5 同步 |
| [L24 导读](notes/lectures/L24.md) | [Warehouse-scale computers](originals/sp23/lectures/L24-WSCs-CS152-CS252-2023-Guest_lecture.pdf) | 设施/服务器效率、TCO、故障域与 FireSim；尾延迟另补 | 无专门 HW；PUE/故障率/建模自检 |
| [L25 导读](notes/lectures/L25.md) | [Interconnects](originals/sp23/lectures/L25-Interconnects.pdf) | 拓扑、流控、VC、路由、死锁、拥塞与 QoS | 无专门 HW；小网络纸面推演 |
| [L26 导读](notes/lectures/L26.md) | [Summary](originals/sp23/lectures/L26-Summary.pdf) | 跨层视角、综合诊断与后续方向 | 错题回查、无答案试卷与性能报告 |

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
