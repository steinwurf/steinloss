from steinloss.Packet import Packet
from steinloss.PacketTable import PacketTable
from steinloss.utilities import log


class ConsecutiveLostPacketsTable(dict):
    def __init__(self, *args, **kw):
        super(ConsecutiveLostPacketsTable,self).__init__(*args, **kw)
        self.itemlist = super(ConsecutiveLostPacketsTable, self).keys()

    def add(self, list_of_recieved_packets):
        # These two functions are needed to first calculate the missing values in the recieved packets list
        # and afterwards count the consecutive value in the list
        def missing_elements(L):
            return sorted(set(range(L[-1], L[0])) - set(L))

        def count_consec(lst):
            consec = [1]
            for x, y in zip(lst, lst[1:]):
                if x == y - 1:
                    consec[-1] += 1
                else:
                    consec.append(1)
            return consec


        missing_packets =  missing_elements(list_of_recieved_packets)
        cons_value = count_consec(missing_packets)
        # Add the values to the 
        for i in cons_value:
            if i in self.keys():
                self[i] += 1
            else:
                self[i] = 1

