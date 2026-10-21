# Lab 4 Modern：RVV 1.0 本地替代实验

这是经你选择后单独建立的学习路线，**不是原版 RVV 0.10 / 定制 Spike 的复刻**。
原目录 `edu_cs152/lab4/` 不被这套工具覆盖。全套使用说明见 [`../docs/LOCAL_ENVIRONMENT.md`](../docs/LOCAL_ENVIRONMENT.md)。

**本机已构建全部 15 个程序，并通过 11/11 项核心运行验收。**
VLEN 128/512 的自检分别验证 4/16 个元素；同一依赖向量指令链在延迟 1/8 下分别耗时 598/1069 周期。
额外通过了原向量示例的 VLEN 128/512/1024 运行，以及未完成练习、失败撤销和错误码 256 的负测。
实时检查用 `scripts/cs152-local/cs152 lab4-modern doctor`；这些环境检查不代表六组 TODO 已完成。

## 保留什么，替换什么

- 保留原课程的 7 组 C 主程序、输入数据和结果校验函数。
- 保留 `csaxpy` 提供的向量示例，以及另外 6 组向量练习中的 TODO；没有新增作业答案。
- 向量汇编工作副本位于 `exercises/vec-*/`。初始化只为旧式 `vsetvli` 补显式 `tu,mu` 策略，已有策略不变。
- 运行时改为静态 RISC-V Linux 程序，由 gem5 SE 模式提供系统调用，不需要远程服务器或完整 Linux 镜像。
- 时序使用固定版本 gem5 的乱序 CPU、事件驱动缓存和内存模型，不使用普通 Spike 的功能指令计数冒充性能。

重复执行 `setup` 或 `benchmarks` **不会覆盖已经存在的汇编工作副本**。修改汇编后需要重新编译；不要只重跑旧 ELF。

## 固定版本与宿主依赖

| 项目 | 版本或位置 |
|---|---|
| gem5 | `v25.1.0.1`，提交 `c8222cc67a399bfc01e8658dd14b30d5bfd634f9` |
| gem5 源码/程序 | `.local/src/gem5/` / `.local/src/gem5/build/CS152/gem5.opt` |
| SCons | 私有安装的 `4.9.1`；`requirements-build.txt` 固定官方 wheel SHA-256 |
| 交叉编译器 | `/usr/bin/riscv64-linux-gnu-gcc`，本机 GCC 11.4.0，静态 glibc |
| 构建 Python | 系统 Python 3.10 与开发头；不用 NAS 上的 Conda Python |

构建隔离 `PYTHONHOME`、`PYTHONPATH`、`LD_LIBRARY_PATH`；只在本项目的私有目录安装 SCons。
若在另一台 Ubuntu 上重建，需要先准备 `g++`、`binutils`、`git`、`python3.10-dev`、`python3-pip`、
`zlib1g-dev`、`libpng-dev`、`gcc-riscv64-linux-gnu`、`libc6-dev-riscv64-cross`。
缺少 protobuf/HDF5 时，相应可选输出功能不可用，不影响此处的基本时序运行。

## 从准备到运行

在项目根目录执行：

```bash
scripts/cs152-local/cs152 lab4-modern setup
scripts/cs152-local/cs152 lab4-modern build --jobs 8
scripts/cs152-local/cs152 lab4-modern benchmarks
scripts/cs152-local/cs152 lab4-modern run rvv-runtime --vlen 128 --vector-latency 1
scripts/cs152-local/cs152 lab4-modern run csaxpy
scripts/cs152-local/cs152 lab4-modern run vec-csaxpy
```

第一次 gem5 源码构建较慢，需要数 GB 构建空间；后续日常运行不重新构建 gem5。
所有基准禁止编译器自动向量化，避免把“标量基线”悄悄变成向量程序。
编译后的程序在 `.local/benchmarks/lab4-modern/`。

独立的 `rvv-runtime` 只检查向量执行、数据结果、实际 VLEN 和依赖指令延迟，不实现任何课程内核。
它需要覆盖多个 VLEN 和延迟设置；一次通过不能代替整套环境验收。

## 怎样边学边做

| 程序组 | 学习主题 | 初始状态 |
|---|---|---|
| `csaxpy` / `vec-csaxpy` | 动态 VL、掩码与浮点运算 | 原课程已有向量示例 |
| `cmplxmult` / `vec-cmplxmult` | 交错数据与复数运算 | 向量 TODO 保留 |
| `dgemv` / `vec-dgemv` | 矩阵向量乘、归约 | 向量 TODO 保留 |
| `dgemm` / `vec-dgemm` | 数据复用、寄存器分组与余数 | 两份向量汇编 TODO 保留 |
| `imax` / `vec-imax` | 比较、归约与索引 | 向量 TODO 保留 |
| `spmv` / `vec-spmv` | 不规则访问与间接寻址 | 向量 TODO 保留 |
| `rsort` / `vec-rsort` | 排序、掩码与数据重排 | 向量 TODO 保留 |

例如，编辑 `lab4-modern/exercises/vec-cmplxmult/vec_cmplxmult.S` 后：

