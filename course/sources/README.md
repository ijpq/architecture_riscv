# 必要实验源码快照

六个 `.tar.gz` 归档把本机已恢复环境的必要源码带到学习分支。目录不包含安装好的编译器、Conda、构建缓存或完整 Git 历史。

| 归档 | 字节数 | 包含的源码仓库数 |
|---|---:|---:|
| `lab1.tar.gz` | 49,289,871 | 25 |
| `lab2.tar.gz` | 52,190,314 | 25 |
| `lab3.tar.gz` | 43,088,135 | 22 |
| `lab4-original.tar.gz` | 2,763,842 | 1 |
| `lab5.tar.gz` | 35,973,088 | 23 |
| `rv32-reference.tar.gz` | 754,626 | 1 |

总计约 175.5 MiB。精确哈希、提交、修改摘要与追加文件见 [manifest.json](manifest.json)。上游源码的许可证与版权标头保留在各自归档内部，不能把不同上游的代码统一声明为本项目原创。

```bash
# 在项目根目录执行；不要手工 tar 到已有实验目录。
python3 course/source_bundle.py check
python3 course/source_bundle.py restore
```

原版 Lab4 的练习源文件会恢复，但缺失的课程 RVV 0.10 模拟器不会被伪装成已经找回。现代替代见 [Lab4 指南](../labs/lab4.md)。

完整边界和新检出启动方法见 [SOURCES.md](../SOURCES.md)。这是可检出的课程源代码集合，不是全离线工具链镜像，也不是包含所有可选模块的通用 Chipyard 发行版。
