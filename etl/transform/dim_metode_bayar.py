import logging
import re
import pandas as pd

def build_dim_metode_bayar(df_penjualan):
    unique = df_penjualan['metode_bayar'].astype("string").str.strip().dropna().unique()

    dim = pd.DataFrame({"metode_bayar": unique})
    dim = dim[dim["metode_bayar"] !=    ""].reset_index(drop=True)

    dim["metode_bayar_key"] = dim.index + 1

    row_default = pd.DataFrame([{
        'metode_bayar_key': 0,
        'metode_bayar': 'Tidak Diketahui'
    }])
    dim = pd.concat([row_default, dim], ignore_index=True)

    return dim[["metode_bayar_key", "metode_bayar"]]