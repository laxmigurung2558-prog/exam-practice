"""ETL for the restaurant case: one row per day with total sales, lagged sales, weather and game data."""
import pandas as pd, numpy as np
from scipy import stats

def load(path):
    x = pd.read_excel(path, sheet_name=None)
    s, w, g = x["salesData"], x["weatherData"], x["gameData"]
    d = s.groupby("date").agg(sales=("netTotal", "sum"), sales_7=("netTotal_7", "sum"),
                              sales_28=("netTotal_28", "sum"), sales_364=("netTotal_364", "sum")).reset_index()
    d = d.merge(w, on="date", how="left").merge(g[["date", "gameDay", "homeGame"]], on="date", how="left")
    d[["gameDay", "homeGame"]] = d[["gameDay", "homeGame"]].fillna(0).astype(int)
    return d, x

def ols(df, y, xs):
    X = np.column_stack([np.ones(len(df))] + [df[c].to_numpy(float) for c in xs])
    yv = df[y].to_numpy(float)
    b, *_ = np.linalg.lstsq(X, yv, rcond=None)
    resid = yv - X @ b
    n, k = X.shape
    s2 = resid @ resid / (n - k)
    se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
    t = b / se
    p = 2 * stats.t.sf(np.abs(t), n - k)
    r2 = 1 - (resid @ resid) / ((yv - yv.mean()) @ (yv - yv.mean()))
    return {"terms": ["Intercept"] + xs, "b": b, "se": se, "p": p, "r2": r2, "n": n,
            "adj_r2": 1 - (1 - r2) * (n - 1) / (n - k), "rmse": np.sqrt(s2)}
