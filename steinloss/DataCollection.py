from calendar import c
from struct import pack
from time import time
from steinloss.class_patterns import Singleton
from steinloss.TimeTable import TimeTable
from steinloss.PacketTable import PacketTable
from steinloss.Packet import Packet, ReceivePackage, SentPackage
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from hurry.filesize import size, verbose
import copy
from itertools import groupby
import bitmath
from steinloss.ConsecutiveLostPacketsTable import ConsecutiveLostPacketsTable
import collections

KILOBYTE = 1024

class DataCollection(metaclass=Singleton):
    def __init__(self) -> None:
        self.time_table = TimeTable()
        self.packet_table = PacketTable()
        self.consecutive_packets_lost_table = ConsecutiveLostPacketsTable()
        self.latency = None

        self.delay = 1  # Number of seconds the dashboard is behind realtime.
        self.data_interval = 180  # The number of seconds in the data window (only interested in the last two X seconds).
        self.queue_size = 200
        self.recieved_packet_queue = collections.deque(maxlen=self.queue_size) # The last 200 recieved packets is in this queue, must be the samme as in add methode (before %)

    def get_time_table(self):
        return self.time_table

    def get_packet_table(self):
        return self.packet_table
    def get_consecutive_packets_lost_table(self):
        return self.consecutive_packets_lost_table
    
    def get_consecutive_packets_lost_df(self):
        df = pd.DataFrame(self.consecutive_packets_lost_table.items(),columns=['lost_cons_packets','count'])

        #add normalized count
        df['normalized_count'] = df['count']/df['count'].sum()

        return df

    def add(self, packet: Packet):
        # Register the packet in the packettable
        self.packet_table[packet.id].add_packet(packet)

        # Register the packet in the timetable.
        self.time_table[packet.time].add_packet(packet)

        # Register recieved packet in the packet queue
        if isinstance(packet, ReceivePackage):
            self.recieved_packet_queue.appendleft(int(packet.id))

            # Register all the packets in the recieved package queue in the consecutive pakcet lost table
            if int(packet.id) % self.queue_size == 0:
                self.consecutive_packets_lost_table.add(self.recieved_packet_queue)

            # Update the latency
            latency_datetime = self.packet_table[packet.id].received_at - self.packet_table[packet.id].sent_at
            latency_miliseconds = latency_datetime.total_seconds() * 1000
            self.latency = latency_miliseconds


    def __contains__(self, item):
        if isinstance(item, Packet):
            return item.id in self.packet_table
        elif isinstance(item, datetime):
            return item in self.time_table

    def __getitem__(self, key):
        if isinstance(key, datetime):
            return self.time_table[key]
        else:
            return self.packet_table[key]

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
        base = datetime.now() - timedelta(seconds= self.delay) 

        data['time'] = np.array([base - timedelta(seconds=i) for i in range(1, self.data_interval)])

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

        base = datetime.now() - timedelta(seconds=self.delay)  # 30 seconds behind

        data['time'] = np.array([base - timedelta(seconds=i) for i in range(1, self.data_interval)])
        for timestamp in data['time']:
            entry = self.time_table[timestamp]

            data['recieved-count'].append(entry.sent - entry.loss)
            data['sent-count'].append(entry.sent)

        df = pd.DataFrame.from_dict(data)
        return df

    def get_actual_package_speed(self):
        time_table = self.get_time_table()

        timestamp = datetime.now() - timedelta(seconds=self.delay)
        time_entry = time_table[timestamp]

        speed = bitmath.Byte(bytes=time_entry.sent * KILOBYTE).best_prefix()

        # Round speed 
        speed = f'{round(float(speed),2)} {speed.unit}'

        return speed

    def get_package_loss_from_time(self, timestamp: datetime):
        time_entry = self.time_table[timestamp]

        packages_sent = time_entry.sent
        packages_recv = time_entry.received

        if packages_sent == 0 or packages_recv == 0:
            return 0
        else:
            return 1 - packages_recv / packages_sent

    def retrieve_individual_packet_df_from_seconds(self, last_X_seconds=None):
        if last_X_seconds is None:
            last_X_seconds = self.data_interval

        data = {
            'packet_id' : [],
            'sent_at' : [],
            'recieved_at' : [],
            'recieved' : [],
        }

        base = datetime.now() - timedelta(seconds=last_X_seconds)
        snapshot_packet_table = dict(self.packet_table)
        filtered_packet_table = { key:value for (key,value) in snapshot_packet_table.items() if value.sent_at >= base}
        copy_of_packet_table = copy.deepcopy(filtered_packet_table)

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

    def retrieve_individual_packet_df_from_packets(self, list_of_packet_id = None):
        if list_of_packet_id is None:
            return None
        data = {
            'packet_id' : [],
            'sent_at' : [],
            'recieved_at' : [],
            'recieved' : [],
        }

        for packet_id in list_of_packet_id:
            data['packet_id'].append(packet_id)

            data['sent_at'].append(self.packet_table[packet_id].sent_at)

            data['recieved_at'].append(self.packet_table[packet_id].received_at)

            if self.packet_table[packet_id].received_at is None:
                data['recieved'].append(False)
            else:
                data['recieved'].append(True)
        df = pd.DataFrame.from_dict(data)
        return df
        

    def retrieve_count_of_consecutive_lost_packets(self):
        df_indivdual_packets = self.retrieve_individual_packet_df_from_packets(self.recieved_packet_queue)

        def return_list_of_consecutive_count(l):
            return [len(list(g)) for i, g in groupby(l) if i == 0]

        list_of_consecutive_lost_packets = return_list_of_consecutive_count(df_indivdual_packets['recieved'])

        df = pd.DataFrame(list_of_consecutive_lost_packets, columns=['count'])

        return df


    def get_status_report(self):
        server_status = 'Shutdown'
        probe_status = 'Shutdown'
        latency = None
        sent_packets = None
        recv_packets = None
        speed = 0

        time_table = self.get_time_table()

        timestamp = datetime.now() - timedelta(seconds=self.delay)
        time_entry = time_table[timestamp]

        # Check if the server is running

        if time_entry.sent != 0:
            server_status = 'Running'

        if time_entry.received != 0:
            probe_status = 'Running'
        
        # Sent/recv packets 
        
        sent_packets = time_entry.sent
        recv_packets = time_entry.received

        # Get the speed
        speed = self.get_actual_package_speed()

        latency = self.latency

        return server_status, probe_status, sent_packets, recv_packets, latency, speed
