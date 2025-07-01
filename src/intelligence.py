import pandas as pd
from core.chains.business_intelligence_chains import get_intelligence_prospects
from logger import debug_json, info

df1 = pd.read_csv("data/Prospects_5000_12052025_040201.csv", low_memory=False)
df2 = pd.read_csv("data/Prospects_trimmed_for_reasoning.csv", low_memory=False)


async def get_propsects(state, cateogry, products) -> dict:
    full_de = df1[(df1["Primary Category"] == cateogry) & (df1["State"] == state)]
    partialdf = full_de[df2.columns]
    json_data_for_dataframe = partialdf.to_json(orient="records")

    business_info = json_data_for_dataframe
    results = await get_intelligence_prospects(
        business_info=business_info, products_info=products
    )

    companies = [i["Company_name"] for i in results]
    info(f"Companies found are {companies}")
    debug_json(results, "Intelligence results")

    columns_to_extract = [
        "Company Name",
        "Website URL",
        "City",
        "State",
        "Primary Category",
    ]

    # Ensure both columns are string type
    df1["Company Name"] = df1["Company Name"].astype(str).str.strip()
    companies = [str(name).strip() for name in companies]

    # Filter df1 for relevant companies and extract columns
    filtered_df = df1[df1["Company Name"].isin(companies)][columns_to_extract]

    # Convert results to DataFrame
    results_df = pd.DataFrame(results).rename(columns={"Company_name": "Company Name"})
    results_df["Company Name"] = results_df["Company Name"].astype(str).str.strip()

    # Merge on 'Company Name' column
    merged_df = pd.merge(filtered_df, results_df, on="Company Name", how="left")

    debug_json(merged_df.to_dict(orient="records"), "Merged DataFrame")
    return merged_df.to_dict(orient="records")
