from classes.stages import *
import argparse

parser = argparse.ArgumentParser(description="Setup zigzag-v2 inputs")
# parser.add_argument('--workload', metavar='path', required=True, help='module path to workload, e.g. inputs.examples.workload1')
# parser.add_argument('--accelerator', metavar='path', required=True, help='module path to the accelerator, e.g. inputs.examples.accelerator1')
# parser.add_argument('--headname', type=str, required=True, help='result head name')

args = parser.parse_args()
import logging as _logging

_logging_level = _logging.INFO
_logging_format = '%(asctime)s - %(name)s.%(funcName)s +%(lineno)s - %(levelname)s - %(message)s'
_logging.basicConfig(level=_logging_level,
                     format=_logging_format)

####### WHERE THE RESULT FILES WILL BE SAVED TO (USERS CAN CHANGE) #######
result_saving_path = './result'
##########################################################################

mainstage = MainStage([
    WorkloadAndAcceleratorParserStage,
    GeneralParameterIteratorStage,
    SkipIfDumpExistsStage,
    DumpStage,
    DepthFirstStage,
    SpatialMappingConversionStage,
    RemoveExtraInfoStage,
    MinimalEnergyStage,
    LomaStage,
    ZigZagCostModelStage,
],
    # accelerator_path=args.accelerator,
    # workload_path=args.workload,
    workload_path='inputs.WL.Meta_prototype.workload_fsrcnn',
    accelerator_path='inputs.HW.Meta_prototype_DF',
    result_name='test_lbl',
    loma_lpf_limit=6,
    df_tilesize_x=10000000,
    df_tilesize_y=10000000,
    # headname=args.headname,
    result_saving_path=result_saving_path,
    df_stack_cuts=[],
    general_parameter_iterations={('df_horizontal_caching', 'df_vertical_caching'): ((False, False),)},
    dump_filename_pattern='{result_saving_path}/{result_name}.pkl'
)
mainstage.run()
