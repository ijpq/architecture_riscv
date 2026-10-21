# Lab4：现代 RVV 1.0 本地教学路线

原题：[Spring 2023 Lab4](../originals/sp23/labs/lab4.pdf)。前置 L14、L17–L19、HW4。**运行现代替代，不是原版 RVV 0.10 + 定制 timing Spike 的复刻。**完整模型合同见 [lab4-modern/README.md](../../lab4-modern/README.md)。

## 为什么另建

原课程的 DLEN、chaining 与旧分支/缓存延迟接口依赖未取得的课程工具包。普通 Spike 和新编译器不能冒充它。这里保留原 C 主程序、数据和验证器，向量指令按 RVV 1.0 使用，时序由固定 gem5 O3/cache 模型提供。

| 原题内容 | 本地怎么学 |
|---|---|
| 标量/向量内核的正确性、布局、strip-mining | 保留，使用现代工作副本与原校验器 |
| VLEN、SEW、LMUL、掩码 | 按 RVV 1.0 学习与实验 |
| DLEN/lane/chaining 的旧定量题 | 作为原题纸面模型推导，不用现代结果冒充答案 |
| 性能比较 | 只在相同 gem5 模型、输入和 ROI 内比较；FU 数不是物理 lane 数 |

## 从示例开始

```bash
scripts/cs152-local/cs152 lab4-modern benchmarks csaxpy vec-csaxpy
scripts/cs152-local/cs152 lab4-modern run csaxpy
scripts/cs152-local/cs152 lab4-modern run vec-csaxpy --vlen 128
scripts/cs152-local/cs152 lab4-modern run vec-csaxpy --vlen 512
```

先逐行读原提供的 `vec-csaxpy`，指出实际 VL 如何更新剩余元素和指针、向量寄存器如何分配、最后一轮怎样处理。再选 `vec-cmplxmult` 起步；其余 dgemv/dgemm/imax/spmv/rsort 逐步完成。六组 TODO 没有代写，未完成程序校验失败是预期。

```bash
# 自己完成后重编，不能只运行旧 ELF：
scripts/cs152-local/cs152 lab4-modern benchmarks cmplxmult vec-cmplxmult
scripts/cs152-local/cs152 lab4-modern run vec-cmplxmult --vlen 256
```

## 做一次因果实验

先运行独立自检的两个延迟设置，观察同一依赖指令链：

```bash
scripts/cs152-local/cs152 lab4-modern run rvv-runtime --vlen 128 --vector-latency 1
scripts/cs152-local/cs152 lab4-modern run rvv-runtime --vlen 128 --vector-latency 8
```

本机环境验收曾得到 598/1069 周期，说明参数确实进入发射队列的功能单元；这是自检结果，不是课程内核答案。gem5 此处按向量寄存器生成算术微操作，延迟不会自动随 VLEN 缩放，所以增大 VLEN 不保证真实硬件式的 lane 吞吐变化。

`cycles` 来自 `setStats` 对应的 ROI，校验在 ROI 之外但必须成功。查看运行保存的 `stats.txt`、`summary.json`、`config.json`。重复运行会更新同组合证据，正式实验另存结果。完整环境复验用 `cs152 lab4-modern verify`。

**完成标准：**各目标正确、尾部和不同 VLEN 测试、标量/向量同模型对照、原始统计和明确限制。不能声称复现了原课每项 DLEN/chaining 数值，也不能把 host 耗时当模拟硬件性能。
