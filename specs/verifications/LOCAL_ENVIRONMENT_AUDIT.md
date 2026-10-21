---
type: verification
context: cs152-local-environment
---

# 本地实验环境自查

## 结论与范围

功能验收通过：选择现代 Lab 4 时，32/32 项核心检查通过。
这是本机环境验收和作者自查，不是独立代码审查，也不证明所有输入与参数组合均正确。
未派发子代理；未提交、重置或清理用户工作树。

## 检查清单

| 检查 | 结果 | 证据或边界 |
|---|---|---|
| 原课程 RTL | PASS | Lab 1/2/3/5 分别 6/6、6/6、4/4、5/5；doctor 重验 ELF、模拟器及日志指纹 |
| 现代向量执行 | PASS | 11/11；VLEN 128/512 分别检查 4/16 个元素 |
| 时序参数真实生效 | PASS | 实际 IQ 功能单元池被验证；延迟 1→8 时 598→1069 周期 |
| 实际配置合同 | PASS | 检查 VLEN、ELEN、时钟、timing 模式、内存延迟和真实 SIMD count/opLat |
| 编译记录与修改检测 | PASS | 源、头文件、命令、ELF 指纹；改源未重编时拒绝旧 ELF |
| 失败不误报成功 | PASS | 不匹配 VLEN、未完成练习、返回值 256 均被拒绝；失败重跑撤销旧成功证据 |
| 额外模型组合 | PASS | 原示例 VLEN 128/512/1024；自检 VLEN 1024、单向量单元、延迟 8、内存 80 ns |
| 工具回归 | PASS | 51 项 unittest；包含故意超时和错误数据负测，日志出现失败字样不等于整套测试失败 |
| 语法与补丁检查 | PASS | py_compile、bash -n、git diff --check；命令与日志见状态 JSON |
| 参数与进程边界 | 已检查 | 参数使用 argv 列表而非 shell 拼接；范围校验、超时、同实验构建锁和原子证据写入 |
| 来源与依赖 | 已检查 | gem5 固定提交；SCons 固定版本及 wheel SHA；不安装无关框架 |
| 原用户内容 | 保留 | 不覆盖既有汇编练习；不填写作业答案；保留原脏树、已有文件类型变化及 NAS 链接 |
| 原 RVV 0.10 | BLOCKED（预期） | 默认 original doctor 仍返回 1，不把现代替代冒充旧工具链 |
| 全面静态类型检查 | 未执行 | 当前 Python 工具没有完整类型标注；py_compile 只检查语法，不是类型检查 |
| 严格样式门槛 | CONCERNS | 部分工具模块超过 300 行，公共函数未全部标注类型；不为样式做无关大重构 |
| 外部自动质量工具 | 未执行 | 未安装 slopcheck/bp-churn-rank；无独立 reviewer；不声称这些门槛已通过 |

项目没有 AGENTS.md、CLAUDE.md 或 CONVENTIONS.md。上述样式问题是后续维护建议，不改变已执行的功能验收结果。

## 限制

- gem5 为寄存器粒度的 RVV 1.0 时序模型，不是旧 DLEN/chaining 模型或实际芯片性能认证。
- 旧 RTL 的 doctor 不追踪所有源文件变化；改硬件或测试源码后必须先 build。现代路线额外校验编译记录。
- 代表性运行不覆盖大负载和全部参数扫描；未完成练习本来就应校验失败。
- 可选 SPEC CPU2006 需要合法授权；不提供学校私有评分服务或受限课程资源。

主证据：`specs/LOCAL_ENVIRONMENT_STATUS.json`、`.local/logs/`、`.local/evidence/`。
实时检查：`scripts/cs152-local/cs152 doctor all --lab4 modern`。
