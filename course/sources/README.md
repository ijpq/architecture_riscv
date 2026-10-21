# 必要实验源码快照

六个 `.tar.gz` 归档把本机已恢复环境的必要源码带到学习分支。目录不包含安装好的编译器、Conda、构建缓存或完整 Git 历史。

| 归档 | 字节数 | 包含的源码仓库数 |
|---|---:|---:|
| `lab1.tar.gz` | 49,541,321 | 27 |
| `lab2.tar.gz` | 61,050,751 | 31 |
| `lab3.tar.gz` | 43,088,135 | 22 |
| `lab4-original.tar.gz` | 2,763,842 | 1 |
| `lab5.tar.gz` | 35,973,088 | 23 |
| `rv32-reference.tar.gz` | 812,008 | 2 |

总计 106 个仓库、193,229,145 字节（约 184.3 MiB）。精确哈希、提交、修改摘要与追加文件见 [manifest.json](manifest.json)。上游源码的许可证与版权标头保留在各自归档内部，不能把不同上游的代码统一声明为本项目原创。

```bash
# 在项目根目录执行；不要手工 tar 到已有实验目录。
python3 course/source_bundle.py check
python3 course/source_bundle.py restore
```

原版 Lab4 的练习源文件会恢复，但缺失的课程 RVV 0.10 模拟器不会被伪装成已经找回。现代替代见 [Lab4 指南](../labs/lab4.md)。

## Lab2 可选 SPEC 文件的范围

`lab2.tar.gz` 保留上游 `lab/open3/CPU2006/` 中的部分文件：`401.bzip2`、`429.mcf`、`450.soplex`、`458.sjeng`、`470.lbm` 的源码、文档和测试数据，以及构建片段。它们不是完整的 SPEC CPU2006 安装包；本地 CLI 不构建或验收这条可选路线，必学路径不依赖它。使用这些文件仍需遵守相应许可证和授权要求。

## Lab1 trace 解析修正

`lab1.tar.gz` 已修正微码 trace 的 `0/1` 退休标志解析，并保留原有指令分类和访存偏移统计。可审阅的修改见 [补丁](patches/lab1-tracer-retire.patch)。

已有实验目录仍会被 `restore` 保留。若你的解析器仍使用 `0/3`，可在项目根目录检查并应用这个单文件补丁；`--check` 失败时先检查现有修改，不要强制覆盖：

```bash
git -C chipyard-cs152-sp23/generators/riscv-sodor apply --check "$PWD/course/sources/patches/lab1-tracer-retire.patch"
# 仅在上一步成功后执行：
git -C chipyard-cs152-sp23/generators/riscv-sodor apply "$PWD/course/sources/patches/lab1-tracer-retire.patch"
```

完整边界和新检出启动方法见 [SOURCES.md](../SOURCES.md)。这是可检出的课程源代码集合，不是全离线工具链镜像，也不是包含所有可选模块的通用 Chipyard 发行版。
