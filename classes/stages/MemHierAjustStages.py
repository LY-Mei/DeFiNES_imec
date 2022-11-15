from classes.stages.Stage import Stage
import networkx as nx
import logging

logger = logging.getLogger(__name__)


class LayerByLayerMemHierAdjustStage(Stage):
    """
    For a linearly connected NN workload, find the lowest memory level at which the previous layer's output can become next layer's input.
    Skip all the unnecessary high memory levels in the activation memory hierarchy.
    """
    def __init__(self, list_of_callables, *, workload, **kwargs):
        super().__init__(list_of_callables, **kwargs)
        self.workload = workload

    def run(self):
        for id, layer in enumerate(nx.topological_sort(self.workload)):
            # if type(layer) == DummyNode:
            #     continue  # skip the DummyNodes
            kwargs = self.kwargs.copy()
            kwargs['layer'] = layer
            layer_name = id
            logger.info(f"Processing layer {layer_name}...")

            updated_accelerator = self.memory_hierarchy_adjust(self.kwargs['accelerator'])
            kwargs['accelerator'] = updated_accelerator

            sub_stage = self.list_of_callables[0](self.list_of_callables[1:], **kwargs)
            for cme, extra_info in sub_stage.run():
                yield cme, (layer, extra_info)

    @staticmethod
    def memory_hierarchy_adjust(accelerator, layer):
        accelerator_new = accelerator

        # the memory hierarchy that will be adjusted
        memhier = accelerator.get_core(layer.core_allocation).memory_hierarchy

        # TODO
        # memories_to_take_for_O
        #
        # # We now know which memory levels to include, remove everything above it
        # for I in layer.input_operands:
        #     if I not in layer.constant_operands:
        #         while memories_to_take_for_I[-1] not in memhier.get_operator_top_level(layer.memory_operand_links[I])[0]:
        #
        #             removed, _ = memhier.remove_operator_top_level(layer.memory_operand_links[I])
        #             accelerator_mem_level_removed.get_core(layer.core_allocation). \
        #                 recalculate_memory_hierarchy_information()

        return accelerator_new