# Lab2：缓存、Mystery 与预取

原题：[Spring 2023 Lab2](../originals/sp23/labs/lab2.pdf)。前置 L06–L10、HW2。运行源码是 2022 课程版，配置名与路径按本文，不照搬旧服务器绝对路径。

## 1. 建立基线

```bash
scripts/cs152-local/cs152 benchmarks lab2
scripts/cs152-local/cs152 build lab2 --config CS152RocketConfig
scripts/cs152-local/cs152 run lab2 edu_cs152/lab2/lab/directed/transpose.riscv --config CS152RocketConfig --preload
```

`--preload` 会按 ELF 内容生成 HEX，不能自己把 ELF 文件冒充 DRAM 的 HEX。对比循环次序或 blocking 时固定输入，先保证转置正确，再解释局部性和计数器。

## 2. 缓存扫描与 Mystery

可用配置：`CS152RocketConfig`、`CS152RocketL2Config`、`CS152RocketMysteryConfig`。

```bash
scripts/cs152-local/cs152 build lab2 --config CS152RocketL2Config
scripts/cs152-local/cs152 run lab2 edu_cs152/lab2/lab/open1/ccbench/caches/caches --config CS152RocketL2Config --preload --arg=1024 --arg=128 --arg=0
```

三个参数是 int 元素数、迭代数、RunType；数组字节数乘 4。程序可能调整迭代数。示例只是小规模自检，不足以推断容量、关联度和行大小。你需要自己设计工作集/步长扫描、重复测量和对照，保持其他条件不变；不反编译课程 jar 揭开 Mystery。

同配置同程序的运行日志会覆盖。每次扫描后另存并汇总日志，再用 `cs152 plot-caches ... --output .local/plots/名称` 生成 CSV/SVG；旧 Python2 绘图脚本不是推荐入口。

## 3. 预取与真实程序

另有 `CS152RocketNoPrefetchConfig`、`CS152RocketPrefetchConfig`。先构建对应配置，再运行小规模 BFS：

```bash
scripts/cs152-local/cs152 build lab2 --config CS152RocketPrefetchConfig
scripts/cs152-local/cs152 run lab2 edu_cs152/lab2/lab/open2/gapbs/bfs --config CS152RocketPrefetchConfig --preload --arg=-g --arg=5 --arg=-n --arg=1 --arg=-v
```

要求 `Verification: PASS`。改变数据规模前估算 RTL 等待成本，不把超时当性能结果。记录需求访问、缺失、带宽影响和周期，不只记录命中率。

**性能口径：**GAPBS 的计时接口由真实 `rdcycle` 按 1 GHz 归一化，表示模拟周期秒，不是主机耗时或真实芯片频率。普通 Spike 不用于缓存性能。

**完成标准：**保留正确性、扫描原始数据、带单位的图、参数推断过程和至少一个反例检查。SPEC CPU2006 为可选授权内容，不在分支内，不因缺少它阻断以上学习。细节见 [环境说明](../../docs/LOCAL_ENVIRONMENT.md)。
