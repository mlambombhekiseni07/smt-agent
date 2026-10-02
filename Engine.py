import pandas as pd

def run_smt_engine():
    # 1. Load the two CSV files from your SMT Agent folder
    df_erp = pd.read_csv("erp_bom.csv")
    df_machine = pd.read_csv("smt_machine_log.csv")

    # 2. Merge data dynamically on work_order and article_number
    df_merged = pd.merge(
        df_erp, 
        df_machine, 
        on=["work_order", "article_number"], 
        how="inner"
    )

    # 3. Calculate Scrap % and Mounted Quantities
    df_merged["mounted_qty"] = df_merged["picks_attempted"] - df_merged["drops_scrap"]
    df_merged["scrap_pct"] = (df_merged["drops_scrap"] / df_merged["picks_attempted"]) * 100
    df_merged["scrap_pct"] = df_merged["scrap_pct"].round(2)

    # 4. Apply 2.0% Scrap Guardrail Logic
    df_merged["status"] = df_merged["scrap_pct"].apply(
        lambda x: "EXCEEDED (>2%)" if x > 2.0 else "OK"
    )

    # 5. Calculate Phantom Inventory Risk (Drops exceeding 2% allowance)
    df_merged["allowed_drops"] = (df_merged["picks_attempted"] * 0.02).astype(int)
    df_merged["phantom_risk_qty"] = (df_merged["drops_scrap"] - df_merged["allowed_drops"]).clip(lower=0)

    # Display results
    print("\n================ SMT ENGINE REAL-TIME ANALYSIS ================")
    print(df_merged[[
        "work_order", "feeder_slot", "article_number", 
        "picks_attempted", "drops_scrap", "scrap_pct", "status", "phantom_risk_qty"
    ]].to_string(index=False))

if __name__ == "__main__":
    run_smt_engine()
