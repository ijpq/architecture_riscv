#!/usr/bin/env bash
# Source from any directory. Do not change the caller's working directory.
_CS152_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd -P)"
export CS152_ROOT="$_CS152_ROOT"
export CS152_CONDA="${CS152_CONDA:-$CS152_ROOT/chipyard/.conda-env}"
export JAVA_HOME="${CS152_JAVA_HOME:-/usr/lib/jvm/java-11-openjdk-amd64}"
export RISCV="${CS152_RISCV:-$CS152_CONDA/riscv-tools}"
export PATH="$JAVA_HOME/bin:$RISCV/bin:$CS152_CONDA/bin:$PATH"
export COURSIER_REPOSITORIES="https://repo.maven.apache.org/maven2"
export CS152_JOBS="${CS152_JOBS:-8}"
export CS152_RV32_GCC="${CS152_RV32_GCC:-$CS152_ROOT/.local/tools/xpack-riscv-none-elf-gcc-12.2.0-3/bin/riscv-none-elf-gcc}"
export CS152_RV32_OBJDUMP="${CS152_RV32_OBJDUMP:-${CS152_RV32_GCC%gcc}objdump}"
export BMARKS="${CS152_BMARKS:-$CS152_ROOT/chipyard-cs152-sp23/generators/riscv-sodor/riscv-bmarks}"
export CS152_BUILT_BMARKS="$CS152_ROOT/.local/benchmarks/lab1"
export MAKEFLAGS="${MAKEFLAGS:-}"
unset _CS152_ROOT
