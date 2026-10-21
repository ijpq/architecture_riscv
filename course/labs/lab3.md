# Lab3：BOOM、分支预测与推测执行

原题：[Spring 2023 Lab3](../originals/sp23/labs/lab3.pdf)。前置 L11–L16、HW3。运行源码是 2022 课程 BOOM；先读重命名、ROB、方向/目标预测的区别。

## 1. 先验证测量路径

```bash
scripts/cs152-local/cs152 benchmarks lab3
scripts/cs152-local/cs152 build lab3 --config CS152SmallBoomConfig
scripts/cs152-local/cs152 run lab3 .local/checks/boom-runtime.riscv --config CS152SmallBoomConfig --preload
```

需要 `CS152_BOOM_RUNTIME_PASS`，以及正的周期/退休指令数。这是环境检查，不是分支预测作业答案。另有 `CS152BaselineBoomConfig` 与 `CS152SWPredBoomConfig`。

## 2. 学习预测器接口

源文件在：

```text
edu_cs152/lab3/generators/boom/src/main/resources/csrc/predictor_sw.cc
edu_cs152/lab3/generators/boom/src/main/resources/csrc/btb_sw.cc
```

不要改 `generated-src/` 或 `target/` 中的复制品，它们会被重新生成覆盖。先明确表项、索引、初始状态、更新时机和恢复约束，再实现自己的方案。修改后必须重跑相应 `build`；旧 doctor 不自动发现所有 C++/Scala 源码变更。

用短分支序列手算预测状态，再跑受控基准。比较准确率、周期、存储预算与混叠，不把方向准确率直接当成总性能。相同程序、配置和输入才能组成有效对照。

## 3. Spectre 的安全实验边界

```bash
scripts/cs152-local/cs152 run lab3 .local/checks/pk-victim.riscv --config CS152SmallBoomConfig --pk edu_cs152/lab3/lab/open2/pk-spectre
```

必须看到 `CS152_PK_VICTIM_PASS syscall=101 legal-bounds-and-rejection`。这里验证合法受害调用与越界拒绝，不包含推测攻击答案。使用 `--pk` 时不要再用裸机 `--preload`。

`spectre.c` 保留给你完成。仅在自己的课程模拟器和指定受害系统中研究；不针对真实设备、其他用户或第三方服务。要区分架构结果与微架构痕迹，区分环境接口可用与攻击作业成功。空 main 能退出不是完成证据。

**自己的报告：**预测器状态推演、受控比较、完整命令/日志、正确性和限制。pk 来源与完整构建说明见 [本地环境文档](../../docs/LOCAL_ENVIRONMENT.md)。
