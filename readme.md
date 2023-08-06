# from scratch

according to https://inst.eecs.berkeley.edu/~cs152/sp23/assets/labs/lab1.pdf
it contains a step which requires conda activate a dir of .conda-env , which is generated from release chipyard setup steps of docs. SO, you should setup the environment of chipyard release build firstly. while setup the env of release build(https://chipyard.readthedocs.io/en/stable/Chipyard-Basics/Initial-Repo-Setup.html#), **even if it would failed because submodule guestmount not found**, the dir `.conda-env` would generated also. therefore, once you found the .conda-env generated, you can go on the cs152 lab1.pdf.
after the the .conda-env successfuly generated from chipyard release build. you can go on the https://inst.eecs.berkeley.edu/~cs152/sp23/assets/labs/lab1.pdf steps.
you would encounter the java error like following, while running the command `./build-setup.sh riscv-tools`:
```
java.lang.ClassCastException: class java.lang.UnsupportedOperationException cannot be cast to class xsbti.FullReload (java.lang.UnsupportedOperationException is in module java.base of loader 'bootstrap'; xsbti.FullReload is in unnamed module of loader 'app')
	at sbt.internal.XMainConfiguration.run(XMainConfiguration.java:59)
	at sbt.xMain.run(Main.scala:46)
	at xsbt.boot.Launch$$anonfun$run$1.apply(Launch.scala:109)
	at xsbt.boot.Launch$.withContextLoader(Launch.scala:128)
	at xsbt.boot.Launch$.run(Launch.scala:109)
	at xsbt.boot.Launch$$anonfun$apply$1.apply(Launch.scala:35)
	at xsbt.boot.Launch$.launch(Launch.scala:117)
	at xsbt.boot.Launch$.apply(Launch.scala:18)
	at xsbt.boot.Boot$.runImpl(Boot.scala:41)
	at xsbt.boot.Boot$.main(Boot.scala:17)
	at xsbt.boot.Boot.main(Boot.scala)
Error during sbt execution: java.lang.ClassCastException: class java.lang.UnsupportedOperationException cannot be cast to class xsbti.FullReload (java.lang.UnsupportedOperationException is in module java.base of loader 'bootstrap'; xsbti.FullReload is in unnamed module of loader 'app')
```
this error is caused because jdk20 compability error with stb lib.
you should install jdk11 and rename the java from conda to .java, in order to use the system installed jdk11.
after that, coninue to `./build-step.sh riscv-tools` step of https://inst.eecs.berkeley.edu/~cs152/sp23/assets/labs/lab1.pdf

you should see this msg in shell:
```
/data/tangke/chipyard-cs152-sp23
/data/tangke/chipyard-cs152-sp23/generators/constellation /data/tangke/chipyard-cs152-sp23
Cleared directory 'espresso'
Submodule 'espresso' (https://github.com/chipsalliance/espresso.git) unregistered for path 'espresso'
/data/tangke/chipyard-cs152-sp23
/data/tangke/chipyard-cs152-sp23/tools/api-config-chipsalliance /data/tangke/chipyard-cs152-sp23
/data/tangke/chipyard-cs152-sp23
/data/tangke/chipyard-cs152-sp23/generators/cva6/src/main/resources/vsrc /data/tangke/chipyard-cs152-sp23
Cleared directory 'cva6'
Submodule 'src/main/resources/vsrc/cva6' (https://github.com/openhwgroup/cva6.git) unregistered for path 'cva6'
/data/tangke/chipyard-cs152-sp23
Setup complete!
```

the lab1.pdf later requires you execute this commands:
```
eecs$ CHIPYARDROOT=$PWD
eecs$ BMARKS=$CHIPYARDROOT/generators/riscv-sodor/riscv-bmarks
eecs$ SCRIPTS=$CHIPYARDROOT/generators/riscv-sodor/scripts
eecs$ source ./env.sh
```
you have to pay attention to content of env.sh as above, such as modify the path of your local path, rather a ucb official server.

then, you should execute a make command to simulate a non pipeline processor.

you would encounter this error:
```
%Warning-WIDTHEXPAND: /data/tangke/chipyard-cs152-sp23/sims/verilator/generated-src/chipyard.TestHarness.Sodor1StageConfig/gen-collateral/AsyncQueueSink_3.sv:157:28: Operator XOR expects 32 or 6 bits on the LHS, but LHS's SEL generates 3 bits.
                                                                                                                                                                    : ... In instance TestHarness.bits_in_queue.sink
  157 |     .io_d  (_GEN[ridx[2:0] ^ {ridx[3], 2'h0}]),  
      |                            ^
                      ... For warning description see https://verilator.org/warn/WIDTHEXPAND?v=5.008
                      ... Use "/* verilator lint_off WIDTHEXPAND */" and lint_on around source to disable this message.
%Warning-WIDTHEXPAND: /data/tangke/chipyard-cs152-sp23/sims/verilator/generated-src/chipyard.TestHarness.Sodor1StageConfig/gen-collateral/AsyncQueueSink_3.sv:157:28: Operator XOR expects 32 or 6 bits on the RHS, but RHS's REPLICATE generates 3 bits.
                                                                                                                                                                    : ... In instance TestHarness.bits_in_queue.sink
  157 |     .io_d  (_GEN[ridx[2:0] ^ {ridx[3], 2'h0}]),  
      |                            ^
%Error-NEEDTIMINGOPT: /data/tangke/chipyard-cs152-sp23/sims/verilator/generated-src/chipyard.TestHarness.Sodor1StageConfig/gen-collateral/SimJTAG.v:43:17: Use --timing or --no-timing to specify how delays should be handled
                                                                                                                                                         : ... In instance TestHarness.SimJTAG
   43 |    wire         #0.1 __jtag_TDO = jtag_TDO_driven ? 
      |                 ^
%Error-NEEDTIMINGOPT: /data/tangke/chipyard-cs152-sp23/sims/verilator/generated-src/chipyard.TestHarness.Sodor1StageConfig/gen-collateral/SimJTAG.v:54:11: Use --timing or --no-timing to specify how timing controls should be handled
                                                                                                                                                         : ... In instance TestHarness.SimJTAG
   54 |    assign #0.1 jtag_TCK   = __jtag_TCK;
      |           ^
%Error-NEEDTIMINGOPT: /data/tangke/chipyard-cs152-sp23/sims/verilator/generated-src/chipyard.TestHarness.Sodor1StageConfig/gen-collateral/SimJTAG.v:55:11: Use --timing or --no-timing to specify how timing controls should be handled
                                                                                                                                                         : ... In instance TestHarness.SimJTAG
   55 |    assign #0.1 jtag_TMS   = __jtag_TMS;
      |           ^
%Error-NEEDTIMINGOPT: /data/tangke/chipyard-cs152-sp23/sims/verilator/generated-src/chipyard.TestHarness.Sodor1StageConfig/gen-collateral/SimJTAG.v:56:11: Use --timing or --no-timing to specify how timing controls should be handled
                                                                                                                                                         : ... In instance TestHarness.SimJTAG
   56 |    assign #0.1 jtag_TDI   = __jtag_TDI;
      |           ^
%Error-NEEDTIMINGOPT: /data/tangke/chipyard-cs152-sp23/sims/verilator/generated-src/chipyard.TestHarness.Sodor1StageConfig/gen-collateral/SimJTAG.v:57:11: Use --timing or --no-timing to specify how timing controls should be handled
                                                                                                                                                         : ... In instance TestHarness.SimJTAG
   57 |    assign #0.1 jtag_TRSTn = __jtag_TRSTn;
      |           ^
%Error-NEEDTIMINGOPT: /data/tangke/chipyard-cs152-sp23/sims/verilator/generated-src/chipyard.TestHarness.Sodor1StageConfig/gen-collateral/SimJTAG.v:59:11: Use --timing or --no-timing to specify how timing controls should be handled
                                                                                                                                                         : ... In instance TestHarness.SimJTAG
   59 |    assign #0.1 exit = __exit;
      |           ^
%Error: Exiting due to 6 error(s)
```

you should turn to this following content in chinese.




# 如何配置lab1环境
将开源的chipyard clone(https://github.com/ucb-bar/chipyard)下来，里面会有一个.conda_env
如果命令中遇到任何需要activate .conda-env的，都可以activate 这个.conda-env
lab文档中可能一些脚本会写死到一个官方教学机器目录上，本地上就按照自己的目录结构改一下

```
eecs$ echo 'source ~/.bashrc' >> ~/.bash_profile
eecs$ echo 'export ENABLE_SBT_THIN_CLIENT=1' >> ~/.bashrc
eecs$ mkdir -m 0700 -p /scratch/$USER
eecs$ cd /scratch/$USER
eecs$ wget -O Miniforge3.sh \
"https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
eecs$ bash Miniforge3.sh -p "/scratch/${USER}/conda"
eecs$ source /scratch/${USER}/conda/etc/profile.d/conda.sh
eecs$ conda activate /home/ff/cs152/sp23/chipyard-cs152-sp23/.conda-env
eecs$ git clone https://github.com/ucb-bar/chipyard-cs152-sp23
eecs$ cd chipyard-cs152-sp23
eecs$ git checkout main
eecs$ ./build-setup.sh riscv-tools
```
实验前都是用下面的命令激活环境
```
eecs$ CHIPYARDROOT=$PWD
eecs$ BMARKS=$CHIPYARDROOT/generators/riscv-sodor/riscv-bmarks
eecs$ SCRIPTS=$CHIPYARDROOT/generators/riscv-sodor/scripts
eecs$ source ./env.sh
```

可能遇到的第一个问题是stb版本问题，这个conda会装一个jdk20，然后stb编译会有问题，可能是jdk20比较新，还没有修复，所以可以找一下which java, 把这个java改成系统自己安装的java, 我这里是java 11。就可以跑通build-setup.sh riscv-tools

遇到的第二个问题是下面这个命令编译时遇到的
```
eecs$ cd ${CHIPYARDROOT}/sims/verilator
eecs$ make CONFIG=Sodor1StageConfig
```
报错如下：我本地是有6个类似如下的error，[error]这个不是错误
```
%Error-NEEDTIMINGOPT: /home/tangke/cs152/chipyard-cs152-sp23/sims/verilator/generated-src/chipyard.TestHarness.Sodor1StageConfig/gen-collateral/SimJTAG.v:43:17: Use --timing or --no-timing to specify how delays should be handled
: ... In instance TestHarness.SimJTAG
43 | wire #0.1 __jtag_TDO = jtag_TDO_driven ?
```

gpt说

1.
```
这个错误是由于 Verilator 对于模拟代码中的延迟处理方式的要求。Verilator 是一个高性能的硬件描述语言（HDL）模拟器，它可以将 Verilog 或 SystemVerilog 代码转换成 C++ 或 SystemC 代码。

代码中的 `#0.1` 是 Verilog 的延迟语法，表示要在此处引入一个延迟。Verilator 需要知道如何处理这些延迟，因此它要求用户在命令行中使用 `--timing` 或 `--no-timing` 选项来指定。

- `--timing`：这个选项表示要考虑延迟。Verilator 会在生成的 C++ 代码中加入适当的延迟。这会使得模拟更加准确，但也可能使模拟速度变慢。

- `--no-timing`：这个选项表示忽略延迟。Verilator 不会在生成的 C++ 代码中加入任何延迟，这使得模拟速度更快，但可能会牺牲一些准确性。

你可以根据你的需求选择合适的选项。比如，如果你想忽略延迟，你可以在 Verilator 的命令行中加入 `--no-timing` 选项：


verilator --no-timing ...


替换 `...` 为你的其他 Verilator 命令行选项和参数。
```

2.
```
你的错误信息和这个GitHub issue链接强相关：[https://github.com/ucb-bar/riscv-mini/issues/31 ↗](https://github.com/ucb-bar/riscv-mini/issues/31)。这个issue的内容提到，当你使用的Verilator版本大于4.016时，你需要在Verilator的命令行中添加 `--max-num-width` 参数来支持非常宽的线（very wide wires）。

你的makefile中已经包含了这个解决方案。在makefile中，这一行代码：


MAX_WIDTH_OPTS = $(shell verilator --version | perl -lne 'if (/(\d.\d+)/ && $$1 > 4.016) { print "--max-num-width 1048576"; }')


检查了你的verilator版本，并在版本号大于4.016时添加了 `--max-num-width 1048576` 参数。

所以，根据你的makefile，如果你的verilator版本大于4.016，它应该已经自动处理了这个问题。如果你还是遇到这个问题，你应该检查一下你的verilator版本，确保它的版本号大于4.016。如果你的verilator版本小于4.016，你可能需要更新你的verilator版本。

如果问题依然存在，你可能需要检查你的makefile是否正确地执行了这个命令，也就是说，你需要检查 `MAX_WIDTH_OPTS` 变量是否被正确地设置和使用。
```

因此，我修改了makefile，因为我环境中的verilog是大于4.016的，所以第一个修改是把--max-num-width改成强制启用了
```
# see: https://github.com/ucb-bar/riscv-mini/issues/31
# MAX_WIDTH_OPTS = $(shell verilator --version | perl -lne 'if (/(\d.\d+)/ && $$1 > 4.016) { print "--max-num-width 1048576"; }')
MAX_WIDTH_OPTS = --max-num-width 1048576
```
第二个修改是，增加了--timing选项
```
TIMING_OPTS = --timing
VERILATOR_NONCC_OPTS = \
	$(RUNTIME_PROFILING_VFLAGS) \
	$(RUNTIME_THREADS) \
	$(VERILATOR_OPT_FLAGS) \
	$(PLATFORM_OPTS) \
	-Wno-fatal \
	$(TIMESCALE_OPTS) \
	$(MAX_WIDTH_OPTS) \
	$(PREPROC_DEFINES) \
	--top-module $(VLOG_MODEL) \
	--vpi \
	-f $(sim_common_files) \
	$(TIMING_OPTS)
```

至此，编译成功。
make下面的目标来检测输出内容
```
make CONFIG=Sodor1StageConfig run-binary BINARY=${BMARKS}/towers.riscv
```

输出的结尾如下：
```
/home/tangke/cs152/chipyard/.conda-env/bin/x86_64-conda-linux-gnu-c++    SimDRAM.o SimDTM.o SimJTAG.o SimSerial.o SimUART.o emulator.o mm.o mm_dramsim2.o remote_bitbang.o testchip_tsi.o uart.o verilated.o verilated_dpi.o verilated_vpi.o verilated_timing.o verilated_threads.o VTestHarness__ALL.a   -L/home/tangke/cs1
52/chipyard/.conda-env/riscv-tools/lib -Wl,-rpath,/home/tangke/cs152/chipyard/.conda-env/riscv-tools/lib -L/home/tangke/cs152/chipyard-cs152-sp23/sims/verilator -L/home/tangke/cs152/chipyard-cs152-sp23/tools/DRAMSim2 -lfesvr -ldramsim  -pthread -lpthread -latomic   -o /home/tangke/cs152/chipyard-cs152-sp23/sims/ver
ilator/simulator-chipyard-Sodor1StageConfig
rm VTestHarness__ALL.verilator_deplist.tmp
make[1]: Leaving directory '/home/tangke/cs152/chipyard-cs152-sp23/sims/verilator/generated-src/chipyard.TestHarness.Sodor1StageConfig/chipyard.TestHarness.Sodor1StageConfig'
(/home/tangke/cs152/chipyard/.conda-env) tangke@tangke:~/cs152/chipyard-cs152-sp23/sims/verilator$ make CONFIG=Sodor1StageConfig run-binary BINARY=${BMARKS}/towers.riscv
Running with RISCV=/home/tangke/cs152/chipyard/.conda-env/riscv-tools
mkdir -p /home/tangke/cs152/chipyard-cs152-sp23/sims/verilator/output/chipyard.TestHarness.Sodor1StageConfig
(set -o pipefail &&  /home/tangke/cs152/chipyard-cs152-sp23/sims/verilator/simulator-chipyard-Sodor1StageConfig +permissive +dramsim +dramsim_ini_dir=/home/tangke/cs152/chipyard-cs152-sp23/generators/testchipip/src/main/resources/dramsim2_ini +max-cycles=10000000   +verbose +permissive-off /home/tangke/cs152/chipya
rd-cs152-sp23/generators/riscv-sodor/riscv-bmarks/towers.riscv </dev/null 2> >(spike-dasm > /home/tangke/cs152/chipyard-cs152-sp23/sims/verilator/output/chipyard.TestHarness.Sodor1StageConfig/towers.out) | tee /home/tangke/cs152/chipyard-cs152-sp23/sims/verilator/output/chipyard.TestHarness.Sodor1StageConfig/towers
.log)
mcycle = 6166
minstret = 6172
[UART] UART0 is here (stdin/stdout).
```
可以看到这里打印了`mcycle`和`minstret`，所以就完成了环境配置。

**以上内容，根据文档(https://inst.eecs.berkeley.edu/~cs152/sp23/assets/labs/lab1.pdf)进行配置**
