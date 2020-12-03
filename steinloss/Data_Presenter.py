from steinloss.loss_calculator import PacketEntry
from steinloss.loss_calculator import Loss_Calculator
from steinloss.loss_calculator import TimeTable


class Data_Presenter(object):
    __instance__ = None

    def __init__(self):
        if Data_Presenter.__instance__ is not None:
            raise RuntimeError("Cannot init class twice, as it is as singelton")
        else:
            self.data = Loss_Calculator()
            Data_Presenter.__instance__ = self

    @classmethod
    def get_instance(cls):
        """
        :rtype: Data_Presenter
        """
        if cls.__instance__ is None:
            Data_Presenter()
        return cls.__instance__

    @classmethod
    def clear_instance(cls):
        cls.__instance__ = None

    def append(self, packet):
        self.data.add(packet)

    def latest_packages(self, amount=1) -> [PacketEntry]:
        return self.data.get_last_packages(amount)

    def get_time_table(self) -> TimeTable:
        return self.data.time_table
