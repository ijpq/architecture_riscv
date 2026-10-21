# Lab5：共享内存多核、一致性与优化

原题：[Spring 2023 Lab5](../originals/sp23/labs/lab5.pdf)。前置 L21–L23、HW5。运行源码来自 2021/2022 课程版；先理解 coherence、consistency、同步和伪共享不是同一件事。

## 1. 按 hart 数建立正确性基线

```bash
scripts/cs152-local/cs152 benchmarks lab5 --harts 1
scripts/cs152-local/cs152 benchmarks lab5 --harts 2
scripts/cs152-local/cs152 build lab5 --config Lab5RocketConfig
scripts/cs152-local/cs152 build lab5 --config Lab5MESIDualRocketConfig
scripts/cs152-local/cs152 run lab5 .local/benchmarks/lab5-p1/mt-vvadd-naive.riscv --config Lab5RocketConfig
scripts/cs152-local/cs152 run lab5 .local/benchmarks/lab5-p2/mt-vvadd-naive.riscv --config Lab5MESIDualRocketConfig
scripts/cs152-local/cs152 run lab5 .local/benchmarks/lab5-p2/mt-matmul-naive.riscv --config Lab5MESIDualRocketConfig
```

ELF 中的 NHARTS 必须和机器匹配。包装器分别保存 p1/p2，并检查常量；双核程序直接拿去单核跑可能等待不存在的 hart。运行库的旧接口由常量适配器补足，不修改处理器协议语义。

## 2. 读源码，再改变一件事

程序在 `edu_cs152/lab5/lab/`，包括 `mt-vvadd-naive`、`mt-matmul-naive` 及相应 opt 目录。先标出工作划分、共享数据、同步点和每个输出的所有者；确认边界、矩阵维度和线程分工，再设计自己的布局或算法优化。

用户已有的 opt 修改被保留，并非全新空白模板，也不代表这些修改已正确。先保存自己的差异，逐步验证，不把文件存在或编译成功当成答案正确。

## 3. 比较一致性协议

双核另有 `Lab5MSIDualRocketConfig`、`Lab5MIDualRocketConfig`。使用相同 NHARTS、输入、程序和编译条件比较；只切换协议，保留每次完整日志。先按手册预测读共享、写独占、交替写入会产生哪些消息，再观察周期/事件。

普通 Spike 仅作功能检查，协议性能必须使用这些 RTL 配置。不能因为双核正确就断言所有线程交错都正确，也不能用 coherence 替代必要的程序同步。伪共享可能导致慢，却不等于数据竞争。

## 自己的交付物

- 一个可解释的双核工作划分图与正确性不变量。
- 单核/双核以及协议对照表，注明统计区域和输入。
- 一次只改变布局或任务划分的优化尝试，包含失败结果。
- 对串行部分、同步、负载平衡和带宽瓶颈的分析，而非只写加速比。

代表性基准的环境验收通过，不覆盖用户所有 opt 文件或每种输入。更多运行库、计数器和重编规则见 [环境文档](../../docs/LOCAL_ENVIRONMENT.md)。
