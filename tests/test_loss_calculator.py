from datetime import datetime

from src.loss_calculator import Loss_Calculator
from src.packet_entity import Packet_entity


class Test_Loss_Calculator:
    def test_initiate_loss_calculator(self):
        Loss_Calculator()

    def test_loss_calculator_can_add_packet_entry(self):
        loss_calculator = Loss_Calculator()

        loss_calculator.add(Packet_entity('1', datetime.now()))

        assert loss_calculator['1'] is not None
