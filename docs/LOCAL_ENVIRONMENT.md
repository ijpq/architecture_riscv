# CS152 本地实验环境

用途：在开始学习前检查实验是否可做，并提供不依赖 Berkeley 登录服务器的构建、运行和复验入口。

## 当前结论

**按已选择的「Lab 4 现代替代」路线，五个实验的本地环境现已就绪：21 项原课程 RTL 检查 + 11 项现代 Lab 4 检查，共 32/32 项通过。**

Lab 4 使用独立的 RVV 1.0 + gem5 时序实验，**不是原 RVV 0.10 实验的复刻**；原版工具链仍未取得。

| 实验 | 已构建并运行的范围 | 必需验收 | 结论 |
|---|---|---:|---|
| Lab 1 | Sodor 1/3/5 级；源码重编 `towers`、课程 `mix` | 6/6 | 可本地学习、修改、重编和运行 |
| Lab 2 | Rocket、L2、Mystery、NoPrefetch、Prefetch；transpose、ccbench、GAPBS BFS | 6/6 | 可本地开展缓存与预取实验 |
| Lab 3 | Baseline/SWPred/Small BOOM；周期/退休指令检查；官方 pk-spectre 受害系统调用 | 4/4 | 可本地开展分支预测和 Spectre 实验 |
| Lab 4（现代替代） | 7 个标量、原提供向量示例、RVV 宽度与延迟自检；15 个程序全部构建 | 11/11 | 可本地开展现代 RVV 实验；旧题目的 DLEN/chaining 数值不适用 |
| Lab 5 | 单核 Rocket；双核 MESI/MSI/MI；向量加和矩阵乘基准 | 5/5 | 可本地开展多核一致性实验 |

验收检查的是环境，不是学生答案：没有实现 Spectre 攻击、优化学生算法或反编译 Mystery Cache 参数。
代表性小工作负载通过，不表示所有大规模参数组合和学生实现都已通过。
Lab 2 快照的 `lab/open3/CPU2006/` 保留上游已有的部分 SPEC CPU2006 源码、文档和测试数据；该可选路线未纳入本地构建及运行验收，使用仍需合法授权。具体范围见 [源码包说明](../course/sources/README.md)。
这套环境不提供 Berkeley 私有评分服务或受限课程视频；书面作业仍需按对应年份资料自行完成。

## 入口与诊断

从项目根目录执行：

```bash
cd /home/tangke/cs152
source scripts/cs152-local/env.sh
scripts/cs152-local/cs152 doctor lab1
scripts/cs152-local/cs152 doctor lab2
scripts/cs152-local/cs152 doctor lab3
scripts/cs152-local/cs152 doctor lab5
scripts/cs152-local/cs152 doctor all --lab4 modern
```

五条命令在其运行证据仍有效时均返回 0。最后一条显式选择现代 Lab 4，检查全套 32 项。
不带 `--lab4 modern` 的 `doctor` 仍检查原课程路线，因旧 Lab 4 阻塞，**应返回 1**；不会偷偷切换模型。
`doctor` 不只检查可执行文件是否存在，还核对程序、模拟器、运行日志及代理内核的 SHA256。
改变这些文件后，需要重新运行相应验收，不能把旧的通过记录当成新结果。
旧 RTL 路线的 `doctor` 不自动检测所有 Scala/C/C++ 源码变化；修改源码后必须先重新编译。
现代 Lab 4 另外校验编译命令、源文件及头文件记录；修改后未重编会明确拒绝运行旧 ELF。

`env.sh` 不切换目录，也不修改全局 Java、Git、Conda 配置。
`cs152` 启动器会自行加载该环境；直接调用 `make` 时应先 `source`。
保留原有 `local.sh` 和学生修改，不再依赖课程里的 `/home/ff/...` 路径。

## 本机工具与版本边界

