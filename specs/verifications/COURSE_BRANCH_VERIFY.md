# 完整学习分支验收

## 结论与适用范围

`learn/cs152-complete` 已收录可检出的 CS152 自学材料、必要实验源码和本地工具。验收基于源码提交 `58822b3`，不是只检查当前目录已有的模拟器。机器可读摘要见 [COURSE_BRANCH_STATUS.json](../COURSE_BRANCH_STATUS.json)。

以下冷构建及归档大小记录对应上述提交。后续微码 trace 和说明修正见文末「阅读复查后的修正」；当前归档大小和哈希以 [源码清单](../../course/sources/manifest.json) 为准。

这不是官方单学期镜像：原题以 Spring 2023 为主，运行源码跨年份；Lab4 明确采用 RVV 1.0/gem5 替代。新检出不带 Conda、编译器安装目录、编译缓存、gem5 可执行文件或旧 PASS 证据。安装工具和首次构建仍需要网络与时间。

## 材料覆盖

| 内容 | 验收结果 |
|---|---|
| 原始 PDF | 56 份；文件大小、SHA-256、PDF 结构全部通过 |
| Spring 2023 讲义 | L01–L19、L21–L26，共 25 份 |
| 缺失材料 | L20、disc05 未发现原件；提供明确标注的补课与文本自测，不虚构官方内容 |
| 作业与配套手册 | HW1–5，以及四份相关手册；不包含答案 |
| 实验指导 | Lab1–5 原始 PDF，加五份本地学习指南 |
| 其他原件 | 12 份讨论题、3 份试卷、参考卡、1 份旧学期虚拟化补充讲义 |
| 文本可读性 | 55 份可提取正文；disc13 为 20 页扫描件，标明不可完整检索，不宣称已 OCR |
| 中文教学 | 逐讲路线、8 组概念导读、本地补课、自测、报告模板和实验映射 |
| 文档链接 | 最终提交树中 20 篇课程相关入口与验收 Markdown 的 164 个本地链接通过 |

## 源码恢复与隔离验证

六个源码包合计 **193,229,149 字节**，包含 **106 个浅 Git 仓库**。每个仓库保留钉定的上游提交及必要工作树修改，不携带完整历史、私有配置、hooks 或凭据。

验证使用两个隔离目录：

- `.local/course-pristine`：直接从最终已提交分支检出，再恢复六包。
- `.local/course-checkout`：从归档恢复源码，用正常 Make/CLI 入口编译、运行。

两个目录的 106 个仓库 HEAD、浅历史、Git 对象完整性，以及 **19,986 个归档源码文件/符号链接条目**均逐项核对。实际运行目录与最终提交的归档内容一致。没有从宿主复制 simulator、Scala target 或 C++ 对象。

隔离构建显式复用了宿主已安装的工具链和下载缓存。这证明源码快照能重建，不等于验证一台空白操作系统或全离线安装。

| 隔离运行 | 结果 |
|---|---|
| Lab1 `Sodor1StageConfig` | 源码构建成功；新编 `towers` 运行成功，mcycle=4225、minstret=4232 |
| Lab2 `CS152RocketConfig` | 源码构建成功；directed、ccbench、GAPBS 编译成功；新编转置运行成功 |
| Lab3 `CS152BaselineBoomConfig` | 源码构建成功；新编 BOOM 环境探针通过，cycles=2132、instret=261 |
| Lab5 `Lab5MESIDualRocketConfig` | 源码构建成功；新编双核 vvadd、matmul 通过，分别 43201、477178 cycles |

Lab2 曾使用过过短的 120 秒限制，真实超时按失败保留；随后在文档默认的 900 秒内完成，不把失败尝试改写为成功。其他配置的本机 21 项 RTL 和现代 Lab4 的 11 次运行，由完整 doctor 另外复验，不混为新检出的全部配置冷构建。

## 新检出发现并修复的问题

