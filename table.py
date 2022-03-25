import pandas as pd


def read_md(path):
    return pd.read_table(path, sep=" *[\||\+] *", header=0, skipinitialspace=True, engine='python', skiprows=[0,2], skipfooter=1).dropna(axis=1, how='all')
