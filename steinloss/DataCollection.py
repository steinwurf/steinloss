from steinloss.class_patterns import Singleton
from steinloss.TimeTable import TimeTable
from steinloss.PacketTable import PacketTable
from steinloss.Package import Package
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from hurry.filesize import size, verbose
import copy


class DataCollection(metaclass=Singleton):
    def __init__(self) -> None:
        self.time_table = TimeTable()
        self.packet_table = PacketTable()

    def get_time_table(self):
        return self.time_table

    def get_packet_table(self):
        return self.packet_table

    def add(self, packet: Package):

        # Register the packet in the packettable
        self.packet_table[packet.id].add_packet(packet)

        # Register the packet in the timetable.
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
            'time': [],
            'loss': [],
        }
        time_table = self.time_table
        base = datetime.now() - timedelta(seconds=30)  # 30 seconds behind

        data['time'] = np.array([base - timedelta(seconds=i) for i in range(1, 180)])

        for timestamp in data['time']:
            entry = time_table[timestamp]

            if entry.sent != 0:
                loss_pct = entry.loss / entry.sent * 100
            else:
                loss_pct = 0

            data['loss'].append(loss_pct)

        df = pd.DataFrame.from_dict(data)
        return df

    def retrieve_sent_recieved_packets_over_time_df(self):
        data = {
            'time': [],
            'sent-count': [],
            'recieved-count': []
        }

        base = datetime.now() - timedelta(seconds=30)  # 30 seconds behind

        data['time'] = np.array([base - timedelta(seconds=i) for i in range(1, 180)])
        for timestamp in data['time']:
            entry = self.time_table[timestamp]

            data['recieved-count'].append(entry.sent - entry.loss)
            data['sent-count'].append(entry.sent)

        df = pd.DataFrame.from_dict(data)
        return df

    def get_actual_package_speed(self):
        time_table = self.get_time_table()

        timestamp = datetime.now() - timedelta(seconds=15)  # 15 seconds delayed
        time_entry = time_table[timestamp]

        speed = size(time_entry.sent * 1024, system=verbose)

        return speed

    def get_package_loss_from_time(self, timestamp: datetime):
        time_entry = self.time_table[timestamp]

        packages_sent = time_entry.sent
        packages_recv = time_entry.received

        if packages_sent == 0 or packages_recv == 0:
            return 0
        else:
            return 1 - packages_recv / packages_sent

    def retrieve_individual_packet_df(self):
        data = {
            'packet_id' : [],
            'sent_at' : [],
            'recieved_at' : [],
            'recieved' : [],
        }
        
        copy_of_packet_table = copy.deepcopy(dict(self.packet_table))

        for packet_id in copy_of_packet_table:
            data['packet_id'].append(packet_id)

            data['sent_at'].append(copy_of_packet_table[packet_id].sent_at)

            data['recieved_at'].append(copy_of_packet_table[packet_id].received_at)

            if copy_of_packet_table[packet_id].received_at is None:
                data['recieved'].append(False)
            else:
                data['recieved'].append(True)
        df = pd.DataFrame.from_dict(data)
        return df