1. Lab1 的 Make 设置 `java.io.tmpdir=.java_tmp`，但不创建目录。CLI 现在在构建前创建此生成目录；不将它当源码打包。
2. 温热构建目录掩盖了源码依赖缺漏。快照增加 `api-config-chipsalliance`、`rocket-dsp-utils`、Lab2 开放实验基准和 FPGA 壳，以及 RV32 的 `env/encoding.h`。
3. Lab5 正常 Make 会先生成本地 FIRRTL JAR；直接执行聚合 `sbt compile` 不是等价冷构建测试。未为了让错误入口通过而升级原课程硬件库。

对应回归先观察到失败，再实现修复。源码恢复器仍遵守非空目标 `KEEP`，不会用修复归档覆盖学生代码。

## 工具与既有环境复验

- 源码恢复器：11 项无网络、临时 Git fixture 测试通过。
- 本地 CLI、绘图与现代模型工具：52 项单元测试通过。
- 源码包哈希与安全检查：6/6 通过。
- 当前机器 `doctor all --lab4 modern`：21 项 RTL + 11 项现代运行全部通过；向量延迟 1→8 的依赖链为 598→1069 cycles。
- 默认原版 Lab4 路线仍不可用；现代模型不等价于 RVV 0.10 的 DLEN、lane 或 chaining。

日志保留在本机 `.local/logs/course-final-*.log`、`course-isolated-*.log`，摘要记录其 SHA-256。日志不是新检出中的预置 PASS；学习时仍需重建并产生自己的运行证据。

## 阅读复查后的修正

- 微码 trace 的退休标志解析由 `0/3` 修正为硬件输出的 `0/1`，同步更新 Lab1 归档和清单；归档其余 4,798 个条目的内容与元数据未变。新增三项回归覆盖退休计数、boot ROM 排除、气泡和普通流水线统计，保留已有访存偏移汇总。
- 现代 Lab4 的完整复验顺序补上 `benchmarks`：它负责编译，`verify` 运行已编译程序，并拒绝缺失或过期的 ELF。
- 更正 SPEC 范围：Lab2 包含五个基准的部分上游源码、文档和测试数据；可选路线未纳入本地构建与运行验收，具体目录见 [源码包说明](../../course/sources/README.md)。

本次课程测试 **14/14**、本地工具测试 **52/52**、源码包检查 **6/6** 通过。另在临时目录恢复 Lab1，运行三项 trace 回归，检查补丁保留额外学生修改，以及再次恢复输出 `KEEP`。现有环境指纹复验 **32/32**；本次没有重新构建 RTL 或 gem5。日志为 `.local/logs/course-corrections-*.log`，摘要见状态文件的 `post_review_corrections`。

## 保留的边界

未提供官方评分服务、学生答案、Mystery 参数或 Spectre 攻击实现。Lab2 归档保留部分上游 SPEC CPU2006 源码、文档和测试数据；该可选路线未构建验收，使用需合法授权。原件权利仍属原作者，公开镜像不代表授予再发布许可；没有推送远端。

用户原有 `chipyard` 修改、删除的旧 Gitlink、`local.sh` 和 NAS 链接均保留，未混入本次提交。根 `readme.md` 只选择性收录本次课程入口和旧安装记录警示，其余既有修改保留。未委派独立 reviewer；这是脚本验证加自审，不冒称独立审查。

## 最小复验入口

```bash
python3 course/fetch_materials.py
python3 course/source_bundle.py check
python3 -m unittest discover -s course -p 'test_*.py' -v
python3 -m unittest discover -s scripts/cs152-local -p 'test_*.py' -v
scripts/cs152-local/cs152 doctor all --lab4 modern
```

首次检出须先按 [SOURCES.md](../../course/SOURCES.md) 恢复源码、安装工具、构建和运行。首次 doctor 若缺少模拟器或运行证据，应视为尚未就绪，不能据此报告 PASS；完成实际运行后再验收。
