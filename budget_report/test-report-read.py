import pandas as pd

df = pd.read_csv('invoice-export-2024-12-05-08_32.csv')
new_df = df['Invoice line fund distributions'].str.split('\"\"', expand=True)
print(new_df)

print(df.columns[0])

import os
from tkinter import filedialog

ACCEPTED_FILETYPES = [
    ('Comma-separated values', '*.csv'),
    # ('Microsoft Excel', '*.xlsx')
]

folder_path = filedialog.askopenfilename(title='Find file - jaq',
                                         initialdir=os.curdir,
                                         defaultextension='.csv',
                                         filetypes=ACCEPTED_FILETYPES)

print(folder_path)