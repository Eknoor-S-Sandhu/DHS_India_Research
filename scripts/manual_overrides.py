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
    ("madhya pradesh", 24, "Khargone"): 24,      # Khargone / West Nimar (1991 name)
    ("maharashtra", 1, "MUMBAI"): 1,             # Mumbai / Greater Bombay (1991 name)
    ("tamil nadu", 1, "Chennai"): 1,             # Chennai / Madras (1991 name)                                # Chennai -- fuzzy matched to Chengalpattu-MGR (69.2); 1991 sheet likely says "Madras"
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

    # Northeast states (Arunachal Pradesh, Manipur, Meghalaya, Mizoram,
    # Nagaland): dist_list_81_91.xlsx had only placeholder rows for these
    # five states, so the fuzzy matcher had no real candidate pool and
    # fell back to matching on the state name. Resolved by confirming
    # shdist == 1991 Census distid directly for these states, verified via
    # 1991 PCA (Rural) district extraction + DHS user forum thread 232
    # (Fred Arnold, DHS Program) confirming NFHS district codes follow
    # standard 1991 Census coding.
    ("arunachal pradesh", 1, "TAWANG"): 1,
    ("arunachal pradesh", 2, "WEST KAMENG"): 2,
    ("arunachal pradesh", 3, "EAST KAMENG"): 3,
    ("arunachal pradesh", 4, "LOWER SUBANSIRI"): 4,
    ("arunachal pradesh", 5, "UPPER SUBANSIRI"): 5,
    ("arunachal pradesh", 6, "WEST SIANG"): 6,
    ("arunachal pradesh", 7, "EAST SIANG"): 7,
    ("arunachal pradesh", 8, "DIBANG VALLEY"): 8,
    ("arunachal pradesh", 9, "Lohit"): 9,
    ("arunachal pradesh", 10, "CHANGLANG"): 10,
    ("arunachal pradesh", 11, "TIRAP"): 11,
    ("manipur", 1, "SENAPATI"): 1,
    ("manipur", 2, "TAMENGLONG"): 2,
    ("manipur", 3, "CHURACHANPUR"): 3,
    ("manipur", 4, "CHANDEL"): 4,
    ("manipur", 5, "THOUBAL"): 5,
    ("manipur", 6, "BISHNUPUR"): 6,
    ("manipur", 7, "IMPHAL"): 7,
    ("manipur", 8, "UKHRUL"): 8,
    ("meghalaya", 1, "JAINTIA HILLS"): 1,
    ("meghalaya", 2, "EAST KHASI HILLS"): 2,
    ("meghalaya", 3, "WEST KHASI HILLS"): 3,
    ("meghalaya", 4, "EAST GORA HILLS"): 4,                           # East Gora Hills / East Garo Hills
    ("meghalaya", 5, "WEST GARO HILLS"): 5,
    ("mizoram", 1, "AIZAWL"): 1,
    ("mizoram", 2, "LUNGLEI"): 2,
    ("mizoram", 3, "CHHIMTUIPUI"): 3,
    ("nagaland", 1, "KOHIMA"): 1,
    ("nagaland", 2, "PHEK"): 2,
    ("nagaland", 3, "ZUNHEBOTO"): 3,
    ("nagaland", 4, "WOKHA"): 4,
    ("nagaland", 5, "MOKOKCHUNG"): 5,
    ("nagaland", 6, "TUENSANG"): 6,
    ("nagaland", 7, "MON"): 7,
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