```bash
scripts/cs152-local/cs152 lab4-modern benchmarks cmplxmult vec-cmplxmult
scripts/cs152-local/cs152 lab4-modern run cmplxmult
scripts/cs152-local/cs152 lab4-modern run vec-cmplxmult
```

**未完成的练习应校验失败，不应显示 PASS。** 原校验函数可能返回大于 255 的错误位置；
适配器会先输出完整 `code`，再将任何非零值统一映射到 Linux 退出码 1，防止 256 被截成 0。
只有校验正确后才讨论加速比。使用相同输入、编译选项和模型，比较 ROI 周期，而不是主机运行秒数。

## 可控制的性能模型

```bash
scripts/cs152-local/cs152 lab4-modern run vec-csaxpy \
  --vlen 512 --vector-latency 8 --vector-units 2 --memory-latency-ns 80
```

| 参数 | 可选范围 | 真实含义 |
|---|---|---|
| `--vlen` | 128 / 256 / 512 / 1024 bit | ISA 向量寄存器位宽；ELEN 固定 64 |
| `--vector-latency` | 1–64 CPU 周期，默认 4 | SIMD 算术功能单元的操作延迟 |
| `--vector-units` | 1–16，默认 2 | SIMD 算术功能单元实例数 |
| `--memory-latency-ns` | 1–1000 ns，默认 50 | 末级缓存之后的 SimpleMemory 延迟 |

固定模型：单核 `RiscvO3CPU`，1 GHz；32 KiB/4-way L1I 与 L1D，访问延迟 2 周期；
256 KiB/8-way L2，访问延迟 12 周期；64 B 缓存行；512 MiB 内存、12.8 GiB/s 带宽。
详细参数与配置代码在 `gem5_config.py`；一次运行也会保存 `config.ini` 和 `config.json`。

**必须理解的限制：**

1. gem5 该版本按向量寄存器生成算术微操作，LMUL 可产生多个微操作。其操作延迟不会自动按 VLEN/SEW 缩放。
2. `vector-units` 是算术功能单元个数，**不是物理向量 lane 数，也不是旧 Spike 的 DLEN**。
3. 这是寄存器粒度的 O3 依赖调度，不是按元素的向量 chaining 模型；不同 SIMD 算术操作在本配置中使用同一个可控延迟。
4. 向量访存产生真实的模拟内存请求，但不是某个实际 RVV 芯片的校准模型。
5. 原讲义的 DLEN、chaining、旧分支预测参数及绝对周期答案不能直接沿用。本路线保留向量编程与模型内的性能比较，
   不覆盖旧专用模型的每个定量问题。不要把这些周期与 Lab 1/2/3/5 的 RTL 周期直接比较。

可以研究：正确性、strip-mining、LMUL、掩码、数据布局、减少指令、同一模型下的相对周期、FU 延迟/资源和内存延迟敏感性。
不能据此声称：复现了原版 DLEN 扫描结果，或测出了实际硬件 lane/chaining 的吞吐率。

## 测量区域与验收

原 `setStats(1/0)` 被桥接为 gem5 `workbegin/workend`。入口重置统计，出口单独输出 ROI 统计；
随后继续执行完整的结果校验，校验失败不会变成成功证据。ROI 包含少量边界调用开销，不包含后续校验；重置统计不会清空缓存。
原始统计文件可能有多个区段，工具只读取**第一个完整 ROI 区段**，不混入后面的 printf 和校验工作。
`cycles` 是模拟 CPU 周期，`instructions` 是该区段的模拟指令统计，不是主机计时。

```bash
scripts/cs152-local/cs152 lab4-modern verify
scripts/cs152-local/cs152 lab4-modern doctor
# 全套采用明确授权的现代 Lab 4 路线：
scripts/cs152-local/cs152 doctor all --lab4 modern
# 默认仍检查原版 Lab 4，不会被悄悄替换：
scripts/cs152-local/cs152 doctor all --lab4 original
```

环境验收要求 7 个原标量校验、课程向量示例，以及 RVV 自检的不同 VLEN/延迟运行；
提高依赖指令链的功能单元延迟必须实际增加模拟周期。未完成的学生练习不被算作已完成答案。

每次运行将命令、日志、`stats.txt`、`summary.json` 和配置保存在 `.local/`，通过后才写 SHA-256 证据。
现代 `doctor` 检查程序、模拟器、相关源码、配置、日志和统计指纹；修改后应重新编译并复验。
同一程序/模型的重复运行会替换该组合的记录；实验扫描时请另存表格或日志。
`--seconds` 控制主机超时，`--max-cycles` 控制模拟上限；两者触发均不算通过。

## 资料

- [RISC-V Vector Extension 1.0](https://github.com/riscv/riscv-v-spec/releases/tag/v1.0)
- [固定 gem5 源码](https://github.com/gem5/gem5/tree/c8222cc67a399bfc01e8658dd14b30d5bfd634f9)
- [本项目恢复范围与其他实验](../docs/LOCAL_ENVIRONMENT.md)
