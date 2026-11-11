# CS152 学习进度

日常入口：[architecture_riscv 的 main 分支](https://github.com/ijpq/architecture_riscv/tree/main)。本页记录自己学到哪里，课程资料和实验环境分别见 [学习路线](course/ROADMAP.md) 与 [环境指南](docs/LOCAL_ENVIRONMENT.md)。

学习记录更新日期：2026-11-11。最近技术讨论到 2026-11-10 的 HW1 P5.f；本次核对进度分类与发布状态。讲解过的内容与独立完成的练习分别记录。

完整笔记：[Notion 页面](https://app.notion.com/p/4056a691a12d814ebc07c97c6ff28576)。个人笔记以 Notion 为准，仓库缓存已在回读核对后移除；本页保留学习摘要与链接，规则见[维护说明](docs/NOTION_SYNC.md)。

## 下次从这里继续

**当前实践：已讨论 HW1 3.B 的 WAW、3.C 精确异常、3.D interlock、3.E 旧值恢复，以及 P4 A–D、P5 a–f。3.A/3.D/3.E 英文答案由助手根据讨论整理，不记为独立完成；3.B、P4/P5 的正式草稿仍需回填订正。Notion 已记录个人误解、正确质疑与助手更正。2.C 的 µBr/周期表、2.B 优化与寄存器重合仍待完成。本次笔记记录没有新增模型或 RTL 测试。**

1. 对照[异常与流水线纠错](https://app.notion.com/p/40e6a691a12d8185afc9d2f4f28d7601)订正 3.B 的 WAW 解释；对照[HW1 P4–5 性能推理](https://app.notion.com/p/4146a691a12d81a1bd2ec57b03801878)整理 P4/P5，逐项注明 IC、CPI、SPC 的实现假设。5.f 采用“原实现为非流水化单总线”的假设分析，不能写成题干已知条件。前次 BEQ 长讲解仍未确认读完。
2. 2.C 已确认 AUIPC 删除多余 A−4、BEQ 拆分 PC−4、JAL 改用 ImmJ、JALR 直接复制 B。接着逐行补 µBr，确认 J 是否保留写 x0 的状态；明确统计自拟微程序还是参考源码，独立数拍后再填写仍空白的周期表。
3. 对照[学习笔记](https://app.notion.com/p/4056a691a12d814ebc07c97c6ff28576)、[MODULOM 副本](work/hw01/modulom-reviewed.md)与[MINV 测试说明](work/hw01/MINV.md)，自行整理正式答案；2.B 仍需检查重复读取首元素、寄存器重合等问题，1.A–1.F 旧稿仍需订正。
4. 模型通过不等于独立掌握或真实 RTL 验证。可先预测 17%5、MINV `[7,3,9]` 再对照 trace；Pure ROM 的 Cond/Busy 完整采样时序仍待研究，整份 HW1 和本轮 Lab1 均未标为完成。

旧的 [2025-07-23 Lab1 记录](https://github.com/ijpq/architecture_riscv/commit/b53fcf75716d0f7fa31d2f6910edc8b7b3515d2d) 和 [个人报告](lab1.report.md) 保留作历史学习证据，不作为本轮完成情况，也未重新验收整份报告。

## 课程进度

“未登记”表示当前没有在这里确认完成情况，不能据此判断以前是否学过。只有自己完成并留下推导、代码或报告后，才标为“完成”。

| 项目 | 当前记录 | 资料与成果 |
|---|---|---|
| L01 | 已讨论课程背景、ISA/微架构与 IBM 360；未作逐页验收 | [本轮笔记](https://app.notion.com/p/4056a691a12d814ebc07c97c6ff28576) |
| L02 | 已讨论第 25 页取指及单总线控制；未逐页验收 | [本轮笔记](https://app.notion.com/p/4056a691a12d814ebc07c97c6ff28576) |
| L03 | 已讨论第 5–7、10–12 页的控制器、分支与复杂指令；Pure ROM 时序仍待研究 | [本轮笔记](https://app.notion.com/p/4056a691a12d814ebc07c97c6ff28576)、[L03 导读](course/notes/lectures/L03.md) |
| L04：流水线、异常与性能 | 已通过 HW1 P3/P5 讨论旁路、停顿、精确异常及性能铁律；尚未登记 L04 讲义的阅读页码 | [L04 导读](course/notes/lectures/L04.md)、[流水线与异常笔记](https://app.notion.com/p/40e6a691a12d8185afc9d2f4f28d7601)、[性能推理笔记](https://app.notion.com/p/4146a691a12d81a1bd2ec57b03801878) |
| L05–L19、L21–L26 | 原讲义已收录；本轮逐讲阅读进度未登记 | [逐讲路线](course/ROADMAP.md)、[中文导读](course/notes/README.md) |
| 补充单元：系统衔接与虚拟化 | 尚未登记学习；用于补充知识，不计为已找回或已完成官方 L20 | [补充材料](course/notes/lectures/L20-supplement.md)、[来源与缺口](course/ORIGINS.md) |
| HW1 | 进行中：已讨论至 P5.f；3.A/3.D/3.E 由助手整理，3.B 与 P4/P5 仍需订正；2.C 四处旧订正已回填，µBr/计数、2.B 优化与寄存器重合、1.A–1.F 旧稿订正待继续 | [本轮作业笔记](https://app.notion.com/p/4056a691a12d814ebc07c97c6ff28576)、[五级流水线图解](https://app.notion.com/p/40e6a691a12d8185afc9d2f4f28d7601)、[微码测试](work/hw01/README.md)、[MINV 范围](work/hw01/MINV.md)、[原题与手册](course/assignments/README.md) |
| HW2 | 未登记 | [原题与手册](course/assignments/README.md) |
| HW3 | 未登记 | [原题与手册](course/assignments/README.md) |
| HW4 | 未登记 | [原题与手册](course/assignments/README.md) |
| HW5 | 未登记 | [原题与手册](course/assignments/README.md) |
| Lab1 | 本轮未重做；旧报告记录到第二轮 §3.7 | [个人报告](lab1.report.md)、[实验指南](course/labs/lab1.md) |
| Lab2 | 完成情况未登记 | [实验指南](course/labs/lab2.md) |
| Lab3 | 完成情况未登记 | [实验指南](course/labs/lab3.md) |
| Lab4-modern | 完成情况未登记；采用 RVV 1.0/gem5 | [实验指南](course/labs/lab4.md) |
| Lab5 | 完成情况未登记；保留已有个人代码 | [实验指南](course/labs/lab5.md) |

资料说明：收录的 Spring 2023 镜像包含 L01–L19、L21–L26，没有 L20 编号；无法据此判断是漏传、改号还是停课。本地另有系统衔接说明与 Spring 2021 虚拟机讲义，均为明确标注的补充材料。“缺失材料”描述的是资料来源，不表示学习者漏学了这些内容。

## 每次学习后更新

在上表更新当前小节和成果链接，再在下表追加一行。日常把记录提交到主仓库的 `main` 分支；其他源码仓库的用途见 [仓库导航](docs/REPOSITORIES.md)。

| 日期 | 学习项目 | 本次留下的成果 | 下次继续的位置 |
|---|---|---|---|
| 2025-07-23 | Lab1 第二轮，§3.4–§3.7 | [已有报告与测量记录](lab1.report.md) | 复核 §3.7 的推导和后续实验要求 |
| 2026-10-26 | 从头重学，L01 与 L02 到第 25 页 IF | [ISA、微架构、微码与取指笔记](https://app.notion.com/p/4056a691a12d814ebc07c97c6ff28576) | 独立复述 MA/A/PC 与控制信号，再继续取指和 ALU 微程序 |
| 2026-10-27 | 讨论学习方法，技术位置仍为 L02 第 25 页 | [先建立框架、最小推演、练习检验与回查的方法](https://app.notion.com/p/4056a691a12d814ebc07c97c6ff28576) | 手推一次取指，再继续 ALU/LW；将缺失的实现前提单独标记 |
| 2026-10-27 | 补充学习导航，技术位置不变 | [逐讲重点页与分层自检](course/notes/lectures/README.md)、[HW 逐题覆盖](course/assignments/coverage.md) | 使用 L02 三道基础检查后进入相应微码练习，选做题按薄弱项补 |
| 2026-10-28 | HW1 第一题 1.A–1.C：立即数/访存、test/ZF、指令长度/标签、栈不变量和动态计数 | [讨论与核对笔记](https://app.notion.com/p/4056a691a12d814ebc07c97c6ff28576)；已修复 1.C 回环前缺少 n 的问题，其他订正仍待回填 | 自己订正、复算 1.A–1.C 后开始 1.D；不自动推进讲义页码 |
| 2026-10-29 | 补记 1.D–1.F；开始 Worksheet 2.A；核对 L03/handout/源码中的微指令、busy 与 µPC | [控制器结构、取指状态表与讲解订正](https://app.notion.com/p/4056a691a12d814ebc07c97c6ff28576)；当日 Notion 授权受阻，2026-10-30 已恢复授权、补同步并回读确认两端一致 | 独立推演 IF，再填写 2.A；保留 Pure ROM 首次采样时序为待查问题 |
| 2026-10-31 | L03 分支与复杂指令；Worksheet 2.A 逐行讨论和题意纠正 | [MODULOM 流程、IR 连线、控制信号误区与学习反思](https://app.notion.com/p/4056a691a12d814ebc07c97c6ff28576)；补记 Pure ROM 的个人思考及未解问题 | 订正伪代码、独立填写控制表，用具体输入检查所有后继路径 |
| 2026-11-01 | 补记 Worksheet 2.A 完整控制表复核与代码验证 | [修正副本](work/hw01/modulom-reviewed.md)于前一日通过 5,036 组行为模型用例，16 项模拟器回归检查通过；补记读内存/写 B、MemWr/enMem、SUB/COPY_A 与安全 don’t care | 整理正式答案，先独立预测每拍再对照 trace；测试未涉及真实 RTL 或 Pure ROM 时序 |
| 2026-11-01 | Worksheet 2.B MINV 控制表讨论与测试；2026-11-02 补记 | [MINV 副本及测试](work/hw01/MINV.md)通过 5,448 组用例和 19 项针对性检查；补记目的寄存器、A/B 的角色、循环推进、显式写回与已知重合反例 | 最少周期优化及寄存器重合处理仍待继续，不能扩大为 RTL 验证或所有输入的证明 |
| 2026-11-02 | HW1 2.C 第一条 SUB：实现范围、时钟周期、取指与分派 | [2.C 纠错笔记](https://app.notion.com/p/4056a691a12d814ebc07c97c6ff28576)：六拍草稿的取指顺序和减法操作数已订正；用 0x1000 例子区分 PC/IR/µPC，澄清无需额外 NOP；记录助手曾误转述提问的问题 | 独立复述后继续 ANDI；其余周期未代填，整份 2.C 未完成 |
| 2026-11-03 | HW1 2.C 草稿核查；BNE 和机器/微状态跳转 | [2.C-4、6～9 笔记](https://app.notion.com/p/4056a691a12d814ebc07c97c6ff28576)：补记 PC+4 与 D 独立、x0 读写、自拟/源码计数差别；保留 N 忽略 Next State、J 选择微地址的纠正过程。当时 BNE 草稿仍未拆开 PC−4，后来修订见下一条 | 当时待订正各行、补 µBr、继续 AUIPC；尚未完成整份 2.C，也未新增测试验证 |
| 2026-11-03 | 2.C 草稿续改；AUIPC 与 U 型立即数 | [2.C-7、10～11 笔记](https://app.notion.com/p/4056a691a12d814ebc07c97c6ff28576)：记录 SUB/ANDI/BNE 已作的修订、JALR 返回地址多加 4；保留忘记 U 型格式、AUIPC 误写 PC 和多减 4 的纠正过程。用源码区分自拟 5 拍与参考 7 拍 | 删除 AUIPC 多余的 A−4，完成 BEQ/JAL/JALR 等订正后再统一计数；本次仅手推与源码核对，未新增行为模型或 RTL 测试 |
| 2026-11-04 | HW1 P3 前置五级流水线复习 | [修正图、控制补全图与 P3-1～8 纠错](https://app.notion.com/p/40e6a691a12d8185afc9d2f4f28d7601)：核对 PC、时钟沿、RF 端口、旁路、load-use、保持 D 与 bubble；原笔记及新增图文已回读验证，仓库正文缓存已移除 | 先独立复述 LW→SUB 三拍，再继续尚未阅读的 BEQ；未新增 RTL 仿真，不标记 P3 或 HW1 完成 |
| 2026-11-05 | 笔记覆盖核对；五级流水线与 3.A 问答补记 | [P3-0、P3-9、3.A-1～3](https://app.notion.com/p/40e6a691a12d8185afc9d2f4f28d7601)：补全 ADD 五阶段例子、旁路与 RF 写回的区别、第二写口需求和算术指令时序对照；主笔记 2.C-12 确认四处订正已回填。两页回读一致，旧记录、两图与附件保留 | 自行订正 3.A，继续 2.C 的 µBr 与周期表；本次仅记录与资料核对，未修改作业答案、未新增代码测试 |
| 2026-11-06 | 补记学习者指出遗漏的讲解第 10 节 | [P3-10：三种旁路分别在什么情况下派上用场](https://app.notion.com/p/40e6a691a12d8185afc9d2f4f28d7601)：补记 EX/MEM/WB→Decode 的三个例子、时钟沿、来源选择与 load-use 边界；此前仅零散提及旁路，不等于完整保存该节 | 学习位置不推进；需要时用三组指令间隔回查旁路来源，未新增 RTL 仿真 |
| 2026-11-08 | 3.A 纠错与答案整理；开始理解 3.B | [P3-9/10 续问、3.A-1～4、3.B-1](https://app.notion.com/p/40e6a691a12d8185afc9d2f4f28d7601)：保存旁路/RF 区别、采样沿、NOP 间隔、M1/M2、反例及两个比较基准；明确助手讲解中的混淆。Notion 重新授权后已同步并回读核对，原图与附件保留 | 独立复述 3.A 后继续 3.B 的新冒险分析；本次未新增代码测试，不把助手整理的答案记为独立完成 |
| 2026-11-10 | 3.B–E、P4 与 P5 a–f 问答整理 | [精确异常与恢复](https://app.notion.com/p/40e6a691a12d8185afc9d2f4f28d7601)、[ISA 与性能推理](https://app.notion.com/p/4146a691a12d81a1bd2ec57b03801878)：WAW、架构状态、一拍 interlock、旧值备份；延迟槽、stage/state/CPI、关键路径、访存等待、短编码与 CISC 内部实现。保留助手过强断言及学习者的正确反驳 | 回填正式答案，区分实现假设与普遍结论；未发现本地官方 HW01 答案，讨论不是标准答案或实测性能 |

作业推导、代码、实验报告和验证记录可放到 `work/hw01/`、`work/lab01/` 等目录，并从这里链接；个人知识疑问与纠错写入 Notion，不再保留长期仓库正文缓存。没有记录的题目保持“未登记”，不要仅根据环境通过就勾选完成。

## 环境准备记录

2026-10-21 的环境核查：21 项原课程 RTL 与 11 项现代 Lab4 检查通过；课程及工具测试共 66 项通过，六个源码快照校验通过。详见 [验收记录](specs/verifications/COURSE_BRANCH_VERIFY.md)。

这些是环境与工具的结果。Lab4-modern 使用 RVV 1.0/gem5，原版 RVV 0.10 的 DLEN/chaining 定量题仍有限制；学生练习的完成情况以上面的个人记录为准。
