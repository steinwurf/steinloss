from steinloss.Packet import Packet
from steinloss.PacketTable import PacketTable
from steinloss.utilities import log


class ConsecutiveLostPacketsTable(dict):
    def __init__(self, *args, **kw):
        super(ConsecutiveLostPacketsTable,self).__init__(*args, **kw)
        self.itemlist = super(ConsecutiveLostPacketsTable, self).keys()

    def collect_data(self, packet:Packet, packet_table:PacketTable):
        """ if int(packet.id) > 5:
            i = 0
            while packet_table[int(packet.id) - (i + 1)].received_at == None:
                i += 1
            if i != 0: 
                log('')
            else: 
                pass """