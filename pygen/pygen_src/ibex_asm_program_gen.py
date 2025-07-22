import logging
import random
import copy
import sys
import vsc
from importlib import import_module
from pygen_src.riscv_instr_sequence import riscv_instr_sequence
from pygen_src.riscv_callstack_gen import riscv_callstack_gen
from pygen_src.riscv_instr_pkg import (pkg_ins, privileged_reg_t,
                                       privileged_mode_t, mtvec_mode_t,
                                       misa_ext_t, riscv_instr_group_t,
                                       satp_mode_t, exception_cause_t)
from pygen_src.riscv_signature_pkg import (signature_type_t, core_status_t,
                                           test_result_t)
from pygen_src.riscv_instr_gen_config import cfg
from pygen_src.riscv_data_page_gen import riscv_data_page_gen
from pygen_src.riscv_privileged_common_seq import riscv_privileged_common_seq
from pygen_src.riscv_utils import factory
rcs = import_module("pygen_src.target." + cfg.argv.target + ".riscv_core_setting")

from .riscv_asm_program_gen import riscv_asm_program_gen

class ibex_asm_program_gen(riscv_asm_program_gen):
    def __init__(self):
        super().__init__()
        
    def gen_program_header(self):
        #  Override the mstatus_mprv config because there is no current way to randomize writing to
        #  mstatus.mprv in riscv-dv (it's constrained by set_mstatus_mprv argument to have either
        #  1 or 0 for the duration of the run)
        if cfg.set_mstatus_mprv :
            cfg.set_mstatus_mprv = random.randint(0, 1)
        #  Override the cfg value, below fields are not supported by ibex
        cfg.mstatus_mxr  = 0
        cfg.mstatus_sum  = 0
        cfg.mstatus_tvm  = 0  
        # Disable below fields checking against spike as spike implementation is different compared
        # with ibex.
        cfg.check_misa_init_val=0
        cfg.check_xstatus=0
        self.instr_stream.append(".section .text")
        # if cfg.mtvec_mode == mtvec_mode_t.VECTORED:
        #     self.gen_table(0,"m",self.instr_stream)
        # self.instr_stream.append("j mtvec_handler")
        self.instr_stream.append(".globl _start")
        self.instr_stream.append(".option norvc")
        # 0x0 debug mode entry
        # self.instr_stream.append("j debug_rom")
        # self.instr_stream.append(".align 3")
        # # 0x8 debug mode exception handler
        # self.instr_stream.append("j debug_exception")
        # Align the start section to 0x80
        # self.instr_stream.append(".align 7")
        # self.instr_stream.append(".align 7")
        # self.instr_stream.append(".option rvc")
        # self.instr_stream.append("_start:")
    def gen_program(self):
        self.instr_stream.clear()
        # Generate program header
        self.gen_program_header()
        for hart in range(cfg.num_of_harts):
            # Starting point of data section
            if not cfg.bare_program_mode:
                 
                # Generate kernel program section ->gen_kernel_sections(hart)
                # ->self.gen_all_trap_handler(hart)
                 if not rcs.support_pmp:
                    # self.gen_trap_handlers(hart)
                    # self.gen_trap_handler_section(hart, "m", privileged_reg_t.MCAUSE,
                    #                   privileged_reg_t.MTVEC, privileged_reg_t.MTVAL,
                    #                   privileged_reg_t.MEPC, privileged_reg_t.MSCRATCH,
                    #                   privileged_reg_t.MSTATUS, privileged_reg_t.MIE,
                    #                   privileged_reg_t.MIP)
                    mode="m"
                    status= privileged_reg_t.MSTATUS
                    cause= privileged_reg_t.MCAUSE
                    tvec= privileged_reg_t.MTVEC
                    ie= privileged_reg_t.MIE
                    ip= privileged_reg_t.MIP
                    scratch = privileged_reg_t.MSCRATCH
                    instr = []
                    if cfg.mtvec_mode == mtvec_mode_t.VECTORED:
                        # self.gen_interrupt_vector_table(hart, mode, status, cause, ie, ip, scratch, instr)
                        instr.extend((".option norvc;", "j {}{}mode_exception_handler".format(
                            pkg_ins.hart_prefix(hart), mode)))
                        # Redirect the interrupt to the corresponding interrupt handler
                        for i in range(1, rcs.max_interrupt_vector_num):
                            instr.append("j {}{}mode_intr_vector_{}".format(pkg_ins.hart_prefix(hart), mode, i))
                        if not cfg.disable_compressed_instr:
                            instr.append(".option rvc;")
                    
                    if rcs.SATP_MODE != satp_mode_t.BARE:
                        self.instr_stream.append(".align 12")
                    else:
                        self.instr_stream.append(".align {}".format(cfg.tvec_alignment))
                    tvec_name = tvec.name
                    # logging.info("Generating {} trap handler for hart {}".format(tvec_name, hart))
                    self.gen_section(pkg_ins.get_label("{}_handler".format(tvec_name.lower()), hart), instr)
        self.instr_stream.append(".align 7")
        self.instr_stream.append(".option rvc")
        self.instr_stream.append("_start:")

        for hart in range(cfg.num_of_harts):
            sub_program_name = []
            self.instr_stream.append(f"h{int(hart)}_start:")
            if not cfg.bare_program_mode: # its zero 
                # logging.info("cfg.bare_program_mode is set to 0, generating init section")
                self.setup_misa() 
                # Create all page tables
                self.create_page_table(hart)
                # Setup privileged mode registers and enter target privileged mode
                self.pre_enter_privileged_mode(hart)
            # Init section
            self.gen_init_section(hart)
            '''
            If PMP is supported, we want to generate the associated trap handlers and the test_done
            section at the start of the program so we can allow access through the pmpcfg0 CSR
            '''
            if(rcs.support_pmp and not(cfg.bare_program_mode)): #support_pmp=0
                self.gen_trap_handlers(hart)
                # Ecall handler
                self.gen_ecall_handler(hart)
                # Instruction fault handler
                self.gen_instr_fault_handler(hart)
                # Load fault handler
                self.gen_load_fault_handler(hart)
                # Store fault handler
                self.gen_store_fault_handler(hart)
                if hart == 0:
                    self.gen_test_done()
            # Generate sub program
            self.gen_sub_program(hart, self.sub_program[hart],
                                 sub_program_name, cfg.num_of_sub_program)
            # Generate main program
            gt_lbl_str = pkg_ins.get_label("main", hart)
            label_name = gt_lbl_str
            gt_lbl_str = riscv_instr_sequence()
            self.main_program.append(gt_lbl_str)
            self.main_program[hart].instr_cnt = cfg.main_program_instr_cnt
            self.main_program[hart].is_debug_program = 0
            self.main_program[hart].label_name = label_name
            self.generate_directed_instr_stream(hart=hart,
                                                label=self.main_program[hart].label_name,
                                                original_instr_cnt=
                                                self.main_program[hart].instr_cnt,
                                                min_insert_cnt=1,
                                                instr_stream=self.main_program[hart].directed_instr)
            self.main_program[hart].gen_instr(is_main_program=1, no_branch=cfg.no_branch_jump)
            # Setup jump instruction among main program and sub programs
            self.gen_callstack(self.main_program[hart], self.sub_program[hart],
                               sub_program_name, cfg.num_of_sub_program)
            self.main_program[hart].post_process_instr()
            logging.info("Post-processing main program...done")
            self.main_program[hart].generate_instr_stream()
            logging.info("Generating main program instruction stream...done")
            self.instr_stream.extend(self.main_program[hart].instr_string_list)
            """
            If PMP is supported, need to jump from end of main program
            to test_done section at the end of main_program, as the test_done
            will have moved to the beginning of the program
            """
            self.instr_stream.extend(("{}la x{}, test_done".format(pkg_ins.indent, cfg.scratch_reg),
                                      "{}jalr x0, x{}, 0".format(pkg_ins.indent, cfg.scratch_reg)))
            # Test done section
            # If PMP isn't supported, generate this in the normal location
            if(hart == 0 and not(rcs.support_pmp)):
                self.gen_test_done()
            # Shuffle the sub programs and insert to the instruction stream
            self.insert_sub_program(self.sub_program[hart], self.instr_stream)
            logging.info("Main/sub program generation...done")
            # program end
            self.gen_program_end(hart)
            if not cfg.bare_program_mode:
                # Generate debug rom section
                if rcs.support_debug_mode:
                    self.gen_debug_rom(hart)
                self.gen_section(pkg_ins.hart_prefix(hart) + "instr_end", ["nop"])
        for hart in range(cfg.num_of_harts):
            # Starting point of data section
            self.gen_data_page_begin(hart)
            if not cfg.no_data_page:
                # User data section
                self.gen_data_page(hart)
                # AMO memory region
                if(hart == 0 and riscv_instr_group_t.RV32A in rcs.supported_isa):
                    self.gen_data_page(hart, amo = 1)
            # Stack section
            self.gen_stack_section(hart)
            if not cfg.bare_program_mode:
                # Generate kernel program/data/stack section
                self.gen_kernel_sections(hart)
                # Page table
                self.gen_page_table_section(hart)

    # Generate the interrupt and trap handler for different privileged mode.
    # The trap handler checks the xCAUSE to determine the type of the exception and jumps to
    # corresponding exeception handling routine.
    def gen_trap_handler_section(self, hart, mode, cause, tvec,
                                 tval, epc, scratch, status, ie, ip):
        # is_interrupt = 1
        tvec_name = ""
        instr = []
        if cfg.mtvec_mode == mtvec_mode_t.VECTORED:
            self.gen_interrupt_vector_table(hart, mode, status, cause, ie, ip, scratch, instr)
        else:
            # Push user mode GPR to kernel stack before executing exception handling,
            # this is to avoid exception handling routine modify user program state
            # unexpectedly
            pkg_ins.push_gpr_to_kernel_stack(
                status, scratch, cfg.mstatus_mprv, cfg.sp, cfg.tp, instr)
            # Checking xStatus can be optional if ISS (like spike) has different implementation of
            # certain fields compared with the RTL processor.
            if cfg.check_xstatus:
                instr.append("csrr x{}, {} # {}".format(
                    cfg.gpr[0], hex(status), status.name))
            # Use scratch CSR to save a GPR value
            # Check if the exception is caused by an interrupt, if yes, jump to interrupt
            # handler Interrupt is indicated by xCause[XLEN-1]
            instr.append("csrr x{}, {} # {}\n".format(cfg.gpr[0], hex(cause),
                                                      cause.name) +
                         "{}srli x{}, x{}, {}\n".format(pkg_ins.indent, cfg.gpr[0],
                                                        cfg.gpr[0], rcs.XLEN - 1) +
                         "{}bne x{}, x0, {}{}mode_intr_handler".format(pkg_ins.indent,
                                                                       cfg.gpr[0],
                                                                       pkg_ins.hart_prefix(hart),
                                                                       mode))
        # The trap handler will occupy one 4KB page, it will be allocated one entry in
        # the page table with a specific privileged mode.
        # The mtvec_handler section is not needed now as it is placed above
        # if rcs.SATP_MODE != satp_mode_t.BARE:
        #     self.instr_stream.append(".align 12")
        # else:
        #     self.instr_stream.append(".align {}".format(cfg.tvec_alignment))
        # # logging.info("instr_stream: %s", self.instr_stream)
        # #instr contains mtvec handler by here
        # logging.info("instr: %s", instr)
        # tvec_name = tvec.name
        # logging.info("Generating {} trap handler for hart {}".format(tvec_name, hart))
        # self.gen_section(pkg_ins.get_label("{}_handler".format(tvec_name.lower()), hart), instr)
        # # logging.info("instr_stream: %s", self.instr_stream)


        # Exception handler
        instr = []
        if cfg.mtvec_mode == mtvec_mode_t.VECTORED:
            pkg_ins.push_gpr_to_kernel_stack(
                status, scratch, cfg.mstatus_mprv, cfg.sp, cfg.tp, instr)
        self.gen_signature_handshake(instr, signature_type_t.CORE_STATUS,
                                     core_status_t.HANDLING_EXCEPTION)
        # TODO
        instr.extend(("csrr x{}, {} # {}".format(cfg.gpr[0], hex(epc), epc.name),
                      "csrr x{}, {} # {}".format(cfg.gpr[0], hex(cause), cause.name),
                      # Check if it's an ECALL exception. Jump to ECALL exception handler
                      # TODO ECALL_SMODE, ECALL_UMODE
                      "li x{}, {} # ECALL_MMODE".format(cfg.gpr[1],
                                                        hex(exception_cause_t.ECALL_MMODE)),
                      "beq x{}, x{}, {}ecall_handler".format(
                      cfg.gpr[0], cfg.gpr[1], pkg_ins.hart_prefix(hart)),
                      # Illegal instruction exception
                      "li x{}, {} # ILLEGAL_INSTRUCTION".format(
                      cfg.gpr[1], hex(exception_cause_t.ILLEGAL_INSTRUCTION)),
                      "beq x{}, x{}, {}illegal_instr_handler".format(
                      cfg.gpr[0], cfg.gpr[1], pkg_ins.hart_prefix(hart)),
                      # Skip checking tval for illegal instruction as it's implementation specific
                      "csrr x{}, {} # {}".format(cfg.gpr[1], hex(tval), tval.name),
                      # use JALR to jump to test_done.
                      "1: la x{}, test_done".format(cfg.scratch_reg),
                      "jalr x1, x{}, 0".format(cfg.scratch_reg)))
        # logging.info("Instr:{}".format(instr.items()))
        self.gen_section(pkg_ins.get_label("{}mode_exception_handler".format(mode), hart), instr)

    # ECALL trap handler
    # For riscv-dv in Ibex, ECALL is no-longer used to end the test.
    # Hence, redefine a simple version here that just increments
    # MEPC+4 then calls 'mret'. (ECALL is always 4-bytes in RV32)
    def gen_ecall_handler(self, hart):
        instr=[]
        self.dump_perf_stats(instr)
        self.gen_register_dump(instr)
        instr.extend(("csrr x{}, {} # {}".format(cfg.gpr[0], hex(privileged_reg_t.MEPC), privileged_reg_t.MEPC.name),
                        "addi x{}, x{}, 4".format(cfg.gpr[0], cfg.gpr[0]),
                        "csrw {}, x{}".format(hex(privileged_reg_t.MEPC), cfg.gpr[0]),
                        "mret"))
        self.gen_section(pkg_ins.get_label("ecall_handler", hart), instr)

        
    # Translated the code in SysVerilog (not verified)
    # def gen_debug_rom(self, hart):
    #     """
    #     Generate a debug ROM program for the given hart and append its instructions to this object's instr_stream.
    #     """
    #     logging.info("Creating debug ROM for hart %d", hart)
    #     # Create a new instance of riscv_asm_program_gen for the debug ROM
    #     debug_rom = riscv_asm_program_gen()
    #     debug_rom.cfg = self.cfg if hasattr(self, 'cfg') else cfg  # Use self.cfg if present, else global cfg
    #     debug_rom.hart = hart
    #     debug_rom.gen_program()
    #     # Append the generated debug ROM instructions to this object's instruction stream
    #     self.instr_stream.extend(debug_rom.instr_stream)

    #Re-define gen_test_done() to override the base-class with an empty implementation.
    #Then, our own overriding gen_program() can append new test_done code.
    def gen_test_done(self):
        """Override the base class gen_test_done with an empty implementation."""
        pass

    def gen_init_section(self, hart):
        # This is a good location to put the test done and fail because PMP tests expect these
        # sequences to be before the main function.
        instr = []
        
        super().gen_init_section(hart)
        # RISCV-DV assumes main is immediately after init when riscv_instr_pkg::support_pmp isn't set.
        # This override of gen_init_section breaks that assumption so add a jump to main here so the
        # test starts correctly for configurations that don't support PMP.

        # if not rcs.support_pmp:
        #     # Jump to main program
        #     self.instr_stream.append("j main")
        
    #     # Add the gen_test_end functionality based on relevance 
        self.gen_test_end(result=test_result_t.TEST_PASS, instr=instr)
        self.instr_stream.append("test_done:")
        self.instr_stream.extend(instr)
        instr.clear()
        self.gen_test_end(result=test_result_t.TEST_FAIL, instr=instr)
        self.instr_stream.append("test_fail:")
        self.instr_stream.extend(instr)


        
    def gen_test_end(self, result, instr):
        test_control_addr = cfg.signature_addr - 0x4
        i = pkg_ins.indent
        if cfg.bare_program_mode:
            str_instr = f"{i}j write_tohost\n"
            instr.append(str_instr)
        else:
            str_instr = [
                f"{i}li x{cfg.gpr[1]}, 0x{test_control_addr:x}\n",
                f"{i}li x{cfg.gpr[0]}, 0x{int(result):x}\n",
                f"{i}slli x{cfg.gpr[0]}, x{cfg.gpr[0]}, 8\n",
                f"{i}addi x{cfg.gpr[0]}, x{cfg.gpr[0]}, 0x{int(signature_type_t.TEST_RESULT):x}\n",
                f"{i}sw x{cfg.gpr[0]}, 0(x{cfg.gpr[1]})\n",
                f"{i}ecall\n"
            ]
            instr.extend(str_instr)

# Functions mimiced with ibex_asm_program_gen.sv at 
# https://github.com/lowRISC/ibex/blob/master/dv/uvm/core_ibex/riscv_dv_extension/ibex_asm_program_gen.sv
# are follows
# gen_ecall_handler
# gen_test_end (not implemented)
# gen_debug_rom (implemented but not tested due to errors)
# gen_test_done (implmented but not using due to errors ,without this many functions are not able to use test_done section)
# 
# gen_init_section (modified but not exactly with ibex)
# gen_program_header (modified similar to ibex but not used debug rom and debug exception , so modified the function to make space for vector table)
# gen_program (modified to put the trap handling vector table at the start of the program)
# gen_trap_handler_section (modified to put the trap handling vector table at the start of the program)


# Ibex specific test_done and test_fail sections are generated when you uncomment the gen_init_section's override and gen_test_end function

# Instead of typical <write_tohost> instruction , it writes 1 if test passes and 0 if test fails to the signature address. 0xdeadbeeb

