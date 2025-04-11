import pandas as pd

df = pd.read_csv('test_bias_4_01_to_4_05.csv')
df = df.head(3)
df.to_csv('test_bias.csv')
