# 单进程串行模拟多client后端
# 进程资源限制
# serial_handler仅share一个网络topology模块
# serial_handler对上层提供
import random

from abc import ABC, abstractmethod
from copy import deepcopy

from fedlab_core.client.handler import ClientBackendHandler
from  fedlab_utils.serialization import SerializationTool

class SerialHandler(ABC):
    """An abstract class for serial model training process
    
    It is expensive to simulate a single client per process, because of process exchange in OS.
    Therefore, we need a class to simulate multiple clients with a processs resouce.

    Subclass this class to create your own simulate algorithm.

    Args:
        model (torch.nn.Module): Model used in this federation
        cuda (bool): use GPUs or not
    """ 
    def __init__(self, client_handler_list, aggregator) -> None:
        # 需要添加类型检查
        self.clients = client_handler_list
        self.serial_number = len(client_handler_list)
        self.aggregator = aggregator

    @abstractmethod
    def train(self, epochs, model_parameters, idx_list=None):
        raise NotImplementedError()
    
    @abstractmethod
    def _merge_models(self, idx_list):
        raise NotImplementedError()

    @property
    def model(self):
        return self.model
        

class SerialSGDHandler(SerialHandler):
    """an example of SerialHandler
        Every client in this Serial share the same shape of model. Each of them has different
        datasets and 
    """
    def __init__(self, client_handler_list) -> None:
        super(SerialHandler, self).__init__()
        self.clients = client_handler_list

    def train(self, epochs, model_parameters, idx_list=None, select_ratio=None):

        if idx_list is None:
            if select_ratio is not None:
                idx_list = [i + 1 for i in range(self.serial_number)]
                idx_list = random.sample(idx_list, self.client_num_per_round)
            else:
                raise ValueError("idx_list and select_ration should not be None at the same time!")

        for idx in idx_list:
            assert idx<self.serial_number
            if idx >= self.serial_number:
                raise ValueError("Invalid idx of client: %d >= %d"%(idx, self.serial_number))
            self.clients[idx].train(epochs, model_parameters)

        self.model = self._merge_models(idx_list)
    
    def _merge_models(self, idx_list):
        parameter_list = [SerializationTool.serialize_model(self.clients[idx].model) for idx in idx_list]
        merged_parameters = self.aggregator(parameter_list)
        return merged_parameters

    
    
