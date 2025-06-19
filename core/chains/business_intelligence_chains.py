from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import JsonOutputParser
import logging
from typing import Any
from core.pydantic_classes.pydantic_class import (
    CompaniesSelected,
    Signals,
    QuestionReformulatorOutput,
    CompaniesSelected_Filters,
)
from core.prompts.prospecting_agent_prompts import (
    intelligence_prompt,
    filter_prompt,
    counter_prompt,
    filter_reasoning_prompt,
    query_context_prompt,
)


load_dotenv()

llm: BaseChatModel = ChatOpenAI(model="gpt-4.1", max_retries=3, temperature=0, seed=42)
llm_varied: BaseChatModel = ChatOpenAI(
    model="gpt-4.1", max_retries=3, temperature=1, seed=42
)
llm_pro = ChatOpenAI(model="o4-mini")


async def get_intelligence_prospects(
    products_info, business_info
) -> list[dict[str, str]] | None:
    try:
        llmr = llm.with_structured_output(schema=CompaniesSelected)
        intelligence_chain = intelligence_prompt | llmr
        input_data = {"business": business_info, "products": products_info}
        result = await intelligence_chain.ainvoke(input_data)

        final_results = []
        for i in result.companies:
            final_results.append(
                {
                    "Company_name": i.company_name,
                    "Reason_selected": i.reason,
                    "rank": i.rank,
                    "rank_reason": i.rank_reason,
                }
            )
        return final_results
    except Exception as e:
        logging.error(f"Error occured {e}")


async def get_filter_signals(
    section_value, search_query
) -> list[dict[str, str]] | None:
    try:
        llmr = llm.with_structured_output(schema=Signals)
        signal_chain = filter_prompt | llmr
        input_data = {"signals": section_value, "search_query": search_query}
        result = await signal_chain.ainvoke(input_data)
        final_result = []
        for i in result.signals:
            final_result.append(
                {
                    "Filter_Name": i.signal_name,
                    "Filter_value": i.signal_value,
                    "Selected_Reason": i.selected_reason,
                }
            )
        return final_result

    except Exception as e:
        logging.error(f"Error occured {e}")
        return []


async def get_filter_reasoning_businesses(
    search_query, selected_signals, signals_description, businesses, products
) -> Any:
    try:
        llmr = llm_varied.with_structured_output(schema=CompaniesSelected_Filters)
        filter_reasoning_chain = filter_reasoning_prompt | llmr
        input_data = {
            "search_query": search_query,
            "selected_signals": selected_signals,
            "signals_description": signals_description,
            "businesses": businesses,
            "products": products,
        }
        result = await filter_reasoning_chain.ainvoke(input_data)
        final_results = []
        for i in result.companies:
            final_results.append(
                {
                    "Company Name": i.company_name,
                    "Reason_selected": i.reason,
                    "rank": i.rank,
                    "rank_reason": i.rank_reason,
                    "products_to_sell": i.products,
                    "reason_why_product_selected": i.products_reason,
                }
            )
        return final_results
    except Exception as e:
        logging.error(f"Error occured  {e}")
        return None


async def run_counter_results(search_query, max_retries=3) -> int | None:
    try:
        counter_chain = counter_prompt | llm | JsonOutputParser()
        input_data = {
            "search_query": search_query,
        }
        result = await counter_chain.ainvoke(input_data)
        return result["count"]
    except Exception as e:
        logging.error(f"Error occured  {e}")
        return None


async def return_query_formulator(
    previous_query,
    current_query,
    max_retries=10,
) -> Any:
    """Return the final output"""
    try:
        structured_llm = llm.with_structured_output(schema=QuestionReformulatorOutput)
        query_validator_chain = query_context_prompt | structured_llm
        input_data = {
            "previous_question": previous_query,
            "current_question": current_query,
        }
        result = await query_validator_chain.ainvoke(input_data)
        return result.reformulated_question
    except Exception as e:
        return f"An unexpected error occurred {e}"