- Java：系统 OpenJDK **11**，默认 `/usr/lib/jvm/java-11-openjdk-amd64`。不是任意 Java 版本都能兼容旧 sbt/Scala。
- Verilator：`chipyard/.conda-env/bin/verilator`，本次构建使用 5.008。
- RV64 GCC、elf2hex、普通 Spike：`chipyard/.conda-env/riscv-tools/bin/`。
- RV32I GCC：`.local/tools/xpack-riscv-none-elf-gcc-12.2.0-3/`，带真实 RV32I multilib。
- 现代 Lab 4：gem5 **v25.1.0.1**，私有构建位于 `.local/src/gem5/build/CS152/gem5.opt`。
- 现代 Lab 4 的 Linux 编译器：`/usr/bin/riscv64-linux-gnu-gcc` **11.4.0**；使用静态 `rv64gcv/lp64d`，不混用裸机启动代码。
- 并行度：`CS152_JOBS` 默认 8；内存不足时在命令前设置 `CS152_JOBS=4`。

这是几代课程代码的组合，不能统一套用最新版 Chipyard：

| 用途 | 源码目录 | 本次基线提交 |
|---|---|---|
| Lab 1 | `chipyard-cs152-sp23/` | `8e133223` |
| Lab 2 | `edu_cs152/lab2/` | `7c2a551` |
| Lab 3 | `edu_cs152/lab3/` | `1b8736e` |
| Lab 5 | `edu_cs152/lab5/` | `13b587c` |
| Lab 4 现代替代 | `lab4-modern/`；gem5 位于 `.local/src/gem5/` | gem5 `c8222cc67a399bfc01e8658dd14b30d5bfd634f9` |

初始化、补依赖可能访问 GitHub、Maven Central、JFrog 插件归档及 PyPI（私有 SCons）；日常运行不需要 Berkeley 服务器。
代理默认读取 `git config http.proxy`；可用 `CS152_PROXY=direct` 或代理 URL 覆盖。
不要升级全部 Chisel/FIRRTL 插件来“修复”旧工程。包装器保留旧接口并处理已失效的插件仓库。

已应用的兼容修复包括：

- 按原 gitlink 提交恢复缺失子模块和资源软链，不覆盖学生已有文件。
- sbt 使用可下载的历史插件归档；Lab 2 为消失的测试 SNAPSHOT 固定兼容依赖。
- 宿主模拟器用 C++17 编译，以兼容现代 FESVR 的 `std::optional`。
- 为 Verilator 5 设置 `--timing -Wno-fatal`；Lab 5 另设置旧设计所需的数值宽度上限。
- 修复 GAPBS 的 C++ 启动文件、裸机计时接口，以及 Lab 5 的旧 `nharts` 运行库接口。

这些修改用于恢复构建和运行，不替换学生要实现的硬件或算法。

## 通用流程

```bash
scripts/cs152-local/cs152 setup lab2        # 缺失依赖/资源恢复；不是每次都要执行
scripts/cs152-local/cs152 build lab2        # 从 Scala/Chisel 重新生成并构建 RTL
scripts/cs152-local/cs152 benchmarks lab2   # 从 C/C++/汇编重新编译程序
scripts/cs152-local/cs152 run lab2 edu_cs152/lab2/lab/directed/transpose.riscv --preload
```

`run` 的程序路径是位置参数，不是 `--binary`。
`--seconds` 是主机等待秒数，默认 900；`--max-cycles` 是模拟周期上限，默认 100000000。
RTL 很慢：短基准也可能需数分钟，本机一次 Lab 1 `spmv` 约需 10 分钟。超时不是通过；减少数据量或提高等待上限后重试。
控制台截断长行以便阅读，完整输出保存在 `.local/logs/`。
同一实验使用文件锁，避免同时改写构建和运行记录。

### Lab 1：流水线与可编辑程序

```bash
scripts/cs152-local/cs152 benchmarks lab1
scripts/cs152-local/cs152 build lab1 --config Sodor3StageConfig
scripts/cs152-local/cs152 run lab1 .local/benchmarks/lab1/towers.riscv --config Sodor3StageConfig
scripts/cs152-local/cs152 run lab1 .local/benchmarks/lab1/mix.riscv --config Sodor3StageConfig
```

