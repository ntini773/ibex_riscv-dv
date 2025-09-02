## Overview

RISCV-DV is a SV/UVM based open-source instruction generator for RISC-V
processor verification. It currently supports the following features:

- Supported instruction set: RV32IMAFDC, RV64IMAFDC
- Supported privileged mode: machine mode, supervisor mode, user mode
- Page table randomization and exception
- Privileged CSR setup randomization
- Privileged CSR test suite
- Trap/interrupt handling
- Test suite to stress test MMU
- Sub-program generation and random program calls
- Illegal instruction and HINT instruction generation
- Random forward/backward branch instructions
- Supports mixing directed instructions with random instruction stream
- Debug mode support, with fully randomized debug ROM
- Instruction generation coverage model
- Handshake communication with testbench
- Support handcoded assembly test
- Co-simulation with multiple ISS : spike, riscv-ovpsim, whisper, sail-riscv

## Getting Started

### Prerequisites

To be able to run the instruction generator, you need to have an RTL simulator
which supports SystemVerilog and UVM 1.2. This generator has been verified with
Synopsys VCS, Cadence Incisive/Xcelium, Mentor Questa, and Aldec Riviera-PRO simulators.
Please make sure the EDA tool environment is properly setup before running the generator.

### Install RISCV-DV

Getting the source
```bash
git clone https://github.com/google/riscv-dv.git
```

There are two ways that you can run scripts from riscv-dv.

For developers which may work on multiple clones in parallel, using directly run
by `python3` script is highly recommended. Example:

```bash
pip3 install -r requirements.txt    # install dependencies (only once)
python3 run.py --help
```
For normal users, using the python package is recommended. First, cd to the directory
where riscv-dv is cloned and run:

```bash
export PATH=$HOME/.local/bin/:$PATH  # add ~/.local/bin to the $PATH (only once)
pip3 install --user -e .
```

This installs riscv-dv in a mode where any changes within the repo are immediately
available simply by running `run`/`cov`. There is no need to repeatedly run `pip install .`
after each change. Example for running:

```bash
run --help
cov --help
```

Use below command to install Verible, which is the tool to check Verilog style
```bash
verilog_style/build-verible.sh
```

This is the command to run Verilog style check. It's recommended to run and clean up
all the style violations before submit a PR
```bash
verilog_style/run.sh
```

## Document

