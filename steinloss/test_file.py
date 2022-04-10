import pandas as pd
import plotly.graph_objects as go

dict1 = {1:200, 2:13}

df = pd.DataFrame(dict1.items(),columns=['lost_cons_packets','count'])
fig = go.Figure(go.Bar(x=df['lost_cons_packets'], y=df['count']))
fig.show()

