### For  **RV32IMC** :

**Supported tests:**

* riscv_arithmetic_basic_test
* riscv_floating_point_arithmetic_test

###### Directed tests:

* riscv_int_numeric_corner_stream
* riscv_jal_instr

**Note:**

* Do **not** run riscv_amo_test (since the A extension is not present).
* riscv_b_ext_test is only for targets with the B extension (not included in plain RV32IMC).

---

### For  **RV32IMAC** :

**Supported tests:**

* riscv_arithmetic_basic_test
* riscv_floating_point_arithmetic_test
* riscv_amo_instr_stream

Directed tests :

* riscv_int_numeric_corner_stream
* riscv_jal_instr

**Note:**

* You can run riscv_amo_instr_stream, as the A extension (Atomic) is included.
* riscv_amo_test (needs rv32imafdc, which includes F and D extensions) is **not** fully supported unless you add F/D extensions.
* riscv_b_ext_test still only applies if B extension is present.