同样支持 `Sodor1StageConfig`、`Sodor5StageConfig`。
课程可编辑程序在 `chipyard-cs152-sp23/generators/riscv-sodor/test/custom-bmarks/`。
`benchmarks lab1` 重编课程 `mix`，并从本机 riscv-tests 源码重编 8 个参考基准。
`$BMARKS` 仍指原课程预编译程序；`$CS152_BUILT_BMARKS` 指 `.local/benchmarks/lab1/`。

RV32 构建使用 ISA 2.2 的 RV32I，避免新 CSR 命名导致 GCC 选错 multilib。
xPack 无原生 TLS，单 hart 裸机 printf 缓冲区取消 TLS；这不是通用多线程运行库。
现代 riscv-tests 的 `mm` 需要原子扩展，不纳入这组 RV32I 源码重编目标；没有假造原子接口或给 Sodor 添加 A 扩展。
课程原有的预编译 `mm` 保留，但不因其他基准通过就声称它已重新编译验收。

### Lab 2：缓存、Mystery 和预取

支持的配置：`CS152RocketConfig`、`CS152RocketL2Config`、`CS152RocketMysteryConfig`、
`CS152RocketNoPrefetchConfig`、`CS152RocketPrefetchConfig`。

```bash
scripts/cs152-local/cs152 build lab2 --config CS152RocketL2Config
scripts/cs152-local/cs152 run lab2 edu_cs152/lab2/lab/open1/ccbench/caches/caches \
  --config CS152RocketL2Config --preload --arg=1024 --arg=128 --arg=0
scripts/cs152-local/cs152 run lab2 edu_cs152/lab2/lab/open2/gapbs/bfs \
  --config CS152RocketPrefetchConfig --preload --arg=-g --arg=5 --arg=-n --arg=1 --arg=-v
```

ccbench 的三个参数依次是 int 元素个数、迭代数、RunType。数组字节数是第一个参数 **乘 4**。
程序会按计时阈值调整迭代次数，输出的 NumIterations 不一定等于传入值。
示例是环境检查用的小数据量，不是完成 Mystery 或性能报告所需的完整扫描。
BFS 用 `-v` 输出 `Verification: PASS`；GAPBS 还已编译 cc、sssp、tc，并生成 kron10.sg。

旧 Python 2 绘图入口不再作为推荐路径。用无第三方依赖的 Python 3 工具从真实日志生成 CSV 和 SVG：

```bash
scripts/cs152-local/cs152 plot-caches \
  .local/logs/lab2-CS152RocketL2Config-caches-run.log \
  .local/logs/lab2-CS152RocketMysteryConfig-caches-run.log \
  --output .local/plots/cache-smoke
```

一份输入日志对应一个来源/配置；多个数组尺寸应先保存在同一份独立扫描日志中。
绘图器只连接采集到的数据，不猜缓存参数。上述两条短测只有两个点，不能据此完成缓存逆向。
重复同配置、同程序的 `run` 会覆盖该运行日志；扫描时须将每次结果追加保存，不能只保留最后一个尺寸。

**性能单位：** transpose 等直接读取 RTL 的 HPM。GAPBS 的 `_gettimeofday` 适配器读取真实 `rdcycle`，
按 1 GHz 归一化为“模拟周期秒”，不是主机墙钟时间，也不是该硬件的实际频率声明。
报告原始周期时按此归一化换算，并考虑 timeval 的微秒精度；不要把普通 Spike 的周期当作缓存性能。

### Lab 3：分支预测与 Spectre

```bash
scripts/cs152-local/cs152 benchmarks lab3
scripts/cs152-local/cs152 build lab3 --config CS152SmallBoomConfig
scripts/cs152-local/cs152 run lab3 .local/checks/boom-runtime.riscv --config CS152SmallBoomConfig --preload
scripts/cs152-local/cs152 run lab3 .local/checks/pk-victim.riscv \
  --config CS152SmallBoomConfig --pk edu_cs152/lab3/lab/open2/pk-spectre
```

