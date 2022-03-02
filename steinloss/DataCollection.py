from steinloss.class_patterns import Singleton
from steinloss.TimeTable import TimeTable
from steinloss.PacketTable import PacketTable
from steinloss.Package import Package, ReceivePackage, SentPackage
from datetime import datetime
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from hurry.filesize import size, verbose



class DataCollection(metaclass=Singleton):
    def __init__(self) -> None:
        self.time_table = TimeTable()
        self.packet_table = PacketTable()

    def get_time_table(self):
        return self.time_table

    def get_packet_table(self):
        return self.packet_table

    def add(self, packet: Package):
        if type(packet) is SentPackage:
            self.packet_table[packet.id].sent_at = packet.time
        elif type(packet) is ReceivePackage:
            self.packet_table[packet.id].received_at = packet.time

            sent_timestamp = self.packet_table[packet.id].sent_at
            self.time_table[sent_timestamp].loss -= 1

        self.time_table[packet.time].add_packet(packet)

    def __contains__(self, item):
        if isinstance(item, Package):
            return item.id in self.packet_table
        elif isinstance(item, datetime):
            return item in self.time_table

    def __getitem__(self, key):
        if isinstance(key, datetime):
            return self.time_table[key]
        else:
            return self.packet_table[key]

    def __repr__(self):
        return f"{str(self.time_table)}\n{str(self.packet_table)}"

    def get_last_packages(self, number_of_packages: int):
        arr = []
        counter = number_of_packages
        i = iter(reversed(self.packet_table))

        while counter > 0:
            key = next(i)
            arr.append(self.packet_table[key])
            counter -= 1

        return arr

    def retrieve_lost_percentage_over_time(self):
        data = {
        'Time': [],
        'Loss': [],
        }
        
        time_table = self.time_table
        base = datetime.now() - timedelta(seconds=30)  # 30 seconds behind

        timestamp_array = np.array([base - timedelta(seconds=i) for i in range(1, 180)])
        for timestamp in timestamp_array:
            data["Time"].append(timestamp)

            loss_decimal = 0
            entry = time_table[timestamp]
            if entry.sent != 0:
                loss_decimal = entry.loss / entry.sent
            loss_pct = loss_decimal * 100
            data['Loss'].append(loss_pct)

        df = pd.DataFrame.from_dict(data)
        
        return df

    def get_actual_package_speed(self):
        time_table = self.get_time_table()

        timestamp = datetime.now() - timedelta(seconds=15) #15 seconds delayed
        time_entry = time_table[timestamp]

        speed = size(time_entry.sent * 1024, system=verbose)

        return speed