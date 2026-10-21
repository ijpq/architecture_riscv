# 学习分支怎样带走实验源码

## 包含什么

本分支既提交课程材料，也提交 [六个源码快照](sources/README.md)。它不是只改了分支名称，也不要求能访问根目录旧的私有 Git submodule。

快照包含构建这些实验所需的、已验证工作树中的源码与兼容性修复。每个必要子仓库保留原提交的最小浅 Git 元数据，使旧 sbt 插件和子模块版本检查仍能识别提交。没有复制完整历史、原 Git 配置、hooks、credentials、NAS、Conda 或构建缓存。

| 包 | 恢复位置 | 用途 |
|---|---|---|
| lab1 | `chipyard-cs152-sp23/` | Sodor 与 2023 Chipyard 必要依赖 |
| lab2 | `edu_cs152/lab2/` | 2022 Lab2 的源码、必要依赖与 HTIF 兼容文件 |
| lab3 | `edu_cs152/lab3/` | 2022 Lab3 的源码、必要依赖与课程 pk 运行依赖 |
| lab4-original | `edu_cs152/lab4/` | 保留原练习 / 数据；原版模拟器仍不可用 |
| lab5 | `edu_cs152/lab5/` | 2021 版本的 Lab5 源码、必要依赖与本地多 hart 兼容修复 |
| rv32-reference | `chipyard/toolchains/riscv-tools/riscv-tests/` | Lab1 构建基准所需的 RISC-V tests 源码 |

这些版本有意分开：把所有实验换成同一代 Chipyard 会改变课程接口，不能得到已经验证的环境。

## 在当前目录使用

```bash
python3 course/source_bundle.py check
python3 course/source_bundle.py restore
python3 course/fetch_materials.py
```

`check` 校验六包的大小、SHA-256、成员路径及类型。`restore` 只安装不存在或空的目标目录。**非空目录输出 `KEEP`，不覆盖、不删除已有实验，也不保证这个目录已经完整。** 如果原目录本来缺依赖，仍须用本地环境命令检查或按对应 Lab 指南补齐。

若怀疑现有目录有冲突，不要删除它：先建立另一个不带学生改动的检出，再运行恢复工具。

## 新检出的启动顺序

```bash
git switch learn/cs152-complete
# 不要加 --recurse-submodules，也不要在根目录执行递归 submodule update。
python3 course/source_bundle.py restore
python3 course/fetch_materials.py
source scripts/cs152-local/env.sh
scripts/cs152-local/cs152 env
scripts/cs152-local/cs152 doctor all --lab4 modern
```

**新检出第一次 doctor 显示缺少模拟器 / 二进制是正常的**：源码恢复不是编译，也不会把旧机器的运行证据伪装成新检出的验收结果。按 [本地环境指南](../docs/LOCAL_ENVIRONMENT.md) 和 [各 Lab 指南](labs/README.md) 执行 `setup`、`build`、`benchmarks`、`run`，再检查 doctor。

此机器原环境的 Conda 工具在 `chipyard/.conda-env/`。如果另建 worktree，可在 `source` 之前显式复用宿主工具，例如：

```bash
export CS152_CONDA=/home/tangke/cs152/chipyard/.conda-env
export CS152_RISCV="$CS152_CONDA/riscv-tools"
export CS152_RV32_GCC=/home/tangke/cs152/.local/tools/xpack-riscv-none-elf-gcc-12.2.0-3/bin/riscv-none-elf-gcc
export CS152_RV32_OBJDUMP=/home/tangke/cs152/.local/tools/xpack-riscv-none-elf-gcc-12.2.0-3/bin/riscv-none-elf-objdump
source scripts/cs152-local/env.sh
```

这些绝对路径只示范本机工具复用，不能照搬到其他电脑。RV32 路径以 `cs152 env` / `docs/LOCAL_ENVIRONMENT.md` 的实际安装位置为准；需要时由 `setup lab1` 获取锁定工具。Java 11、RISC-V 工具链、Verilator、sbt 缓存和现代 Lab4 的 gem5 **不是课程源码归档的一部分**。新机器仍有工具安装、构建时间和网络需求，不能称为全离线镜像。

现代 Lab4 的脚本、RVV 1.0 模板和模型配置直接存放在 `lab4-modern/`；gem5 源码 / 可执行文件按锁定版本由独立 setup 流程处理。原 RVV 0.10 模拟器没有因此恢复。

## 快照如何追溯

[manifest.json](sources/manifest.json) 记录每包的哈希、目的目录、子仓库 HEAD、原工作树修改摘要以及显式追加的兼容文件。包内的上游许可证、COPYING 和源文件版权标头随源码保留。课程 PDF 的来源与版权另见 [ORIGINS.md](ORIGINS.md)。

- 浅仓库只保证当前提交及其源文件，不包含任意旧版本的历史遍历。
- 课程之外的大型可选子模块没有全部收录；不能据此宣称完整通用 Chipyard 发行版。
- `pack` 是维护者导出操作，不是日常学习命令。已有归档会被拒绝替换。
- 本分支保留了恢复时已经存在的源码修改，并不声称所有目录与上游提交逐字节相同；请阅读清单中的 `working_changes`。
- 若自己修改过练习，重新 `restore` 不会更新它，也不会覆盖它。

## 安全边界

恢复器先检查清单与归档，拒绝绝对路径、`..` 成员路径、硬链接、设备节点、重复成员、穿越符号链接的成员和越界 / 循环链接。文件只写入临时目录，校验后才安装目标。它是普通用户的本地安装工具，不是抵抗其他进程并发替换目录的多用户沙箱。