还支持 `CS152BaselineBoomConfig`、`CS152SWPredBoomConfig`，三者都跑过环境测试。
`boom-runtime` 必须打印 `CS152_BOOM_RUNTIME_PASS` 和正的周期/退休指令数。
`pk-victim` 必须打印 `CS152_PK_VICTIM_PASS syscall=101 legal-bounds-and-rejection`。
后者验证真实 BOOM 上的代理内核、U-mode 程序、合法受害调用及越界拒绝，不实现推测攻击。
带 `--pk` 的程序不要使用裸机 HEX 预加载。

`pk-spectre` 来自官方 cs152-teach/chipyard-cs152 的固定提交
`296373efa4762bb41387970dfcb98f5f0914e160`，下载校验记录在 `.local/evidence/pk-spectre-download.json`。
学生的 `spectre.c` 仍需自行完成；空 main 可以退出，并不代表攻击作业已完成。

### Lab 4：现代 RVV 本地替代

完整说明和旧题目到现代模型的对应关系见 **[lab4-modern/README.md](../lab4-modern/README.md)**。
原目录 `edu_cs152/lab4` 不改；只在 `lab4-modern/exercises/vec-*/` 中完成自己的汇编 TODO。
原提供的 `vec-csaxpy` 是示例，其余六组练习未代写；重复 setup 不覆盖已有练习副本。

```bash
# 已构建的本机日常使用：
scripts/cs152-local/cs152 lab4-modern doctor
scripts/cs152-local/cs152 lab4-modern run csaxpy
scripts/cs152-local/cs152 lab4-modern run vec-csaxpy --vlen 512

# 自己完成汇编后，先重编，再校验和测量：
scripts/cs152-local/cs152 lab4-modern benchmarks vec-cmplxmult
scripts/cs152-local/cs152 lab4-modern run vec-cmplxmult --vlen 256

# 如需从头重建或重跑本实验的环境验收：
scripts/cs152-local/cs152 lab4-modern setup
scripts/cs152-local/cs152 lab4-modern build
scripts/cs152-local/cs152 lab4-modern benchmarks
scripts/cs152-local/cs152 lab4-modern verify
```

未完成的练习运行失败是预期行为，不是已经替你完成了作业。
性能数据来自 `setStats` 包围的 ROI；校验在 ROI 外执行，但必须通过后才写成功证据。
`benchmarks` 不带程序名时编译全部 15 个程序。`verify` 使用已编译的程序，运行 7 个标量、原示例和 3 个运行库/时序自检；它不执行编译。
若 ELF 缺失或编译指纹过期，先运行 `lab4-modern benchmarks`，再运行 `verify`。
它会改写相同名称的运行证据；正式测量可另存对应日志和 `stats.txt`。

模型为 1 GHz RiscvO3CPU、时序缓存/内存。可调 `--vlen 128/256/512/1024`、
`--vector-latency`、`--vector-units` 和 `--memory-latency-ns`。
实际发射队列的功能单元配置会被核验，不能仅凭参数回显判断生效。
实测同一条依赖 RVV 指令链的延迟从 1 改为 8，ROI 从 **598 增至 1069 周期**。

gem5 此处按向量寄存器建模算术微操作，延迟不随 VLEN 自动缩放；这不是物理 lane/chaining 模型，
没有等价的旧 `dlen` 参数。可以研究 strip-mining、指令数、功能单元延迟与缓存，
但不能把数值当作原课时序 Spike 的答案，也不能把主机运行耗时当硬件性能。

### Lab 5：多核与一致性

```bash
scripts/cs152-local/cs152 benchmarks lab5 --harts 1
scripts/cs152-local/cs152 benchmarks lab5 --harts 2
scripts/cs152-local/cs152 run lab5 .local/benchmarks/lab5-p1/mt-vvadd-naive.riscv --config Lab5RocketConfig
scripts/cs152-local/cs152 run lab5 .local/benchmarks/lab5-p2/mt-vvadd-naive.riscv --config Lab5MESIDualRocketConfig
scripts/cs152-local/cs152 run lab5 .local/benchmarks/lab5-p2/mt-matmul-naive.riscv --config Lab5MESIDualRocketConfig
```

