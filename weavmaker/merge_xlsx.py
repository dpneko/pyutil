import pandas as pd
import os
import tkinter as tk
import openpyxl
from tkinter import filedialog
 
root = tk.Tk()
root.withdraw()
 
dir_path = filedialog.askdirectory(initialdir=os.getcwd(), title="open xlsx directory")
# dir_path = "/Users/xiang/Downloads/report"
# dir_path = os.getcwd()

dfs = []
paths = []
for file in os.listdir(dir_path):
    if file.endswith(".xlsx") and not file.startswith("~$"):
        path = os.path.join(dir_path, file)
        paths.append(path)
        df = pd.read_excel(path, index_col=None, na_values=["NA"], header=2, engine='openpyxl')
        dfs.append(df)
print("xlsxs to be merged:")
print(os.linesep.join(paths))

all = pd.concat(dfs)

# set 'Campaign Name'
default_campaign = all["Product Name"].iloc[0]
campaign = input(f"input campaign name(default {default_campaign}):")
if len(campaign) == 0:
    campaign = default_campaign
all['Campaign Name'] = campaign
print(f"set 'Campaign Name' to {campaign} Done!")

# replace 'The Trade Desk' to 'Progr'
all['MPL Group'] = all['MPL Group'].replace({
    "The Trade Desk | Display": "Progr.Display",
    "The Trade Desk | Video": "Progr.Video",
    "The Trade Desk | Audio": "Progr.Audio",
    "The Trade Desk | DOOH": "Progr.OOH"
})
print(f"replace 'The Trade Desk' to 'Progr' Done!")

# delete Managed Service Operation Fee
all = all[all['MPL Group'] != 'Managed Service Operation Fee']
print(f"delete Managed Service Operation Fee Done!")

# save excel
save_path = filedialog.asksaveasfilename(filetypes=[('Excel Worksheet','*.xlsx')])
all = all.T.reset_index().T
all.to_excel(save_path, header=False, index=False, sheet_name="Report", startrow=2, engine='openpyxl')
