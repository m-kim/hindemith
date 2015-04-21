from net import Net
import layers.caffe_pb2 as pb
from google.protobuf import text_format


class Solver(object):

    """Docstring for Solver. """

    def __init__(self, param):
        """TODO: to be defined1. """
        self.init_train_net(param)
        self.init_test_nets(param)

    def init_train_net(self, param):
        net_param = pb.NetParameter()
        with open(param.net, "rb") as f:
            text_format.Merge(f.read(), net_param)

        net_state = pb.NetState()
        net_state.phase = pb.TRAIN
        net_state.MergeFrom(net_param.state)
        net_state.MergeFrom(param.train_state)
        net_param.state.CopyFrom(net_state)
        self.train_net = Net(net_param)

    def init_test_nets(self, param):
        pass


def main():
    param = pb.SolverParameter()
    with open("./models/alexnet-ng/solver.prototxt", "rb") as f:
        text_format.Merge(f.read(), param)
    Solver(param)


if __name__ == '__main__':
    main()
