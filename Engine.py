import pandas as pd
from db import init_db, save_engine_results

def run_smt_engine():
    # 1. Initialize Database
    init_db()

    # 2. Load CSV inputs
    df_erp = pd.read_csv("erp_bom.csv")
    df_machine = pd.read_csv("smt_machine_log.csv")

    # 3. Merge data
    df_merged = pd.merge(
        df_erp, 
        df_machine, 
        on=["work_order", "article_number"], 
        how="inner"
    )

    # 4. Math Engine calculations
    df_merged["mounted_qty"] = df_merged["picks_attempted"] - df_merged["drops_scrap"]
    df_merged["scrap_pct"] = (df_merged["drops_scrap"] / df_merged["picks_attempted"]) * 100
    df_merged["scrap_pct"] = df_merged["scrap_pct"].round(2)

    df_merged["status"] = df_merged["scrap_pct"].apply(
        lambda x: "EXCEEDED (>2%)" if x > 2.0 else "OK"
    )

    df_merged["allowed_drops"] = (df_merged["picks_attempted"] * 0.02).astype(int)
    df_merged["phantom_risk_qty"] = (df_merged["drops_scrap"] - df_merged["allowed_drops"]).clip(lower=0)

    # Filter columns to store
    df_to_save = df_merged[[
        "work_order", "feeder_slot", "article_number", 
        "picks_attempted", "drops_scrap", "scrap_pct", "status", "phantom_risk_qty"
    ]]

    # 5. Save to SQLite
    save_engine_results(df_to_save)

if __name__ == "__main__":
    run_smt_engine()
