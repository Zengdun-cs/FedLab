import argparse
from statistics import mode
import sys

import torch
from torch import nn
import torchvision
import torchvision.transforms as transforms

sys.path.append("../../")

from fedlab.core.client.manager import PassiveClientManager
from fedlab.core.network import DistNetwork
from fedlab.utils.logger import Logger
from fedlab.models.mlp import MLP
from fedlab.dataset.mnist import PathologicalMNIST
from fedlab.contrib.clients import FedAvgClientTrainer


parser = argparse.ArgumentParser(description="Distbelief training example")

parser.add_argument("--ip", type=str)
parser.add_argument("--port", type=str)
parser.add_argument("--world_size", type=int)
parser.add_argument("--rank", type=int)
parser.add_argument("--ethernet", type=str, default=None)

parser.add_argument("--lr", type=float, default=0.01)
parser.add_argument("--epochs", type=int, default=2)
parser.add_argument("--batch_size", type=int, default=100)
args = parser.parse_args()

if torch.cuda.is_available():
    args.cuda = True
else:
    args.cuda = False


model = MLP(784, 10)
network = DistNetwork(
    address=(args.ip, args.port),
    world_size=args.world_size,
    rank=args.rank,
    ethernet=args.ethernet,
)

LOGGER = Logger(log_name="client " + str(args.rank))

trainer = FedAvgClientTrainer(model, cuda=args.cuda)

dataset = PathologicalMNIST(root='../../tests/data/mnist/',
                            path="../../tests/data/mnist/",
                            num=args.world_size - 1)
#dataset.preprocess()
trainer.setup_dataset(dataset)
trainer.setup_optim(args.epochs, args.batch_size, args.lr)

manager_ = PassiveClientManager(trainer=trainer,
                                network=network,
                                logger=LOGGER)
manager_.run()