双核还支持 `Lab5MSIDualRocketConfig`、`Lab5MIDualRocketConfig`；构建方法与其他实验相同。
现代运行库不再导出旧的 `nharts` 符号，新增的常量适配器用编译参数补足接口。
原 Makefile 跟踪 NHARTS 变化，包装器分别保存 p1/p2 二进制，并在运行内置配置前校验 ELF 中的常量。
不要把双核程序直接当成单核程序跑。普通 Spike 仅用于功能检查，协议性能必须使用这些真实 RTL。
学生已有优化文件未被重写；未完成的优化程序失败不等于基础设施失败。

## 原版 Lab 4：保留的限制

原 Makefile 要求旧 RVV 指令编码/汇编器及课程定制的时序 Spike，例如：

```text
--isa=rv64gcv --ic=64:4:64:16 --dc=64:4:64:16 --l2=1024:8:64:58
--br=3:28:512:6 --varch=vlen:512,elen:64,dlen:128
```

本机普通 Spike 不支持这一整套接口和模型。新版 RVV 1.0 也不能直接冒充 RVV 0.10。
公开实验仓库只包含实验程序；旧课程下载地址转向 Berkeley CAS，不能把认证 HTML 当作下载成功。
公开学生笔记提及 `lab4-install.tgz`，但未找到可合法公开下载的完整包。

继续恢复需要：合法原课程工具归档，或能验证上述接口和时序语义的源码。
收到归档后先校验内容、版本和授权，再测试向量程序、缓存/分支延迟及 VLEN/DLEN 扫描；仅 `spike --help` 不算通过。
现已按用户选择另建上述现代替代实验，单独标注模型、差异及验证结果；原目录和旧工具需求不变。
若必须逐项复现旧讲义的 DLEN/chaining 数值题，仍需要原课程包，不能沿用“原版 Lab 4 已完成”的结论。

## 证据、常见问题与复验

- `.local/logs/`：实际构建和运行命令、工作目录、完整输出。
- `.local/evidence/`：成功运行的 SHA256 证据；超时、非零退出或失败文本不会记为通过。
- `.local/benchmarks/`：源码重编程序和按 hart 数分离的 Lab 5 程序。
- `.local/loadmem/`：按 ELF 内容哈希缓存的 HEX；**不是直接把 ELF 传给旧 SimDRAM**。
- `specs/LOCAL_ENVIRONMENT_STATUS.json`：本轮验收快照；实时状态以 `doctor` 为准。

旧 DRAM loader 的未对齐 warning 本身不等于失败；检查程序验证输出和退出状态。
若看到 `trap_illegal_instruction`，先检查位宽、扩展和程序启动方式；现代 Spike 读计数器需要 Zicntr/Zihpm。
若遇到旧 SNAPSHOT 下载或 sbt 插件解析错误，使用这里的入口，不要绕过包装器调用系统 sbt。
`open1` 原默认扫描和授权 SPEC 目标不会由 `benchmarks lab2` 自动触发。

复验命令：

```bash
python3 -m unittest discover -s scripts/cs152-local -p 'test_*.py' -v
python3 -m py_compile scripts/cs152-local/*.py lab4-modern/gem5_config.py
bash -n scripts/cs152-local/env.sh scripts/cs152-local/sbt scripts/cs152-local/cs152
scripts/cs152-local/cs152 doctor lab1
scripts/cs152-local/cs152 doctor lab2
scripts/cs152-local/cs152 doctor lab3
scripts/cs152-local/cs152 doctor lab5
# 选定的五实验路线：应返回 0。
scripts/cs152-local/cs152 doctor all --lab4 modern
# 原课程路线：仍应返回 1，不能用 || true 把它算成通过。
scripts/cs152-local/cs152 doctor
```
