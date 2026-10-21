# Lab 4 Modern：FU 参数未连接到发射队列

状态：已修复并通过回归。下列初始失败记录保留用于解释根因。

## Reproduce

环境：gem5 v25.1.0.1，提交 c8222cc67a399bfc01e8658dd14b30d5bfd634f9，RiscvO3CPU，1 GHz。

```bash
scripts/cs152-local/cs152 lab4-modern verify
```

日志：`.local/logs/lab4-modern-verify.log`。
7 个标量、提供的向量示例、3 个 RVV 探针均通过数据校验，但向量延迟敏感性失败：
`VECTOR-LATENCY EFFECT: 598 -> 598 cycles FAIL`。
探针包含 128 条依赖的 `vadd.vi v8,v8,1`；VLEN 128/512 分别验证 4/16 个元素。

## Isolate

- `.local/src/gem5/src/arch/riscv/isa/decoder.isa:4701-4703` 将 vadd_vi 分类为 `SimdAddOp`。
- 延迟 8 的 ROI 中 `system.cpu.issuedInstType_0::SimdAdd=128`，证明目标指令实际发射。
- `.local/src/gem5/src/cpu/o3/inst_queue.cc:916-929` 通过 `issuing_inst->iq` 和 `iq->fuPool()` 取延迟。
- `.local/src/gem5/src/cpu/o3/BaseO3CPU.py:187` 定义 `instQueues = VectorParam.IQUnit(IQUnit(), ...)`。
- `.local/src/gem5/src/cpu/o3/IQUnit.py:53` 为队列定义自己的 `fuPool`。
- 实际 `config.json` 同时存在两个池：`cpu.instQueues[0].fuPool` 为 count=4、SimdAdd latency=1；
  另加的 `cpu.fuPool` 为 count=2、latency=8。原配置合同检查了后者，但 C++ 实际使用前者。

## Hypothesize

1. **优先假设：配置挂到了未使用的普通子对象，真实 IQ 池未改变。**
   证伪实验：只在私有配置副本中将该池接到 `cpu.instQueues[0].fuPool`，比较 latency=1 与 8。
2. vadd 被分类为 IntAlu：已被解码器和 issuedInstType 的证据排除。
3. 探针没有执行或结果被优化：已被汇编指令计数和元素结果校验排除。

## Verify

单变量诊断脚本 `.local/checks/gem5-fu-route.py` 不修改生产文件，只将池接到真实队列：

| 探针 | 真实队列 count / latency | ROI 周期 | 结果 |
|---|---|---:|---|
| RVV 128 | 2 / 1 | 598 | 数据校验 PASS |
| RVV 128 | 2 / 8 | 1069 | 数据校验 PASS |

诊断日志：`.local/logs/gem5-fu-route-lat1.log`、`.local/logs/gem5-fu-route-lat8.log`。
实际配置中不再出现无效的 `cpu.fuPool` 子对象。结果支持假设 1，排除探针不敏感的解释。

## 修复与回归

- `lab4-modern/gem5_config.py` 使用 `system.cpu.instQueues[0].fuPool = pool`。
- `scripts/cs152-local/lab4_modern.py:validate_config` 检查真实单 IQ 池的 count 和所有 opLat；
  不允许旁支 `cpu.fuPool` 充当配置证明。
- `test_unused_cpu_pool_cannot_hide_the_active_queue_configuration` 在旧验证器上真实失败，修复后通过。
- 51 项工具单测通过；生产 `lab4-modern verify` 通过 11/11，保持延迟敏感性门槛。
  生产运行同样得到 **598 → 1069 周期**，不是只有私有诊断脚本有效。
- `doctor all --lab4 modern` 返回 0；原 Lab 1/2/3/5 的 21 项 RTL 证据保持有效。

验证日志：`.local/logs/lab4-modern-fu-routing-red.log`、`.local/logs/local-tooling-tests.log`、
`.local/logs/lab4-modern-verify.log`、`.local/logs/doctor-all-modern.log`。
