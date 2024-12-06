import pandas as pd

df = pd.read_csv('invoice-export-2024-12-05-08_32.csv')
new_df = df['Invoice line fund distributions'].str.split('\"\"', expand=True)
print(new_df)