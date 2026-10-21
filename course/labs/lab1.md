# Lab1：流水线与测量基础

原题：[Spring 2023 Lab1](../originals/sp23/labs/lab1.pdf)。先学 L01–L05、完成 HW1 相关题，再读 [中文导读](../notes/README.md)。本地使用 `chipyard-cs152-sp23`，不是顶层历史 `chipyard` 私有 Gitlink。

## 第一轮：不改答案，跑通同一个程序

从项目根目录执行：

```bash
scripts/cs152-local/cs152 benchmarks lab1
scripts/cs152-local/cs152 build lab1 --config Sodor3StageConfig
scripts/cs152-local/cs152 run lab1 .local/benchmarks/lab1/towers.riscv --config Sodor3StageConfig
scripts/cs152-local/cs152 doctor lab1
```

`doctor lab1` 检查整组证据；刚恢复的新检出只跑一个程序后，整组尚未齐全不算安装失败。要产生 Lab1 的全部 6 项核心运行证据：

```bash
for config in Sodor1StageConfig Sodor3StageConfig Sodor5StageConfig; do
  scripts/cs152-local/cs152 build lab1 --config "$config"
  for program in towers mix; do
    scripts/cs152-local/cs152 run lab1 ".local/benchmarks/lab1/$program.riscv" --config "$config"
  done
done
scripts/cs152-local/cs152 doctor lab1
```

## 第二轮：比较设计

另外构建 `Sodor1StageConfig` 和 `Sodor5StageConfig`，用相同 `towers.riscv` 运行。先预测数据相关和分支对三个实现的影响，再观察周期与指令。没有合成时序数据时，只报告周期，不编造真实时钟频率或 CPU 秒数。

课程可编辑汇编在 `chipyard-cs152-sp23/generators/riscv-sodor/test/custom-bmarks/`。先读 `mix`，自己设计小序列区分旁路、load-use 和控制冒险。改汇编后重跑 `benchmarks lab1`，改 Scala/硬件后重跑 `build`；不能只运行旧 ELF 或 simulator。

## 应交给自己的成果

- 一张采用明确计时假设的指令时序图。
- 同 ELF、不同配置的周期/指令表及原始日志。
- 对一个测量结果的解释，以及一个能推翻解释的最小对照程序。

**边界：**源码重编的 8 个参考基准与原课程预编译包不是完全同一集合。现代 `mm` 需要原子扩展，未纳入 RV32I 重编验收；不要据此宣称所有预编译基准都已从源码验证。RV32 工具链用私有 xPack，旧 Java/sbt 用本地包装器。

更多准确命令、统计和工具边界见 [环境说明的 Lab1 部分](../../docs/LOCAL_ENVIRONMENT.md)。
