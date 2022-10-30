import logging

from typing import Generator, Callable, List, Tuple, Any

from classes.depthfirst.data_copy_layer import DataCopyLayer
from classes.mapping.combined_mapping import FourWayDataMoving
from classes.stages.Stage import Stage
from classes.cost_model.cost_model import CostModelEvaluation
logger = logging.getLogger(__name__)


class MinimalEnergyStage(Stage):
    """
    Class that keeps yields only the cost model evaluation that has minimal energy of all cost model evaluations
    generated by it's substages created by list_of_callables
    """
    def __init__(self, list_of_callables, *, reduce_minimal_keep_others=False, **kwargs):
        """
        Initialize the compare stage.
        """
        super().__init__(list_of_callables, **kwargs)
        self.best_cme = None
        self.keep_others = reduce_minimal_keep_others


    def run(self) -> Generator[Tuple[CostModelEvaluation, Any], None, None]:
        """
        Run the compare stage by comparing a new cost model output with the current best found result.
        """
        sub_list_of_callables = self.list_of_callables[1:]
        substage = self.list_of_callables[0](sub_list_of_callables, **self.kwargs)

        other_cmes = []
        for cme, extra_info in substage.run():
            if self.best_cme is None or cme.energy_total < self.best_cme.energy_total:
                self.best_cme = cme
            if self.keep_others:
                other_cmes.append((cme, extra_info))
        yield (self.best_cme, other_cmes)


class MinimalLatencyStage(Stage):
    """
    Class that keeps yields only the cost model evaluation that has minimal latency of all cost model evaluations
    generated by it's substages created by list_of_callables
    """
    def __init__(self, list_of_callables,*, reduce_minimal_keep_others=False, **kwargs):
        """
        Initialize the compare stage.
        """
        super().__init__(list_of_callables, **kwargs)
        self.best_cme = None
        self.keep_others = reduce_minimal_keep_others


    def run(self) -> Generator[Tuple[CostModelEvaluation, Any], None, None]:
        """
        Run the compare stage by comparing a new cost model output with the current best found result.
        """
        sub_list_of_callables = self.list_of_callables[1:]
        substage = self.list_of_callables[0](sub_list_of_callables, **self.kwargs)

        other_cmes = []
        for cme, extra_info in substage.run():
            if self.best_cme is None or cme.latency_total < self.best_cme.latency_total:
                self.best_cme = cme
            if self.keep_others:
                other_cmes.append((cme, extra_info))
        yield (self.best_cme, other_cmes)

class SumStage(Stage):
    """
    Class that keeps yields only the sum of all cost model evaluations generated by its
    substages created by list_of_callables
    """
    def __init__(self, list_of_callables, **kwargs):
        """
        Initialize the compare stage.
        """
        super().__init__(list_of_callables, **kwargs)
        self.total_cme = None


    def run(self) -> Generator[Tuple[CostModelEvaluation, Any], None, None]:
        """
        Run the compare stage by comparing a new cost model output with the current best found result.
        """
        substage = self.list_of_callables[0](self.list_of_callables[1:], **self.kwargs)

        all_cmes = []
        for cme, extra_info in substage.run():
            if self.total_cme is None:
                self.total_cme = cme
            else:
                self.total_cme += cme
            all_cmes.append((cme, extra_info))
        yield self.total_cme, all_cmes

class ListifyStage(Stage):
    """Class yields all the cost model evaluations yielded by its substages as a single list instead of as a generator."""
    def __init__(self, list_of_callables, **kwargs):
        """
        Initialize the compare stage.
        """
        super().__init__(list_of_callables, **kwargs)
        self.list = []


    def run(self) -> Generator[Tuple[CostModelEvaluation, Any], None, None]:
        """
        Run the compare stage by comparing a new cost model output with the current best found result.
        """
        substage = self.list_of_callables[0](self.list_of_callables[1:], **self.kwargs)

        for cme, extra_info in substage.run():
            self.list.append((cme, extra_info))
        yield self.list, None




from utils import pickle_deepcopy
def remove_w_cost(cme):
    out = pickle_deepcopy(cme)
    if isinstance(out, DataCopyLayer):
        return out

    W_operands = out.layer.constant_operands

    for W in W_operands:
        out.layer.operand_precision[W] = 0
        out.energy_breakdown[W] = [0] * len(out.energy_breakdown[W])
        out.energy_breakdown_further[W] = [FourWayDataMoving(0, 0, 0, 0)] * len(out.energy_breakdown[W])
        out.memory_word_access[W] = [FourWayDataMoving(0, 0, 0, 0)] * len(out.energy_breakdown[W])
        out.calc_memory_energy_cost()  # also updates energy_total
    return out


class MinimumEnergyIgnoringWeightsStage(Stage):
    """
    Class that keeps yields only the cost model evaluation that has minimal energy of all cost model evaluations
    generated by it's substages created by list_of_callables, IGNORING COST OF WEIGHTS
    """
    def __init__(self, list_of_callables, *, reduce_minimal_keep_others=False, **kwargs):
        """
        Initialize the compare stage.
        """
        super().__init__(list_of_callables, **kwargs)
        self.best_cme = None
        # Visualization stuff
        self.keep_others = reduce_minimal_keep_others


    def run(self) -> Generator[Tuple[CostModelEvaluation, Any], None, None]:
        """
        Run the compare stage by comparing a new cost model output with the current best found result.
        """
        sub_list_of_callables = self.list_of_callables[1:]
        substage = self.list_of_callables[0](sub_list_of_callables, **self.kwargs)

        other_cmes = []
        best_energy = float('inf')
        for cme, extra_info in substage.run():
            cost_wo_w = remove_w_cost(cme).energy_total
            if cost_wo_w < best_energy:
                self.best_cme = cme
                best_energy = cost_wo_w
            if self.keep_others:
                other_cmes.append((cme, extra_info))
        yield (self.best_cme, other_cmes)