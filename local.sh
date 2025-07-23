#!/bin/bash

# 加载 conda 环境（重要：必须 source 它的初始化脚本）
source /home/tangke/miniforge3/etc/profile.d/conda.sh

# 激活 chipyard 环境（假设路径为相对路径）
conda activate chipyard/.conda-env/

# 切换到 EDU_CHIPYARD 路径（该变量需要提前设定）
cd ./chipyard-cs152-sp23 || {
  echo "Error: EDU_CHIPYARD is not set or directory does not exist."
  return 1
}

# 设置环境变量
export CHIPYARDROOT=$PWD
export BMARKS=$CHIPYARDROOT/generators/riscv-sodor/riscv-bmarks
export SCRIPTS=$CHIPYARDROOT/generators/riscv-sodor/scripts

# 运行额外的环境脚本
source ./env.sh

# 清除sbt导致的java error日志
unset JAVA_TOOL_OPTIONS

# 可选：打印提示信息
echo "✅ Chipyard environment setup complete."