To understand how to setup and customize the generator, please check the full
document under docs directory. You can use the makefile to generate the
document. [HTML
preview](https://htmlpreview.github.io/?https://github.com/google/riscv-dv/blob/master/docs/build/singlehtml/index.html#document-index).
You can find the prebuilt document under docs/build/singlehtml/index.html

## External contributions and collaborations

RISC-V DV is now contributed to CHIPS Alliance. We have regular meetings to
discuss the issues, feature priorities, development progress etc. Please join
the [mail group](https://lists.chipsalliance.org/g/riscv-dv-wg) for latest
status.

Please refer to CONTRIBUTING.md for license related questions.

## Supporting model

Please file an issue under this repository for any bug report / integration
issue / feature request. We are looking forward to knowing your experience of
using this flow and how we can make it better together.

## Disclaimer

This is not an officially supported Google product.


# Ibex-Compatible RISC-V DV (Fork)

This repository provides modifications to [riscv-dv](https://github.com/google/riscv-dv) so that it can generate instruction tests compatible with the [Ibex RISC-V core](https://github.com/lowRISC/ibex). The key goal is to make ELF/assembly files that match Ibex’s expectations, especially regarding trap handling and vector table placement.

---

## 🔹 Motivation

The vanilla `riscv-dv` generator targets generic RISC-V cores and often assumes a different boot/reset behavior than Ibex. Ibex requires:

* A **trap vector table** aligned to 256 bytes and placed before `_start`.
* Boot address handling consistent with Ibex reset flow (e.g., reset at `0x...80`).
* Simpler end-of-test semantics (write pass/fail to a signature address instead of `tohost`).

This fork adapts `riscv-dv` to these needs.

---

## 🔹 Running Tests with PyFlow

Tests can be generated using the **Python-based PyFlow simulator** (no licensed tools required):

```bash
python3 run.py --test=ibex_load_instr_test --simulator=pyflow
python3 run.py --test=ibex_arithmetic_basic_test --simulator=pyflow
python3 run.py --test=ibex_rand_instr_test --simulator=pyflow
```

Generated outputs include `.S` assembly files, `.o` objects, and `.elf` binaries that can be simulated on Ibex or co-simulated with Spike.

---

## 🔹 Key Code Changes

### 1. **New Base Test**: `ibex_instr_base_test.py`

* Inherits from `riscv_instr_base_test`.
* Overrides `_run_phase()` to:

  * Apply Ibex-specific directed instructions.
  * Call `ibex_asm_program_gen` instead of the default generator.
* Ensures consistent seeds and logging for reproducibility.

### 2. **Custom Generator**: `ibex_asm_program_gen.py`

Derived from `riscv_asm_program_gen`, with Ibex-specific overrides:

* **`gen_program_header`**

  * Removes unsupported fields (`mstatus.mxr`, `mstatus.sum`, `mstatus.tvm`).
  * Disables certain checks (`misa` init value, `xstatus`).
  * Aligns/places Ibex-specific directives.

* **`gen_program`**

  * Places the trap handler **vector table at the start of the program**.
  * Ensures `_start` follows the vector table, matching Ibex boot behavior.
  * Simplifies debug ROM handling.

* **`gen_trap_handler_section`**

  * Builds trap handler vector entries first.
  * Jumps to exception/interrupt handlers in Ibex style.

* **`gen_ecall_handler`**

  * Unlike vanilla DV, Ibex doesn’t use ECALL to end tests.
  * Instead, increments `MEPC` by 4 and returns with `mret`.

* **`gen_init_section`**

  * Space for Ibex-specific test-done/fail logic (currently optional, commented).

* **`gen_test_end`**

  * Writes pass/fail values to a **signature address** (instead of using `write_tohost`).

### 3. **YAML Testlist Entries**

Example from `base_testlist.yaml`:

```yaml
- test: ibex_arithmetic_basic_test
  description: >
    Arithmetic instruction test, no load/store/branch instructions
  gen_opts: >
    +instr_cnt=100
    +num_of_sub_program=0
    +directed_instr_0=riscv_int_numeric_corner_stream,4
    +no_fence=1
    +no_data_page=1
    +no_branch_jump=0
    +boot_mode=m
    +no_csr_instr=0
  iterations: 2
  gen_test: ibex_instr_base_test
  rtl_test: core_base_test
```

This allows `run.py` to recognize Ibex-specific tests just like the existing RISC-V ones.

---

## 🔹 Example Generated Assembly (Excerpt)

```asm
.section .text
.globl _start
.option norvc
.align 4
mtvec_handler:
    .option norvc;
    j mmode_exception_handler
    j mmode_intr_vector_1
    j mmode_intr_vector_2
    ...
    j mmode_intr_vector_31
    .option rvc;

.align 7
.option rvc
_start:
    # main program starts here
```

This shows the **vector table placed before `_start`**, which is crucial for Ibex.

---

## 🔹 Supported Tests (with PyFlow)

Currently working tests (subject to PyFlow limitations):

* `ibex_arithmetic_basic_test`
* `ibex_load_instr_test`
* `ibex_rand_instr_test`

For general PyFlow test support, see [PYFLOW\_SUPPORTED\_TESTS.md](./PYFLOW_SUPPORTED_TESTS.md).

---

## 🔹 References

* [Ibex DV Extensions (SystemVerilog)](https://github.com/lowRISC/ibex/blob/master/dv/uvm/core_ibex/riscv_dv_extension/ibex_asm_program_gen.sv) – Original implementation mirrored here in Python.
* [Ibex Documentation on Exceptions/Interrupts](https://ibex-core.readthedocs.io/en/latest/03_reference/exception_interrupts.html#exceptions-and-interrupts)
* [PyFlow GitHub Issue](https://github.com/chipsalliance/riscv-dv/issues/781) – Tracking PyFlow support.

---
