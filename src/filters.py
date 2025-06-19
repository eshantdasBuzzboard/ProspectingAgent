from src.utils.set import set1, set2, set3, set4, set5
import asyncio
import pandas as pd
from typing import Any
from src.utils.utils import extract_rows_and_match_details

from core.chains.business_intelligence_chains import get_filter_reasoning_businesses
from core.chains.business_intelligence_chains import (
    get_filter_signals,
    run_counter_results,
    return_query_formulator,
)

# Import logger
from logger import info, debug, warning, error, debug_json

df = pd.read_csv("data/Prospects_trimmed_for_reasoning.csv")
de = pd.read_csv("data/Prospects_5000_12052025_040201.csv", low_memory=False)
all_set = set1 + set2 + set3 + set4 + set5


async def get_filter_signalss(search_query) -> Any:
    try:
        debug(f"Starting get_filter_signalss with query: {search_query}")
        sets = [set1, set2, set3, set4, set5]
        # Run all async calls concurrently
        results = await asyncio.gather(
            *[get_filter_signals(s, search_query) for s in sets]
        )

        # Filter logic
        filtered_results = [
            item
            for result in results
            for item in result
            if item.get("Filter_Name") is not None
            or item.get("Filter_value") is not None
        ]

        debug(
            f"get_filter_signalss completed with {len(filtered_results)} filtered results"
        )
        return filtered_results

    except Exception as e:
        error(f"Error in get_filter_signalss: {str(e)}")
        return []


async def get_prospect_filters(search_query):
    try:
        debug(f"Starting get_prospect_filters with query: {search_query}")

        filter_signals_result, counter_results_result = await asyncio.gather(
            get_filter_signalss(search_query), run_counter_results(search_query)
        )
        debug_json(filter_signals_result, "filter ai")

        debug(
            f"Filter signals result count: {len(filter_signals_result) if filter_signals_result else 0}"
        )

        rows = extract_rows_and_match_details(filter_signals_result)
        debug(f"Extracted rows count: {len(rows) if rows else 0}")

        desc_map = {
            d["Signal Name"]: d["Description"] for d in all_set if isinstance(d, dict)
        }
        result_description = [
            {
                "Signal Name": item["Filter_Name"],
                "Description": desc_map.get(item["Filter_Name"]),
            }
            for item in filter_signals_result
            if item["Filter_Name"] in desc_map
        ]

        companies = []
        for i in rows[:40]:
            companies.append(i["Company Name"])

        filtered_df = df[df["Company Name"].isin(companies)]
        filtered_json = filtered_df.to_json(orient="records")
        businesses = filtered_json
        signals_description = result_description
        selected_signals = filter_signals_result

        debug("get_prospect_filters completed successfully")
        return businesses, signals_description, selected_signals

    except Exception as e:
        error(f"Error in get_prospect_filters: {str(e)}")
        # Return empty but valid data structures
        return "[]", [], []


async def get_main_prospects(
    search_query, signals_description, selected_signals, businesses, products
):
    try:
        debug(f"Starting get_main_prospects with query: {search_query}")
        debug(
            f"Input parameters - signals_description count: {len(signals_description) if signals_description else 0}"
        )
        debug(
            f"Input parameters - selected_signals count: {len(selected_signals) if selected_signals else 0}"
        )

        response = await get_filter_reasoning_businesses(
            search_query=search_query,
            signals_description=signals_description,
            selected_signals=selected_signals,
            businesses=businesses,
            products=products,
        )

        # Add null check and logging
        if response is None:
            warning("get_filter_reasoning_businesses returned None")
            debug_json(None, "RESPONSE_FROM_get_filter_reasoning_businesses")
            return []

        if not isinstance(response, (list, tuple)):
            error(
                f"get_filter_reasoning_businesses returned unexpected type: {type(response)}"
            )
            debug_json(response, "UNEXPECTED_RESPONSE_TYPE")
            return []

        if len(response) == 0:
            warning("get_filter_reasoning_businesses returned empty list")
            return []

        debug(f"get_filter_reasoning_businesses returned {len(response)} items")
        debug_json(response, "RESPONSE_FROM_get_filter_reasoning_businesses")

        company_list = []
        for i, item in enumerate(response):
            try:
                if isinstance(item, dict) and "Company Name" in item:
                    company_list.append(item["Company Name"])
                    debug(f"Added company {i + 1}: {item['Company Name']}")
                else:
                    warning(
                        f"Item {i + 1} does not have 'Company Name' key or is not a dict: {type(item)}"
                    )
                    debug_json(item, f"INVALID_ITEM_{i + 1}")
            except Exception as e:
                error(f"Error processing item {i + 1} in response: {str(e)}")
                debug_json(item, f"ERROR_ITEM_{i + 1}")
                continue

        debug(f"Extracted {len(company_list)} company names")

        if not company_list:
            warning("No valid company names found in response")
            return []

        columns_to_extract = [
            "Company Name",
            "Website URL",
            "City",
            "State",
            "Primary Category",
        ]

        try:
            filtered_data = de[de["Company Name"].isin(company_list)][
                columns_to_extract
            ].to_dict(orient="records")
            debug(f"Filtered data from CSV: {len(filtered_data)} records")
        except Exception as e:
            error(f"Error filtering CSV data: {str(e)}")
            return []

        info_lookup = {item["Company Name"]: item for item in filtered_data}

        # Merge data from both lists
        merged_data = []
        for item in response:
            try:
                if isinstance(item, dict) and "Company Name" in item:
                    company_name = item["Company Name"]
                    if company_name in info_lookup:
                        combined = {
                            **item,
                            **info_lookup[company_name],
                        }  # Merge dictionaries
                        merged_data.append(combined)
                        debug(f"Merged data for company: {company_name}")
                    else:
                        warning(f"Company {company_name} not found in CSV data")
                else:
                    warning(f"Invalid item structure in response: {type(item)}")
            except Exception as e:
                error(f"Error merging data for item: {str(e)}")
                debug_json(item, "ERROR_MERGING_ITEM")
                continue

        info(f"get_main_prospects completed with {len(merged_data)} prospects")
        return merged_data

    except Exception as e:
        error(f"Error in get_main_prospects: {str(e)}")
        return []


async def get_formulated_query(current_quesion, previous_question):
    try:
        debug(
            f"Formulating query - Previous: '{previous_question}', Current: '{current_quesion}'"
        )
        formulated_query = await return_query_formulator(
            previous_question, current_quesion
        )
        debug(f"Formulated query result: '{formulated_query}'")
        return formulated_query
    except Exception as e:
        error(f"Error in get_formulated_query: {str(e)}")
        return current_quesion  # Return original query as fallback
