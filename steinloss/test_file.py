import pandas as pd 

df = pd.read_csv('/home/jeppe/Downloads/packet_time_data(5).csv')
df.to_json('test', orient='records')