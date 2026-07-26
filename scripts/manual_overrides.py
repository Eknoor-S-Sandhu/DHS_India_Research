"""
Manually reviewed and confirmed district-name matches flagged by the fuzzy
matcher in build_district_crosswalk.py.

Key: (state, shdist, nfhs_district_name) -> census_distid
Using shdist in the key (not just district name) avoids any risk of a
same-named district in a different state accidentally picking up an override
meant for a different row.
"""

import pandas as pd

MANUAL_OVERRIDES = {
    # (state, shdist, nfhs_district_name): census_distid
    ("gujarat", 10, "MAHESANA"): 10,                                  # Mahesana / Mahasana
    ("jammu & kashmir", 11, "Kathua"): 11,                            # Kathua / Kuthua
    ("madhya pradesh", 39, "Surguja"): 39,                            # Surguja / Sarguja
    ("rajasthan", 7, "DHAULPUR"): 7,                                  # Dhaulpur / Dholpur
    ("rajasthan", 18, "JALOR"): 18,                                   # Jalor / Jalaur
    ("rajasthan", 22, "CHITTAURGARH"): 22,                            # Chittaurgarh / Chittorgarh
    ("tamil nadu", 15, "Pasumpon Muthuramalinga The"): 15,            # Pasumpon Muthuramalinga Thevar / Pasumpon M. Thevar
    ("west bengal", 11, "HAORA"): 11,                                 # Haora / Howrah
    ("bihar", 40, "Pas. Singhbhum"): 40,                              # Pashchimi Singhbhum (NFHS-2 only)
    ("jammu & kashmir", 2, "Palwama"): 2,                             # Palwama / Pulwama (NFHS-2 only)
    ("jammu & kashmir", 5, "Barmala"): 5,                             # Barmala / Baramula (NFHS-2 only)
    ("jammu & kashmir", 1, "Anandnagar"): 1,                          # Anandnagar / Anantnag (NFHS-2 only)
}


def apply_overrides(crosswalk_df):
    """
    Applies MANUAL_OVERRIDES to a crosswalk dataframe produced by
    build_district_crosswalk.py. Overwrites census_distid and match_score
    (set to 100) wherever a (state, shdist, nfhs_district_name) key matches.
    Returns the updated dataframe and a log of what was changed.
    """
    df = crosswalk_df.copy()
    changes = []

    for idx, row in df.iterrows():
        key = (row["state"], row["shdist"], row["nfhs_district_name"])
        if key in MANUAL_OVERRIDES:
            old_distid = row["census_distid"]
            new_distid = MANUAL_OVERRIDES[key]
            df.at[idx, "census_distid"] = new_distid
            df.at[idx, "match_score"] = 100
            df.at[idx, "match_source"] = "manual_override"
            changes.append({
                "state": row["state"],
                "shdist": row["shdist"],
                "nfhs_district_name": row["nfhs_district_name"],
                "old_distid": old_distid,
                "new_distid": new_distid,
            })

    return df, pd.DataFrame(changes)


if __name__ == "__main__":
    for round_label, path in [
        ("NFHS-1", "data/processed/district_crosswalks/nfhs1_district_crosswalk.csv"),
        ("NFHS-2", "data/processed/district_crosswalks/nfhs2_district_crosswalk.csv"),
    ]:
        xwalk = pd.read_csv(path)
        if "match_source" not in xwalk.columns:
            xwalk["match_source"] = "fuzzy"

        updated, changes_log = apply_overrides(xwalk)
        updated.to_csv(path, index=False)

        print(f"{round_label}: applied {len(changes_log)} manual overrides")
        if len(changes_log):
            print(changes_log.to_string(index=False))
        print()
