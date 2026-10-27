# 补课：ABI、二进制翻译与系统虚拟机

[导读索引](README.md) · [Spring 2021 L22 原件，45 页](../../originals/supplementary/sp21-L22-VirtualMachines.pdf) · [系统衔接说明](../20-local-bridge.md)

**这不是 Spring 2023 L20。** 镜像没有 L20，不能据此确定其题目或页码。此处按课程总结包含的 virtual machines 主题，使用有明确年份的补充 PDF，页码只属于这份 2021 原件。

## 页面怎么读

| PDF 页 | 等级 | 看完应当掌握什么 |
|---|---|---|
| [2–6：程序、ABI 与 user VM](../../originals/supplementary/sp21-L22-VirtualMachines.pdf#page=2) | 重点 | 说明同 ISA 为什么不保证任意二进制能运行；区分 ISA、ABI、OS 环境 |
| [7–11：软件补 ISA、解释与翻译](../../originals/supplementary/sp21-L22-VirtualMachines.pdf#page=7) | 重点 | 比较每次解释和先翻译复用，解释 guest 状态由谁维护 |
| [13–20：目标映射、自修改、DBT 与 chaining](../../originals/supplementary/sp21-L22-VirtualMachines.pdf#page=13) | 重点 | 说明 guest PC→host code 映射及缓存失效问题；权衡翻译成本 |
| [29–32：优化、精确异常与 shadow state](../../originals/supplementary/sp21-L22-VirtualMachines.pdf#page=29) | 重点 | 解释优化后执行顺序改变，为什么仍要恢复到 guest 精确状态 |
| [33–40：system VM / VMM](../../originals/supplementary/sp21-L22-VirtualMachines.pdf#page=33) | 重点 | 画 guest OS、VMM、硬件；解释特权资源与隔离责任 |
| [41–44：地址与设备虚拟化](../../originals/supplementary/sp21-L22-VirtualMachines.pdf#page=41) | 重点 | 区分 GVA/GPA/机器 PA、shadow 与两阶段机制；说明 DMA/I/O 也需管理 |

1 封面，12/16 为翻译示意、17 历史、21–22 事务，23–28 为 Transmeta 细节，可回查；45 致谢。无需先掌握一个完整 hypervisor。

## 三个相近名字，三个问题

进程虚拟内存管理地址翻译、保护和页面分配；user VM 提供运行某类程序所需的 ISA/ABI 环境；system VM 向 guest OS 提供一套受控机器。运行程序的模拟器不一定提供可启动 OS 的系统环境。

解释器逐条 fetch/decode/execute，简单但每次重复解释；动态翻译把常用块转换成 host 指令并缓存。译后分支目标、代码被修改后的失效、异常时的 guest 状态都要维护。翻译后的代码跑得快，也要摊销翻译时间。

## 两套地址映射由谁管理

guest OS 管 GVA→GPA；VMM/硬件再控制 GPA→机器地址。shadow page table 由 VMM 维护供硬件使用的组合映射；两阶段硬件转换把第二层保护交给硬件遍历与缓存，但 miss 路径会更复杂。

guest 修改自己的页表、切换上下文或设备做 DMA 时，都需要维持隔离与映射一致。普通 cache coherence 不替代权限检查；CPU 地址保护也不会自动约束设备 DMA。

讲义中的“guest 内核降到 user mode”等是经典实现模型，现代虚拟化扩展可以提供专用 guest 执行模式；“零开销”也只是特定负载的近似，不是所有 VM 的保证。

## 基础自检（约 10–15 分钟）

1. 两个系统 ISA 相同，但系统调用和可执行文件格式不同。为什么一个程序不一定能直接运行？应核对哪层接口？
2. guest 程序访问 GVA，guest OS 将它映射到 GPA=`0x2000`；VMM 再映到机器页。为什么不能直接拿 `0x2000` 当真实机器地址？
3. 解释“虚拟内存”“系统虚拟机”“动态二进制翻译”各解决什么；是否要求三者总同时出现？

<details>
<summary>完成后核对要点</summary>

1. 还需匹配 ABI、装载格式、运行环境/系统调用；仅 ISA 编码不够。
2. GPA 属于 guest 的资源视图，VMM 可把它放到不同机器页并保护其他 guest。
3. 分别是地址空间管理、受控机器环境、不同/同 ISA 代码的运行期转换优化；不必总绑定。

</details>

## 补缺／迁移（选做，实践后）

1. 翻译一个块花 200 拍，此后每执行一次节省 5 拍，忽略其他开销。至少执行多少次才严格净收益为正？自修改代码如何影响这个分析？
2. guest 两条指令被翻译并重排，较年轻操作已写出部分状态，较老操作此时异常。要维持 guest 的精确异常，需要保存/回滚哪些类状态？

<details>
<summary>检查方向</summary>

`5N>200`，至少 41 次；失效和重译会增加成本。恢复需涵盖 guest 寄存器、PC 与尚未不可逆生效的 store，类似 L12–13 的提交思想，不能只把 host PC 改成 handler 地址。

</details>

## 接到作业与实践

HW1–5 没有独立 VM 题，用三道基础检查和一张 GVA→GPA→机器地址图即可先过渡到 L21。可先读 [系统衔接说明](../20-local-bridge.md) 做任务划分。仓库没有完整 OS/hypervisor 实验，gem5 SE、普通 Spike 功能执行都不能作为完整虚拟机验收。
