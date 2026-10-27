# HW1–5 逐题覆盖与自检补缺

基于仓库内 Spring 2023 原题及四份 handout 核对。以下页码均为 **PDF 页序**，只列要求与学习连接，不提供原题解答。历史“Lecture 3/7”等引用可能沿用旧课表，以题目实际机制和下列映射为准。

## 原题具体要求

| 原题与 PDF 页 | 实际检查的知识 | 对应导读 |
|---|---|---|
| [HW1 P1A–F，2–7 页](../originals/sp23/homework/hw01.pdf#page=2) | x86、RISC-V、栈、累加器 ISA 的同一程序；静态代码字节、动态取指、数据流量；汇编优化 | L01–02 的 ISA 概念；CS61C 汇编复习 |
| [HW1 P2A–B，8–12 页](../originals/sp23/homework/hw01.pdf#page=8) | 给 MODULOM、MINV 写合法且高效的总线微程序，遵守寄存器副作用、busy 与返回 FETCH0 约束 | L02–03 |
| [HW1 P2C，13 页](../originals/sp23/homework/hw01.pdf#page=13) | 在指定微码实现上数各类指令周期，分别处理分支结果 | L02–03 |
| [HW1 P3A–E，14–16 页](../originals/sp23/homework/hw01.pdf#page=14) | 六级机提前 ALU 写回、旁路、写端口、新冒险、精确异常及两种修复方式 | L04–05 |
| [HW1 P4A–D，17–18 页](../originals/sp23/homework/hw01.pdf#page=17) | 根据编译器、逻辑与存储技术论证 CISC/RISC 取舍 | L01、L03；不是现代产品性能的绝对二选一 |
| [HW1 P5a–f，19–20 页](../originals/sp23/homework/hw01.pdf#page=19) | 性能铁律三因素如何变化；压缩指令、寄存器数、复杂指令、实现变更的条件与权衡 | L03–04 |
| [HW2 P1A–B，2–3 页](../originals/sp23/homework/hw02.pdf#page=2) | 用组件延迟算直映/四路 cache 关键路径、访问时间和 CPU 周期 | L06–07；handout #2 的电路图必读 |
| [HW2 P1C–D，4–6 页](../originals/sp23/homework/hw02.pdf#page=4) | 地址 trace；直映、四路 LRU/FIFO 状态与 miss；平均延迟及替换策略反例 | L06–07 |
| [HW2 P2A–C，7–8 页](../originals/sp23/homework/hw02.pdf#page=7) | 行主序矩阵两种循环顺序的 miss、最小容量与相联度影响 | L06–08 |
| [HW2 P3A–C，9–11 页](../originals/sp23/homework/hw02.pdf#page=9) | microtag 加速选路、完整 tag 验证、关键路径、AMAT 与同组 microtag 唯一约束 | L07–08；microtag 不等于 way prediction |
| [HW2 P4A–C，12–15 页](../originals/sp23/homework/hw02.pdf#page=12) | victim cache 电路、交换/替换 trace 与 AMAT | L08 |
| [HW2 P5，16 页；P6，17 页](../originals/sp23/homework/hw02.pdf#page=16) | 改变行大小、组数、预取、合并 I/D 后，3C 与 hit time/miss rate/miss penalty 的变化 | L06–08；必须说明工作负载与参数约束 |
| [HW3 P1A–B，2–4 页](../originals/sp23/homework/hw03.pdf#page=2) | data-in-ROB、单发射、共享写回端口、无限/四项 ROB 的重命名与逐拍调度 | L11–12 |
| [HW3 P2A–E，5–8 页](../originals/sp23/homework/hw03.pdf#page=5) | 统一物理寄存器文件、异常回滚、free list、回收、容量及双发射重命名 | L12–13 |
| [HW3 P3A–C，9–13 页](../originals/sp23/homework/hw03.pdf#page=9) | 五级机 PC+4、Decode BHT、Fetch BTB 三种方案，含错路与冲刷的时序 | L04、L15 |
| [HW3 P4A–F，14–15 页](../originals/sp23/homework/hw03.pdf#page=14) | store 提交、store→load 转发、别名、访存乱序、精确异常与地址推测失败 | L13 |
| [HW3 P5A–C，16–18 页](../originals/sp23/homework/hw03.pdf#page=16) | 饱和两位计数器，独立/共享表项导致的干扰，以及静态 hint | L15 |
| [HW4 P1A–C，2–4 页](../originals/sp23/homework/hw04.pdf#page=2) | 热路径概率、trace scheduling 对最好/最坏/平均时间的影响与资源瓶颈 | L14 |
| [HW4 P2A–D，5–14 页](../originals/sp23/homework/hw04.pdf#page=5) | 七槽 VLIW SAXPY：无优化、展开、软件流水及组合；前后序和 FLOP/cycle | L14 |
| [HW4 P3A–B，15–21 页](../originals/sp23/homework/hw04.pdf#page=15) | 32 元素向量、8/16/32 lanes、无/有 chaining 的逐拍执行与循环周期 | L17；不是 RVV ISA 编程题 |
| [HW4 P4A–D，22–23 页](../originals/sp23/homework/hw04.pdf#page=22) | 链表查找的长 load 延迟、固定/按依赖切换、线程需求、延迟与吞吐 | L16 |
| [HW4 P5A–C，24–26 页](../originals/sp23/homework/hw04.pdf#page=24) | load/FP 依赖下两种切换策略；SMT 线程数的硬件约束 | L16 |
| [HW5 P1A–D，2–3 页](../originals/sp23/homework/hw05.pdf#page=2) | SC 下三线程对同一 X 的读改写，合法最终值与局部依赖 | L22；跨地址顺序仍需另练 |
| [HW5 P2A–C，4–5 页](../originals/sp23/homework/hw05.pdf#page=4) | LdR/StC reservation 的失效、总线实现及相对 test-and-set 的优势 | L23 |
| [HW5 P3，6 页](../originals/sp23/homework/hw05.pdf#page=6) | 弱序下 seqlock 的 load/store fence 分类与最小顺序约束 | L22–23；题设汇编模型，不是可直接抄用的 C 实现 |
| [HW5 P4A–F，7–9 页](../originals/sp23/homework/hw05.pdf#page=7) | 目录协议下 1000 线程的 TAS/TTAS 初次竞争、自旋、释放的失效消息 | L21、L23 |
| [HW5 P5A–D，10–12 页](../originals/sp23/homework/hw05.pdf#page=10) | 将目录失效协议改成 update：SC 反例、状态表、silent drop、FIFO 假设 | L21–22 |
| [HW5 P6A–B，13–16 页](../originals/sp23/homework/hw05.pdf#page=13) | SUN MBus 风格五状态 snoopy 协议；最新数据位置、总线事务、owner intervention | L21；不能照搬 MSI 状态表 |

## 手册怎样配合

- [HW1 handout #1](../originals/sp23/handouts/hw01-handout.pdf)：1–6、8–9 页给总线机及微分支；7 页另含五级流水线图。取指表把 IR 读取/等待放在 PC 更新之前，**不与 L02 略图逐行等同**。控制与周期按所选模型核对。
- [HW2 handout #2](../originals/sp23/handouts/hw02-handout.pdf)：1 页直映、2 页四路电路，求关键路径应按并行路径和汇合点计算。
- [HW5 handout #6](../originals/sp23/handouts/hw05-handout.pdf)：目录协议；1 页假设/状态/消息，2–3 页 cache 与 home 状态表。
- [HW5 handout #7](../originals/sp23/handouts/hw05-handout2.pdf)：**MBus snoopy 五状态 I/CE/OE/CS/OS**，不是 MSI。读到 owned shared 时，内存可以是旧值，owner 保存最新数据。

## 哪些讲需要用自检补足

“直接”指原题确实要求该机制，不表示穷尽整讲。“部分”指主机制练过、仍有明显空缺；“无专题”不等于不重要。

| 导读 | HW 覆盖 | 自检重点补什么 |
|---|---|---|
| [L01](../notes/lectures/L01.md) | 部分：HW1 P1、P4 | ISA 与实现兼容；历史案例不靠背年代 |
| [L02](../notes/lectures/L02.md)、[L03](../notes/lectures/L03.md) | 直接：HW1 P2；P4/P5 部分相关 | 从伪码到控制、总线合法性、ROM 编码成本 |
| [L04](../notes/lectures/L04.md)、[L05](../notes/lectures/L05.md) | 直接/部分：HW1 P3/P5，HW3 P1/P3 | 首末指令计时、延迟/启动间隔、调度与解耦 |
| [L06](../notes/lectures/L06.md)、[L07](../notes/lectures/L07.md) | 直接/部分：HW2 P1–3/P5–6 | DRAM 行行为、写缓冲、多级 local/global rate |
| [L08](../notes/lectures/L08.md) | 部分：HW2 P2/P4，P5–6 定性预取 | 非阻塞、预取准确性/及时性/污染、tiling |
| [L09](../notes/lectures/L09.md)、[L10](../notes/lectures/L10.md) | 无专题 | 页表访问、TLB reach、异常分流、VIPT、别名 |
| [L11](../notes/lectures/L11.md)、[L12](../notes/lectures/L12.md) | 直接：HW3 P1–2 | 简化记分牌前提；完成、提交、回收的区别 |
| [L13](../notes/lectures/L13.md) | 直接：HW3 P2E/P4 | 同拍 RAW 转发、内存重叠范围与恢复 |
| [L14](../notes/lectures/L14.md) | 直接：HW4 P1–2 | 小循环启动成本、错路径副作用与变延迟 |
| [L15](../notes/lectures/L15.md) | 部分：HW3 P3/P5 | 历史相关、RAS、恢复、取指带宽；不必先实现大预测器 |
| [L16](../notes/lectures/L16.md) | 直接：HW4 P4–5 | SMT 吞吐、单线程延迟、公平性及共享竞争 |
| [L17](../notes/lectures/L17.md) | 部分：HW4 P3 | bank 冲突、mask/reduction、scatter 地址重复 |
| [L18](../notes/lectures/L18.md) | 无 GPU 专题 | warp/block/lane、分歧、合并访存与驻留资源 |
| [L19](../notes/lectures/L19.md) | 无 RVV ISA 专题 | 实际 VL、LMUL、尾部/掩码、混合宽度；由现代 Lab4 检验 |
| [虚拟化补课](../notes/lectures/L20-supplement.md) | 无专题 | ABI、翻译、guest/host 映射与精确状态 |
| [L21](../notes/lectures/L21.md) | 直接：HW5 P4–6 | MSI/MESI 与 MBus 模型区分；伪共享另练 |
| [L22](../notes/lectures/L22.md) | 直接/部分：HW5 P1/P3/P5A/D | 跨地址 SC/TSO、MCA、语言与 ISA 层次 |
| [L23](../notes/lectures/L23.md) | 直接/部分：HW5 P2/P4 | aq/rl、原子性与顺序、ABA、进度保证 |
| [L24](../notes/lectures/L24.md)、[L25](../notes/lectures/L25.md) | 无专题 | PUE/TCO/故障域；拓扑、流控、死锁与饱和 |
| [L26](../notes/lectures/L26.md) | 五份作业提供素材，无新专题 | 跨章节诊断、实验论断的证据边界 |

因此，基础自检以短题为主；没有专门作业的章节增加了独立的数值、反例与设计题，放在**实践后选做**，无需全部前置。

## 原题中的文字与参数陷阱

- HW1 P2A 标题仍写 SUBLEQ，正文实际要求 MODULOM；P2B 标题写 Character Count，正文实际要求 MINV。以正文语义和副作用约束为准。MODULOM 所附重复减法遇除数 0 不终止，分析时应明确输入前提。
- HW2 P4B 虽写“word-addressable”，但地址拆分图明确含低 2 位 byte select，已填示例也按**字节地址、访问字对齐**解释才一致。按图核对单位，不把表中地址再乘 4；其 victim cache 的行大小和容量也重新给定。
- HW2 P4C 同时写“15% of memory accesses”由 victim cache 解决和 L1 miss rate 为 10%；若分母都为全部访问，两者矛盾。先写明问题并声明采用的条件解释，不悄悄代换百分比。
- HW3 P1 把可写整数寄存器写成 `x1-x32`；RISC-V 实际为 `x1-x31`，x0 固定为 0。求该题调度仍以原题给定的资源、延迟和写回规则为准。
- HW4 有教学伪指令和旧向量记号；不能直接交给当前 RISC-V/RVV 汇编器。HW5 的 fence、原子伪代码也先按题设推演，落地 C/C++ 需遵守语言内存模型。

回到 [逐讲导读](../notes/lectures/README.md) 或 [作业入口](README.md)。
