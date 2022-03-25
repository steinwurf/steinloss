import pandas as pd
from itertools import groupby
import time


df = pd.read_csv('/home/jeppe/Downloads/packet_data(1).csv')
def groups(l):
    return [len(list(g)) for i, g in groupby(l) if i == 0]

start = time.time()
list = groups(df['recieved'])
end = time.time()

final_time = end - start
print(f'{final_time=}')
