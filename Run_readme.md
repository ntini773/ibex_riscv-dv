# RISC-V DV (Design Verification) Framework - Complete Guide

## Overview

The ibex_riscv-dv is a comprehensive RISC-V instruction generator framework designed to create random assembly programs for testing RISC-V processors. It supports both SystemVerilog (UVM) and Python (pyflow) simulators, providing a robust platform for processor verification.

## Table of Contents

1. [Framework Architecture](#framework-architecture)
2. [Command Flow Analysis](#command-flow-analysis)
3. [File Generation Process](#file-generation-process)
4. [Configuration System](#configuration-system)
5. [Directory Structure](#directory-structure)
6. [Usage Examples](#usage-examples)
7. [Advanced Features](#advanced-features)

## Framework Architecture

### Core Components

1. **Test Runner (`run.py`)**: Main entry point that orchestrates the entire test generation process
2. **Python Generator (`pygen/`)**: Python-based instruction generator using pyflow simulator
3. **SystemVerilog Generator (`src/`)**: UVM-based instruction generator for traditional simulators
4. **Configuration Files (`yaml/`)**: Test specifications and simulator configurations
5. **Target Configurations (`target/`)**: Processor-specific settings for different RISC-V implementations

### Key Files and Their Roles

- `run.py`: Main orchestration script
- `pygen/pygen_src/riscv_asm_program_gen.py`: Core assembly program generation class
- `yaml/base_testlist.yaml`: Test definitions and configurations
- `yaml/simulator.yaml`: Simulator-specific command configurations
- `target/rv32imc/riscv_core_setting.sv`: Processor feature configuration

## Command Flow Analysis

### Example Command
```bash
python3 run.py --test=riscv_arithmetic_basic_test --simulator=pyflow
#If you want to run with specific steps:
python3 run.py --test=riscv_arithmetic_basic_test --simulator=pyflow --steps=gen,gcc_compile,iss_sim
```

```bash
args.test = "riscv_arithmetic_basic_test"
args.simulator = "pyflow"
args.target = "rv32imc"                # default
args.o = None                          # output dir (default: None)
args.testlist = ""                     # default -> args.testlist = cwd + "/target/" + args.target + "/testlist.yaml"
args.iterations = 0                    # default
args.iss = "spike"                     # default
args.verbose = False                   # default
args.co = False                        # default
args.cov = False                       # default
args.so = False                        # default
args.cmp_opts = ""                     # default
args.sim_opts = ""                     # default
args.gcc_opts = ""                     # default
args.steps = "all"                     # default
args.lsf_cmd = ""                      # default
args.isa = ""                          # will be set by load_config() -> args.isa = "rv32imc_zicsr_zifencei"
args.priv = "m"                        # default
args.mabi = ""                         # will be set by load_config() -> args.mabi = "ilp32"
args.gen_timeout = 360                 # default -> for pyflow , its changed to 1200 in the process if not specified by user
args.end_signature_addr = "0"          # default
args.iss_opts = ""                     # default
args.iss_timeout = 10                  # default
args.iss_yaml = ""                     # will be set by load_config() -> args.iss_yaml = cwd + "/yaml/iss.yaml"
args.simulator_yaml = ""               # will be set by load_config() ->  args.simulator_yaml = cwd + "/yaml/simulator.yaml"
args.csr_yaml = ""                     # will be set by load_config() -> args.csr_yaml = cwd + "/yaml/csr_template.yaml"
args.custom_target = ""                # default -> if set , it should have testlist.yaml 
args.core_setting_dir = ""             # will be set by load_config() -> args.core_setting_dir = cwd + "/pygen/pygen_src/target/" + args.target
args.user_extension_dir = ""           # default
args.asm_test = ""                     # default
args.c_test = ""                       # default
args.log_suffix = ""                   # default
args.exp = False                       # default
args.batch_size = 0                    # default 
args.stop_on_first_error = False       # default
args.noclean = True                    # default
args.verilog_style_check = False       # default
args.debug = ""                        # default
args.start_seed = None                 # default
args.seed = None                       # default
args.seed_yaml = None                  # default
```
```
If custom target is specified:
args.core_setting_dir =args.custom_target
args.testlist = args.custom_target + "/testlist.yaml"
args.mabi, args.isa must be specified
```

```bash
GCC command for .o file : /home/nitin/projects/riscv-verification/riscv-gnu-toolchain/install/bin/riscv32-unknown-elf-gcc -static -mcmodel=medany              -fvisibility=hidden -nostdlib              -nostartfiles out_2025-07-14/asm_test/riscv_arithmetic_basic_test_1.S              -I/home/nitin/ibex_riscv-dv/user_extension              -T/home/nitin/ibex_riscv-dv/scripts/link.ld  -o out_2025-07-14/asm_test/riscv_arithmetic_basic_test_1.o  -march=rv32imc_zicsr_zifencei -mabi=ilp32

GCC command for .bin file : /home/nitin/projects/riscv-verification/riscv-gnu-toolchain/install/bin/riscv32-unknown-elf-objcopy -O binary out_2025-07-14/asm_test/riscv_arithmetic_basic_test_1.o out_2025-07-14/asm_test/riscv_arithmetic_basic_test_1.bin

ISS command: /home/nitin/.local/bin//spike --log-commits --isa=rv32imc_zicsr_zifencei --priv=m --misaligned -l out_2025-07-14/asm_test/riscv_arithmetic_basic_test_0.o &> out_2025-07-14/spike_sim/riscv_arithmetic_basic_test_0.log

Generator options: --instr_cnt=100 --num_of_sub_program=0 --directed_instr_0=riscv_int_numeric_corner_stream,4 --no_fence=1 --no_data_page=1 --no_branch_jump=1 --boot_mode=m --no_csr_instr=1

Command to run at do_simulate():  python3 /home/nitin/ibex_riscv-dv/pygen/pygen_src/test/riscv_instr_base_test.py --num_of_tests=2 --start_idx=0 --asm_file_name=out_2025-07-15/asm_test/riscv_arithmetic_basic_test --log_file_name=out_2025-07-15/sim_riscv_arithmetic_basic_test_0.log  --target=rv32imc  --gen_test=riscv_instr_base_test  --seed=493738672 --instr_cnt=100 --num_of_sub_program=0 --directed_instr_0=riscv_int_numeric_corner_stream,4 --no_fence=1 --no_data_page=1 --no_branch_jump=1 --boot_mode=m --no_csr_instr=1

```

```bash
# When we run base_test , the configs are
cfg.argv values:
cfg.argv.num_of_tests = 2
cfg.argv.enable_page_table_exception = 0
cfg.argv.enable_interrupt = 0
cfg.argv.enable_nested_interrupt = 0
cfg.argv.enable_timer_irq = 0
cfg.argv.num_of_sub_program = 0
cfg.argv.instr_cnt = 100
cfg.argv.tvec_alignment = 2
cfg.argv.no_ebreak = 1
cfg.argv.no_dret = 1
cfg.argv.no_wfi = 1
cfg.argv.no_branch_jump = 1
cfg.argv.no_load_store = 0
cfg.argv.no_csr_instr = 1
cfg.argv.fix_sp = 0
cfg.argv.use_push_data_section = 0
cfg.argv.enable_illegal_csr_instruction = 0
cfg.argv.enable_access_invalid_csr_level = 0
cfg.argv.enable_misaligned_instr = 0
cfg.argv.enable_dummy_csr_write = 0
cfg.argv.allow_sfence_exception = 0
cfg.argv.no_data_page = 1
cfg.argv.no_directed_instr = 0
cfg.argv.no_fence = 1
cfg.argv.no_delegation = 1
cfg.argv.illegal_instr_ratio = 0
cfg.argv.hint_instr_ratio = 0
cfg.argv.num_of_harts = None
cfg.argv.enable_unaligned_load_store = 0
cfg.argv.force_m_delegation = 0
cfg.argv.force_s_delegation = 0
cfg.argv.require_signature_addr = 0
cfg.argv.signature_addr = 3735928559
cfg.argv.disable_compressed_instr = 0
cfg.argv.randomize_csr = 0
cfg.argv.gen_debug_section = 0
cfg.argv.bare_program_mode = 0
cfg.argv.num_debug_sub_program = 0
cfg.argv.enable_ebreak_in_debug_rom = 0
cfg.argv.set_dcsr_ebreak = 0
cfg.argv.enable_debug_single_step = 0
cfg.argv.set_mstatus_tw = 0
cfg.argv.set_mstatus_mprv = 0
cfg.argv.enable_floating_point = 0
cfg.argv.enable_vector_extension = 0
cfg.argv.enable_b_extension = 0
cfg.argv.enable_bitmanip_groups = ['ZBB', 'ZBS', 'ZBP', 'ZBE', 'ZBF', 'ZBC', 'ZBR', 'ZBM', 'ZBT', 'ZB_TMP']
cfg.argv.boot_mode = 'm'
cfg.argv.asm_test_suffix = ''
cfg.argv.march_isa = []
cfg.argv.directed_instr_0 = 'riscv_int_numeric_corner_stream,4'
cfg.argv.stream_name_0 = ''
cfg.argv.stream_freq_0 = 4
cfg.argv.directed_instr_1 = ''
cfg.argv.stream_name_1 = ''
cfg.argv.stream_freq_1 = 4
cfg.argv.directed_instr_2 = ''
cfg.argv.stream_name_2 = ''
cfg.argv.stream_freq_2 = 4
cfg.argv.directed_instr_3 = ''
cfg.argv.stream_name_3 = ''
cfg.argv.stream_freq_3 = 4
cfg.argv.directed_instr_4 = ''
cfg.argv.stream_name_4 = ''
cfg.argv.stream_freq_4 = 4
cfg.argv.directed_instr_5 = ''
cfg.argv.stream_name_5 = ''
cfg.argv.stream_freq_5 = 4
cfg.argv.directed_instr_6 = ''
cfg.argv.stream_name_6 = ''
cfg.argv.stream_freq_6 = 4
cfg.argv.directed_instr_7 = ''
cfg.argv.stream_name_7 = ''
cfg.argv.stream_freq_7 = 4
cfg.argv.directed_instr_8 = ''
cfg.argv.stream_name_8 = ''
cfg.argv.stream_freq_8 = 4
cfg.argv.directed_instr_9 = ''
cfg.argv.stream_name_9 = ''
cfg.argv.stream_freq_9 = 4
cfg.argv.directed_instr_10 = ''
cfg.argv.stream_name_10 = ''
cfg.argv.stream_freq_10 = 4
cfg.argv.directed_instr_11 = ''
cfg.argv.stream_name_11 = ''
cfg.argv.stream_freq_11 = 4
cfg.argv.directed_instr_12 = ''
cfg.argv.stream_name_12 = ''
cfg.argv.stream_freq_12 = 4
cfg.argv.directed_instr_13 = ''
cfg.argv.stream_name_13 = ''
cfg.argv.stream_freq_13 = 4
cfg.argv.directed_instr_14 = ''
cfg.argv.stream_name_14 = ''
cfg.argv.stream_freq_14 = 4
cfg.argv.directed_instr_15 = ''
cfg.argv.stream_name_15 = ''
cfg.argv.stream_freq_15 = 4
cfg.argv.directed_instr_16 = ''
cfg.argv.stream_name_16 = ''
cfg.argv.stream_freq_16 = 4
cfg.argv.directed_instr_17 = ''
cfg.argv.stream_name_17 = ''
cfg.argv.stream_freq_17 = 4
cfg.argv.directed_instr_18 = ''
cfg.argv.stream_name_18 = ''
cfg.argv.stream_freq_18 = 4
cfg.argv.directed_instr_19 = ''
cfg.argv.stream_name_19 = ''
cfg.argv.stream_freq_19 = 4
cfg.argv.start_idx = 0
cfg.argv.asm_file_name = 'out_2025-07-15/asm_test/riscv_arithmetic_basic_test'
cfg.argv.log_file_name = 'out_2025-07-15/sim_riscv_arithmetic_basic_test_0.log'
cfg.argv.target = 'rv32imc'
cfg.argv.gen_test = 'riscv_instr_base_test'
cfg.argv.enable_visualization = False
cfg.argv.trace_csv = ''
cfg.argv.seed = '14826882'
```

```bash
# Sample cfg values generated when riscv_arithmetic_basic_test is run
2025-07-15 19:11:58,526 riscv_instr_base_test.py 87 INFO cfg parameters:
2025-07-15 19:11:58,526 riscv_instr_base_test.py 89 INFO cfg._ro_int = <vsc.impl.randobj_int.RandObjInt object at 0x7791025f1180>
2025-07-15 19:11:58,534 riscv_instr_base_test.py 89 INFO cfg.tname = 'riscv_instr_gen_config'
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg._int_field_info = <vsc.types.field_info object at 0x77910249c250>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.main_program_instr_cnt = <vsc.types.rand_int32_t object at 0x77910249c220>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.sub_program_instr_cnt = <vsc.types.randsz_list_t object at 0x77910249c3a0>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.debug_program_instr_cnt = 0
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.debug_sub_program_instr_cnt = <vsc.types.randsz_list_t object at 0x77910249c460>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.data_page_pattern = <vsc.types.rand_enum_t object at 0x77910249c4c0>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.vreg_init_method = <vreg_init_method_t.RANDOM_VALUES_VMV: 1>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.max_directed_instr_stream_seq = 20
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.argv = Namespace(num_of_tests=2, enable_page_table_exception=0, enable_interrupt=0, enable_nested_interrupt=0, enable_timer_irq=0, num_of_sub_program=0, instr_cnt=100, tvec_alignment=2, no_ebreak=1, no_dret=1, no_wfi=1, no_branch_jump=1, no_load_store=0, no_csr_instr=1, fix_sp=0, use_push_data_section=0, enable_illegal_csr_instruction=0, enable_access_invalid_csr_level=0, enable_misaligned_instr=0, enable_dummy_csr_write=0, allow_sfence_exception=0, no_data_page=1, no_directed_instr=0, no_fence=1, no_delegation=1, illegal_instr_ratio=0, hint_instr_ratio=0, num_of_harts=None, enable_unaligned_load_store=0, force_m_delegation=0, force_s_delegation=0, require_signature_addr=0, signature_addr=3735928559, disable_compressed_instr=0, randomize_csr=0, gen_debug_section=0, bare_program_mode=0, num_debug_sub_program=0, enable_ebreak_in_debug_rom=0, set_dcsr_ebreak=0, enable_debug_single_step=0, set_mstatus_tw=0, set_mstatus_mprv=0, enable_floating_point=0, enable_vector_extension=0, enable_b_extension=0, enable_bitmanip_groups=['ZBB', 'ZBS', 'ZBP', 'ZBE', 'ZBF', 'ZBC', 'ZBR', 'ZBM', 'ZBT', 'ZB_TMP'], boot_mode='m', asm_test_suffix='', march_isa=[], directed_instr_0='riscv_int_numeric_corner_stream,4', stream_name_0='', stream_freq_0=4, directed_instr_1='', stream_name_1='', stream_freq_1=4, directed_instr_2='', stream_name_2='', stream_freq_2=4, directed_instr_3='', stream_name_3='', stream_freq_3=4, directed_instr_4='', stream_name_4='', stream_freq_4=4, directed_instr_5='', stream_name_5='', stream_freq_5=4, directed_instr_6='', stream_name_6='', stream_freq_6=4, directed_instr_7='', stream_name_7='', stream_freq_7=4, directed_instr_8='', stream_name_8='', stream_freq_8=4, directed_instr_9='', stream_name_9='', stream_freq_9=4, directed_instr_10='', stream_name_10='', stream_freq_10=4, directed_instr_11='', stream_name_11='', stream_freq_11=4, directed_instr_12='', stream_name_12='', stream_freq_12=4, directed_instr_13='', stream_name_13='', stream_freq_13=4, directed_instr_14='', stream_name_14='', stream_freq_14=4, directed_instr_15='', stream_name_15='', stream_freq_15=4, directed_instr_16='', stream_name_16='', stream_freq_16=4, directed_instr_17='', stream_name_17='', stream_freq_17=4, directed_instr_18='', stream_name_18='', stream_freq_18=4, directed_instr_19='', stream_name_19='', stream_freq_19=4, start_idx=0, asm_file_name='out_2025-07-15/asm_test/riscv_arithmetic_basic_test', log_file_name='out_2025-07-15/sim_riscv_arithmetic_basic_test_0.log', target='rv32imc', gen_test='riscv_instr_base_test', enable_visualization=False, trace_csv='', seed='891294050')
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.args_dict = {'num_of_tests': 2, 'enable_page_table_exception': 0, 'enable_interrupt': 0, 'enable_nested_interrupt': 0, 'enable_timer_irq': 0, 'num_of_sub_program': 0, 'instr_cnt': 100, 'tvec_alignment': 2, 'no_ebreak': 1, 'no_dret': 1, 'no_wfi': 1, 'no_branch_jump': 1, 'no_load_store': 0, 'no_csr_instr': 1, 'fix_sp': 0, 'use_push_data_section': 0, 'enable_illegal_csr_instruction': 0, 'enable_access_invalid_csr_level': 0, 'enable_misaligned_instr': 0, 'enable_dummy_csr_write': 0, 'allow_sfence_exception': 0, 'no_data_page': 1, 'no_directed_instr': 0, 'no_fence': 1, 'no_delegation': 1, 'illegal_instr_ratio': 0, 'hint_instr_ratio': 0, 'num_of_harts': None, 'enable_unaligned_load_store': 0, 'force_m_delegation': 0, 'force_s_delegation': 0, 'require_signature_addr': 0, 'signature_addr': 3735928559, 'disable_compressed_instr': 0, 'randomize_csr': 0, 'gen_debug_section': 0, 'bare_program_mode': 0, 'num_debug_sub_program': 0, 'enable_ebreak_in_debug_rom': 0, 'set_dcsr_ebreak': 0, 'enable_debug_single_step': 0, 'set_mstatus_tw': 0, 'set_mstatus_mprv': 0, 'enable_floating_point': 0, 'enable_vector_extension': 0, 'enable_b_extension': 0, 'enable_bitmanip_groups': ['ZBB', 'ZBS', 'ZBP', 'ZBE', 'ZBF', 'ZBC', 'ZBR', 'ZBM', 'ZBT', 'ZB_TMP'], 'boot_mode': 'm', 'asm_test_suffix': '', 'march_isa': [], 'directed_instr_0': 'riscv_int_numeric_corner_stream,4', 'stream_name_0': '', 'stream_freq_0': 4, 'directed_instr_1': '', 'stream_name_1': '', 'stream_freq_1': 4, 'directed_instr_2': '', 'stream_name_2': '', 'stream_freq_2': 4, 'directed_instr_3': '', 'stream_name_3': '', 'stream_freq_3': 4, 'directed_instr_4': '', 'stream_name_4': '', 'stream_freq_4': 4, 'directed_instr_5': '', 'stream_name_5': '', 'stream_freq_5': 4, 'directed_instr_6': '', 'stream_name_6': '', 'stream_freq_6': 4, 'directed_instr_7': '', 'stream_name_7': '', 'stream_freq_7': 4, 'directed_instr_8': '', 'stream_name_8': '', 'stream_freq_8': 4, 'directed_instr_9': '', 'stream_name_9': '', 'stream_freq_9': 4, 'directed_instr_10': '', 'stream_name_10': '', 'stream_freq_10': 4, 'directed_instr_11': '', 'stream_name_11': '', 'stream_freq_11': 4, 'directed_instr_12': '', 'stream_name_12': '', 'stream_freq_12': 4, 'directed_instr_13': '', 'stream_name_13': '', 'stream_freq_13': 4, 'directed_instr_14': '', 'stream_name_14': '', 'stream_freq_14': 4, 'directed_instr_15': '', 'stream_name_15': '', 'stream_freq_15': 4, 'directed_instr_16': '', 'stream_name_16': '', 'stream_freq_16': 4, 'directed_instr_17': '', 'stream_name_17': '', 'stream_freq_17': 4, 'directed_instr_18': '', 'stream_name_18': '', 'stream_freq_18': 4, 'directed_instr_19': '', 'stream_name_19': '', 'stream_freq_19': 4, 'start_idx': 0, 'asm_file_name': 'out_2025-07-15/asm_test/riscv_arithmetic_basic_test', 'log_file_name': 'out_2025-07-15/sim_riscv_arithmetic_basic_test_0.log', 'target': 'rv32imc', 'gen_test': 'riscv_instr_base_test', 'enable_visualization': False, 'trace_csv': '', 'seed': '891294050'}
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.m_mode_exception_delegation = {}
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.s_mode_exception_delegation = {}
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.m_mode_interrupt_delegation = {}
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.s_mode_interrupt_delegation = {}
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.init_privileged_mode = <privileged_mode_t.MACHINE_MODE: 3>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.mstatus = <vsc.types.rand_bit_t object at 0x77910249c550>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.mie = <vsc.types.rand_bit_t object at 0x77910249fe50>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.sstatus = <vsc.types.rand_bit_t object at 0x7791024b40d0>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.sie = <vsc.types.rand_bit_t object at 0x7791024b41f0>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.ustatus = <vsc.types.rand_bit_t object at 0x7791024b4280>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.uie = <vsc.types.rand_bit_t object at 0x7791024b4310>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.mstatus_mprv = <vsc.types.rand_bit_t object at 0x7791024b43a0>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.mstatus_mxr = <vsc.types.rand_bit_t object at 0x7791024b4430>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.mstatus_sum = <vsc.types.rand_bit_t object at 0x7791024b44c0>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.mstatus_tvm = <vsc.types.rand_bit_t object at 0x7791024b4550>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.mstatus_fs = <vsc.types.rand_bit_t object at 0x7791024b45e0>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.mstatus_vs = <vsc.types.rand_bit_t object at 0x7791024b4670>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.mtvec_mode = <vsc.types.rand_enum_t object at 0x7791024b4700>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.tvec_alignment = <vsc.types.rand_uint32_t object at 0x7791024b47c0>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.fcsr_rm = <vsc.types.rand_enum_t object at 0x7791024b4850>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.enable_sfence = <vsc.types.rand_bit_t object at 0x7791024b4910>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.gpr = <vsc.types.rand_list_t object at 0x7791024b4a30>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.scratch_reg = <vsc.types.rand_enum_t object at 0x7791024b4a90>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.pmp_reg = <vsc.types.rand_enum_t object at 0x7791024b4b20>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.sp = <vsc.types.rand_enum_t object at 0x7791024b4b80>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.tp = <vsc.types.rand_enum_t object at 0x7791024b4be0>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.ra = <vsc.types.rand_enum_t object at 0x7791024b4c40>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.check_misa_init_val = 0
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.check_xstatus = 1
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.virtual_addr_translation_on = <vsc.types.rand_bit_t object at 0x7791024b4ca0>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.stack_len = 5000
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.mem_region = <vsc.types.list_t object at 0x7791024b4fa0>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.amo_region = <vsc.types.list_t object at 0x7791024b5390>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.s_mem_region = <vsc.types.list_t object at 0x7791024b5780>
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.kernel_stack_len = 4000
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.kernel_program_instr_cnt = 400
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.invalid_priv_mode_csrs = []
2025-07-15 19:11:58,535 riscv_instr_base_test.py 89 INFO cfg.num_of_sub_program = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.instr_cnt = 100
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.num_of_tests = 2
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.no_data_page = 1
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.no_branch_jump = 1
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.no_load_store = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.no_csr_instr = 1
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.no_ebreak = 1
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.no_dret = 1
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.no_fence = 1
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.no_wfi = 1
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.enable_unaligned_load_store = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.illegal_instr_ratio = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.hint_instr_ratio = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.num_of_harts = 1
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.fix_sp = <vsc.types.bit_t object at 0x77910249cac0>
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.use_push_data_section = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.boot_mode_opts = 'm'
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.enable_page_table_exception = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.no_directed_instr = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.asm_test_suffix = ''
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.enable_interrupt = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.enable_nested_interrupt = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.enable_timer_irq = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.bare_program_mode = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.enable_illegal_csr_instruction = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.enable_access_invalid_csr_level = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.enable_misaligned_instr = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.enable_dummy_csr_write = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.randomize_csr = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.allow_sfence_exception = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.no_delegation = 1
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.force_m_delegation = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.force_s_delegation = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.support_supervisor_mode = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.disable_compressed_instr = <vsc.types.uint8_t object at 0x77910249d8a0>
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.require_signature_addr = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.signature_addr = 3735928559
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.gen_debug_section = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.enable_ebreak_in_debug_rom = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.set_dcsr_ebreak = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.num_debug_sub_program = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.enable_debug_single_step = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.single_step_iterations = <vsc.types.rand_uint32_t object at 0x77910249d9c0>
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.set_mstatus_tw = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.set_mstatus_mprv = <vsc.types.bit_t object at 0x77910249dba0>
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.min_stack_len_per_program = 40
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.max_stack_len_per_program = 64
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.max_branch_step = 20
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.reserved_regs = <vsc.types.list_t object at 0x77910249de70>
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.enable_floating_point = <vsc.types.bit_t object at 0x77910249e020>
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.enable_vector_extension = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.vector_instr_only = <vsc.types.bit_t object at 0x77910249e140>
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.enable_b_extension = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.enable_bitmanip_groups = ['ZBB', 'ZBS', 'ZBP', 'ZBE', 'ZBF', 'ZBC', 'ZBR', 'ZBM', 'ZBT', 'ZB_TMP']
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.dist_control_mode = 0
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.category_dist = {}
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.march_isa = []
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.supported_interrupt_mode = <vsc.types.list_t object at 0x77910249e230>
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.XLEN = <vsc.types.uint32_t object at 0x77910249e3e0>
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.SATP_MODE = <vsc.types.enum_t object at 0x77910249e470>
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.init_privil_mode = <vsc.types.enum_t object at 0x77910249e530>
2025-07-15 19:11:58,536 riscv_instr_base_test.py 89 INFO cfg.tvec_ceil = <vsc.types.uint32_t object at 0x77910249ebc0>
```
### Step-by-Step Execution Flow

#### 1. Configuration Loading
The framework reads test configuration from `yaml/base_testlist.yaml`:

```yaml
- test: riscv_arithmetic_basic_test
  description: >
    Arithmetic instruction test, no load/store/branch instructions
  gen_opts: >
    +instr_cnt=100
    +num_of_sub_program=0
    +directed_instr_0=riscv_int_numeric_corner_stream,4
    +no_fence=1
    +no_data_page=1
    +no_branch_jump=1
    +boot_mode=m
    +no_csr_instr=1
  iterations: 2
  gen_test: riscv_instr_base_test
  rtl_test: core_base_test
```

#### 2. Simulator Configuration
Reads `yaml/simulator.yaml` to get the pyflow simulator command:

```yaml
- tool: pyflow
  sim:
    cmd: >
      python3 <cwd>/pygen/pygen_src/test/<test_name>.py <sim_opts>
```
```bash
Main flow for asm generation is 
main()->gen()->do_simulate()
```

#### 3. Target Configuration
Loads processor configuration from `target/rv32imc/` or `pygen/pygen_src/target/rv32imc/`:

```python
# Key configuration parameters
XLEN = 32                    # 32-bit processor
SATP_MODE = BARE            # No address translation
supported_privileged_mode = [MACHINE_MODE]  # Machine mode only
supported_isa = [RV32I, RV32M, RV32C]       # ISA extensions
```

#### 4. Test Generation Process
The framework executes the following phases:

1. **Argument Processing**: Parse command line arguments and validate configurations
2. **Output Directory Creation**: Create timestamped output directory
3. **Test Matching**: Find matching tests from the test list
4. **Generator Invocation**: Call the appropriate generator (Python or SystemVerilog)
5. **Assembly Generation**: Generate `.S` assembly files
6. **Compilation**: Compile to `.o` ELF objects and `.bin` binaries
7. **Simulation**: Run ISS simulation (if configured)
8. **Comparison**: Compare results (if configured)

## File Generation Process

### Assembly Generation (.S files)

The Python-based generator creates assembly files through several key components:

#### 1. Main Test Script (`pygen/pygen_src/test/riscv_instr_base_test.py`)
- Creates test instances for specified iterations
- Generates random seeds for reproducibility
- Calls `riscv_asm_program_gen()` to create assembly programs

#### 2. Program Generation (`pygen/pygen_src/riscv_asm_program_gen.py`)
The core class that generates complete RISC-V assembly programs:

**Key Methods:**
- `gen_program()`: Main orchestration method
- `gen_program_header()`: Creates program header and includes
- `gen_init_section()`: Initializes registers and stack
- `gen_main_program()`: Generates main instruction sequences
- `gen_sub_program()`: Creates sub-programs and call stacks
- `gen_trap_handlers()`: Exception and interrupt handlers
- `gen_test_file()`: Writes final assembly to file

**Program Structure Generated:**
```assembly
.include "user_define.h"
.globl _start
.section .text
_start:
    .include "user_init.s"
    csrr x5, 0xf14          # Read hart ID
    li x6, 0
    beq x5, x6, 0f

0: la x12, h0_start
jalr x0, x12, 0

h0_start:
    li x31, 0x40001104      # Setup MISA
    csrw 0x301, x31
    
kernel_sp:
    la x20, kernel_stack_end

trap_vec_init:
    la x31, mtvec_handler
    ori x31, x31, 1
    csrw 0x305, x31         # MTVEC

init:
    # Initialize GPRs with random values
    li x0, 0xb
    li x1, 0x5
    # ... more register initialization
    
    # Main program instructions
    # ... generated instruction sequences
    
    # Exception handlers
    # ... trap and interrupt handlers
    
    # Data and stack sections
    .section .data
    .section .stack
```

#### 3. Instruction Generation
Various instruction library files generate:
- **Random Instructions**: Based on supported ISA extensions
- **Directed Instruction Streams**: Specific test patterns (e.g., `riscv_int_numeric_corner_stream`)
- **Corner Case Testing**: Edge cases and boundary conditions
- **Exception Scenarios**: Illegal instructions, page faults, etc.

### Compilation Process (.o and .bin files)

After assembly generation, the `gcc_compile()` function handles compilation:

#### 1. GCC Compilation (.S → .o)
```bash
riscv32-unknown-elf-gcc -static -mcmodel=medany -fvisibility=hidden \
    -nostdlib -nostartfiles -march=rv32imc -mabi=ilp32 \
    -T scripts/link.ld riscv_arithmetic_basic_test_0.S \
    -o riscv_arithmetic_basic_test_0.o
```

#### 2. Binary Generation (.o → .bin)
```bash
riscv32-unknown-elf-objcopy -O binary \
    riscv_arithmetic_basic_test_0.o \
    riscv_arithmetic_basic_test_0.bin
```

## Configuration System

### Target Configuration Hierarchy

The framework supports multiple processor configurations through the target system:

```
target/
├── rv32i/          # RV32I base integer
├── rv32imc/        # RV32I + M + C extensions
├── rv32imafdc/     # Full RV32 with floating point
├── rv64gc/         # RV64 general compute
└── ...
```

Each target contains:
- `riscv_core_setting.sv`: SystemVerilog configuration
- `riscv_core_setting.py`: Python equivalent
- `testlist.yaml`: Target-specific tests

### Key Configuration Parameters

#### Processor Features
```systemverilog
// Bit width of RISC-V GPR
parameter int XLEN = 32;

// Address translation mode
parameter satp_mode_t SATP_MODE = BARE;

// Supported privilege modes
privileged_mode_t supported_privileged_mode[] = {MACHINE_MODE};

// ISA extensions
riscv_instr_group_t supported_isa[] = {RV32I, RV32M, RV32C};

// Unsupported instructions
riscv_instr_name_t unsupported_instr[] = {};
```

#### Test Generation Options
```yaml
gen_opts: >
  +instr_cnt=100              # Number of instructions
  +num_of_sub_program=0       # Sub-program count
  +directed_instr_0=riscv_int_numeric_corner_stream,4  # Directed streams
  +no_fence=1                 # Disable fence instructions
  +no_data_page=1             # Disable data page generation
  +no_branch_jump=1           # Disable branch/jump instructions
  +boot_mode=m                # Boot in machine mode
  +no_csr_instr=1             # Disable CSR instructions
```

### Custom Target Creation

To create a custom target:

1. **Copy Existing Target**:
```bash
cp -r target/rv32imc target/my_custom_target
```

2. **Modify Configuration**:
```systemverilog
// In riscv_core_setting.sv
parameter int XLEN = 64;  // Change to 64-bit
riscv_instr_group_t supported_isa[] = {RV64I, RV64M, RV64A};
```

3. **Run with Custom Target**:
```bash
python3 run.py --custom_target target/my_custom_target \
    --isa rv64ima --mabi lp64 --test=my_test
```

## Directory Structure

### Generated Output Structure
```
out_<timestamp>/
├── asm_test/                    # Generated assembly tests
│   ├── riscv_arithmetic_basic_test_0.S    # Assembly source
│   ├── riscv_arithmetic_basic_test_0.o    # Compiled ELF
│   ├── riscv_arithmetic_basic_test_0.bin  # Binary file
│   └── riscv_arithmetic_basic_test_1.*    # Additional iterations
├── seed.yaml                    # Random seeds used
├── sim_*.log                    # Simulation logs
└── spike_sim/                   # ISS simulation results
```

### Source Code Organization
```
ibex_riscv-dv/
├── run.py                       # Main test runner
├── pygen/                       # Python generator
│   └── pygen_src/
│       ├── riscv_asm_program_gen.py  # Core generator
│       ├── riscv_instr_pkg.py        # Instruction definitions
│       ├── test/                     # Test entry points
│       └── target/                   # Target configurations
├── src/                         # SystemVerilog generator
├── yaml/                        # Configuration files
│   ├── base_testlist.yaml       # Test definitions
│   ├── simulator.yaml           # Simulator configurations
│   └── iss.yaml                 # ISS configurations
├── target/                      # Target-specific settings
├── scripts/                     # Utility scripts
└── user_extension/              # User customizations
```

## Usage Examples

### Basic Test Generation
```bash
# Generate arithmetic test with pyflow
python3 run.py --test=riscv_arithmetic_basic_test --simulator=pyflow

# Generate with specific target
python3 run.py --test=riscv_rand_instr_test --target=rv64gc --simulator=pyflow

# Generate multiple iterations
python3 run.py --test=riscv_loop_test --iterations=5 --simulator=pyflow
```

### Advanced Options
```bash
# Generate with custom seed
python3 run.py --test=riscv_arithmetic_basic_test --seed=12345 --simulator=pyflow

# Generate with custom instruction count
python3 run.py --test=riscv_rand_instr_test --simulator=pyflow \
    --gen_opts="+instr_cnt=500"

# Generate with debug output
python3 run.py --test=riscv_arithmetic_basic_test --verbose --simulator=pyflow
```

### Batch Generation
```bash
# Generate all tests in testlist
python3 run.py --testlist=yaml/base_testlist.yaml --simulator=pyflow

# Generate specific test pattern
python3 run.py --test="riscv_*_test" --simulator=pyflow
```

## Advanced Features

### Directed Instruction Streams
The framework supports directed instruction streams for focused testing:

```yaml
gen_opts: >
  +directed_instr_0=riscv_load_store_rand_instr_stream,4
  +directed_instr_1=riscv_loop_instr,4
  +directed_instr_2=riscv_hazard_instr_stream,4
```

Available directed streams:
- `riscv_int_numeric_corner_stream`: Integer arithmetic corner cases
- `riscv_load_store_rand_instr_stream`: Random load/store patterns
- `riscv_loop_instr`: Loop instruction sequences
- `riscv_hazard_instr_stream`: Pipeline hazard testing
- `riscv_multi_page_load_store_instr_stream`: Multi-page memory access

### Exception and Interrupt Testing
The generator creates comprehensive exception handlers:

- **Machine Mode Exceptions**: Illegal instruction, ECALL, EBREAK
- **Interrupt Handling**: Timer, software, external interrupts
- **Page Fault Handling**: TLB miss, protection violations
- **Debug Mode Support**: Breakpoint and single-step debugging

### Privilege Mode Testing
Support for multiple privilege modes:

```systemverilog
privileged_mode_t supported_privileged_mode[] = {
    USER_MODE,
    SUPERVISOR_MODE,
    MACHINE_MODE
};
```

### Memory Management
- **Virtual Memory**: SV32, SV39, SV48 page table generation
- **Physical Memory Protection**: PMP region configuration
- **Memory Ordering**: Fence instruction testing
- **Atomic Operations**: AMO instruction sequences

## Integration with Simulators

### Supported Simulators
- **Pyflow**: Python-based fast simulation
- **VCS**: Synopsys VCS simulator
- **Xcelium**: Cadence Xcelium simulator
- **Verilator**: Open-source Verilog simulator

### ISS Integration
- **Spike**: RISC-V ISS reference
- **OVPsim**: Imperas OVP simulator
- **Sail**: Formal RISC-V model
- **Whisper**: SiFive's ISS

### Trace Comparison
The framework supports automatic trace comparison between RTL and ISS:

```bash
python3 run.py --test=riscv_arithmetic_basic_test --simulator=vcs \
    --iss=spike,ovpsim --steps=all
```

## Troubleshooting

### Common Issues

1. **Compilation Errors**:
   - Verify RISC-V GCC toolchain installation
   - Check `RISCV_GCC` environment variable
   - Ensure correct ISA and ABI settings

2. **Generation Failures**:
   - Check Python dependencies (PyVSC)
   - Verify target configuration compatibility
   - Review test options for conflicts

3. **Simulation Issues**:
   - Confirm simulator installation and licensing
   - Check simulator-specific configuration files
   - Verify environment variables

### Debug Options
```bash
# Enable verbose logging
python3 run.py --test=riscv_arithmetic_basic_test --verbose --simulator=pyflow

# Generate debug commands only
python3 run.py --test=riscv_arithmetic_basic_test --debug --simulator=pyflow

# Stop on first error
python3 run.py --test=riscv_arithmetic_basic_test --stop_on_first_error --simulator=pyflow
```

## Conclusion

The ibex_riscv-dv framework provides a comprehensive solution for RISC-V processor verification. Its modular architecture, extensive configuration options, and support for multiple simulators make it an ideal choice for both academic research and commercial processor development. The framework's ability to generate complex, realistic test scenarios while maintaining reproducibility and debuggability makes it an invaluable tool in the RISC-V ecosystem.

For more specific usage scenarios and advanced customization, refer to the individual component documentation and example configurations provided in the repository.
