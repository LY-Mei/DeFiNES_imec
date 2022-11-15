import os
from classes.hardware.architecture.memory_hierarchy import MemoryHierarchy
from classes.hardware.architecture.memory_level import MemoryLevel
from classes.hardware.architecture.operational_unit import Multiplier
from classes.hardware.architecture.operational_array import MultiplierArray
from classes.hardware.architecture.memory_instance import MemoryInstance
from classes.hardware.architecture.accelerator import Accelerator
from classes.hardware.architecture.core import Core


def memory_hierarchy_dut(multiplier_array):
    """Memory hierarchy variables"""
    ''' size=#bit, bw=(read bw, write bw), cost=(read word energy, write work energy) '''

    wreg = MemoryInstance(name="wreg_1B", size=1 * 1 * 8, r_bw=8, w_bw=8, r_cost=1, w_cost=1, area=1.11, bank=1,
                          random_bank_access=False, r_port=1, w_port=1, rw_port=0, latency=1) #weight buffer inside PE

    wmem = MemoryInstance(name="wmem_16KB", size=1 * 16384 * 8, r_bw=256, w_bw=256, r_cost=94.6, w_cost=274, area=1.11, bank=1,
                          random_bank_access=False, r_port=1, w_port=1, rw_port=0, latency=1) #energy and area unit??current values enetered in pJ

    omem = MemoryInstance(name="omem_16KB", size=1 * 16384 * 8, r_bw=512, w_bw=512, r_cost=94.6, w_cost=274, area=1.11, bank=1,
                          random_bank_access=False, r_port=1, w_port=1, rw_port=0, latency=1)

    imem = MemoryInstance(name="imem_16KB", size=1 * 16384 * 8, r_bw=256, w_bw=256, r_cost=94.6, w_cost=274, area=1.11, bank=1,
                          random_bank_access=False, r_port=1, w_port=1, rw_port=0, latency=1)


    ##################################### on-chip memory hierarchy building blocks #####################################

    # GB = MemoryInstance(name="L1", size=32 * 1024 * 8, r_bw=128, w_bw=128, r_cost=26.01, w_cost=23.65, area=0, bank=1, random_bank_access=False, r_port=1, w_port=1, rw_port=0, latency=2, min_r_granularity=64, min_w_granularity=64)

   #######################################################################################################################

    dram = MemoryInstance(name="dram", size=10000000000 * 8, r_bw=64, w_bw=64, r_cost=16000, w_cost=46400, area=0, bank=1, random_bank_access=False,r_port=0, w_port=0, rw_port=1, latency=10)

    memory_hierarchy_graph = MemoryHierarchy(operational_array=multiplier_array)

    '''
    fh: from high = wr_in_by_high 
    fl: from low = wr_in_by_low 
    th: to high = rd_out_to_high
    tl: to low = rd_out_to_low
    '''
    
    ##################################### on-chip highest memory hierarchy initialization #####################################


    memory_hierarchy_graph.add_memory(memory_instance=wreg, operands=('I2',),
                                      port_alloc=({'fh': 'w_port_1', 'tl': 'r_port_1', 'fl': None, 'th': None},),
                                      served_dimensions={(0, 0)})

    memory_hierarchy_graph.add_memory(memory_instance=wmem, operands=('I2',),
                                      port_alloc=({'fh': 'w_port_1', 'tl': 'r_port_1', 'fl': None, 'th': None},),
                                      served_dimensions='all')

    memory_hierarchy_graph.add_memory(memory_instance=omem, operands=('O',),
                                      port_alloc=({'fh': 'w_port_1', 'tl': 'r_port_1', 'fl': 'w_port_1', 'th': 'r_port_1'},),
                                      served_dimensions='all')

    memory_hierarchy_graph.add_memory(memory_instance=imem, operands=('I1',),
                                      port_alloc=({'fh': 'w_port_1', 'tl': 'r_port_1', 'fl': None, 'th': None},),
                                      served_dimensions='all')

    ####################################################################################################################


    memory_hierarchy_graph.add_memory(memory_instance=dram, operands=('I1', 'I2', 'O'),
                                      port_alloc=({'fh': 'rw_port_1', 'tl': 'rw_port_1', 'fl': None, 'th': None},
                                                  {'fh': 'rw_port_1', 'tl': 'rw_port_1', 'fl': None, 'th': None},
                                                  {'fh': 'rw_port_1', 'tl': 'rw_port_1', 'fl': 'rw_port_1', 'th': 'rw_port_1'},),
                                      served_dimensions='all')

    return memory_hierarchy_graph


def multiplier_array_dut():
    """ Multiplier array variables """
    multiplier_input_precision = [8, 8]
    multiplier_energy = 0.002 #from the meta Y1H1 implementation reports
    multiplier_area = 14 #what is the unit? currently using the pe area as the multiplier area itself 
    dimensions = {'D1': 16, 'D2': 16}  # {'D1': ('K', 16), 'D2': ('C', 16)}



    multiplier = Multiplier(multiplier_input_precision, multiplier_energy, multiplier_area)
    multiplier_array = MultiplierArray(multiplier, dimensions)

    return multiplier_array


def cores():
    multiplier_array1 = multiplier_array_dut()
    memory_hierarchy1 = memory_hierarchy_dut(multiplier_array1)

    core1 = Core(1, multiplier_array1, memory_hierarchy1)

    return {core1}


cores = cores()
global_buffer = None
acc_name = os.path.basename(__file__)[:-3]
accelerator = Accelerator(acc_name, cores, global_buffer)

a = 1
