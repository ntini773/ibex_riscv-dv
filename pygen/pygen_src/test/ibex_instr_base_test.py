from riscv_instr_base_test import *
from pygen_src.ibex_asm_program_gen import ibex_asm_program_gen

class ibex_instr_base_test(riscv_instr_base_test):
    def __init__(self):
        super().__init__()

    def _run_phase(self, num):
        logging.info("Called ibex_instr_base_test._run_phase")
        if num == 0:
            '''Get the user specified seed value otherwise
               generate a random seed value from SeedGen method of run.py'''
            rand_seed = cfg.argv.seed.split("--")[0]
        else:
            # Generate random seed value everytime for multiple test iterations
            rand_seed = random.getrandbits(31)
        # Assign the global seed value for a particular iteration
        random.seed(rand_seed)
        self.randomize_cfg()
        self.asm = ibex_asm_program_gen()
        riscv_instr.create_instr_list(cfg)
        if cfg.asm_test_suffix != "":
            self.asm_file_name = "{}.{}".format(self.asm_file_name,
                                                cfg.asm_test_suffix)
        self.asm.get_directed_instr_stream()
        test_name = "{}_{}.S".format(self.asm_file_name,
                                     num + self.start_idx)
        self.apply_directed_instr()
        logging.info("All directed instruction is applied")
        self.asm.gen_program()
        self.asm.gen_test_file(test_name)
        logging.info("TEST GENERATED USING SEED VALUE = {}".format(rand_seed))
        logging.info("TEST GENERATION DONE")    

    def apply_directed_instr(self):
        # Ibex specific implementation for applying directed instructions
        logging.info("Applying directed instructions for Ibex -------------------------")
        # Add Ibex specific logic here if needed

start_time = time.time()
ibex_base_test_ins = ibex_instr_base_test()
if cfg.argv.gen_test == "ibex_instr_base_test":
    logging.info("Running Ibex instruction base test---------------------------------")
    ibex_base_test_ins.run()
    end_time = time.time()
    logging.info("Total execution time: {}s".format(round(end_time - start_time)))