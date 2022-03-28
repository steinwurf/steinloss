import pandas as pd
from itertools import groupby
import time


#df = pd.read_csv('/home/jeppe/Downloads/packet_data(1).csv')

import bitmath

size = bitmath.Byte(bytes=4026).best_prefix()

print(round(size, 2))
