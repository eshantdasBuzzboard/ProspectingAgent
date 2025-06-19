import streamlit as st
import asyncio
from src.filters import get_prospect_filters, get_main_prospects, get_formulated_query
import json

from src.session import (
    initialize_chat_history,
    # get_last4_chat_history,
    add_to_chat_history,
    get_last_question,
)

from src.utils.constants import PRODUCTS
from langchain_core.messages import HumanMessage, AIMessage

# Import the simple logger
from logger import info, debug, debug_json, warning, error

info("Application startup initiated - Filter Agent")

try:
    st.set_page_config(page_title="Filter Agent", page_icon="🔍", layout="wide")
    debug("Page config set successfully")
except Exception as e:
    error(f"Failed to set page config: {str(e)}")
    st.error("Failed to initialize page configuration")

# Navigation
try:
    if st.button("← Back to Home"):
        info("User clicked Back to Home button")
        st.switch_page("main.py")
except Exception as e:
    error(f"Navigation button error: {str(e)}")

try:
    st.title("🔍 Filter Agent")
    st.markdown("---")
    debug("Main title and separator rendered")
except Exception as e:
    error(f"Error rendering main title: {str(e)}")

# Products Display Section
try:
    st.subheader("🎯 Your Onboarding Products")

    for product_name, product_description in PRODUCTS.items():
        with st.expander(f"📋 {product_name}", expanded=True):
            st.write(product_description)

    st.markdown("---")
    debug("Products section rendered successfully")

except Exception as e:
    error(f"Error rendering products section: {str(e)}")

# Sidebar for settings
try:
    with st.sidebar:
        st.header("Search Settings")
        st.markdown("Configure your prospect search parameters")
        debug("Sidebar rendered successfully")
except Exception as e:
    error(f"Error rendering sidebar: {str(e)}")

# Main interface
try:
    st.subheader("🎯 Prospect Search")
    st.markdown("Enter your search query to find the best prospects for your business")
    debug("Main interface elements rendered")
except Exception as e:
    error(f"Error rendering main interface: {str(e)}")

# Search input
try:
    search_query = st.text_input(
        "Search Query",
        placeholder="e.g., automotive dealers in Texas with website issues",
        help="Enter a descriptive search query about the type of prospects you're looking for",
    )
    debug(
        f"Search input field rendered. Query length: {len(search_query) if search_query else 0}"
    )
except Exception as e:
    error(f"Error rendering search input: {str(e)}")
    search_query = ""

# Search button
if st.button("🔍 Search Prospects", type="primary", use_container_width=True):
    info(f"Search button clicked with query: '{search_query}'")

    if search_query:
        try:
            # Initialize chat history
            info("Initializing chat history")
            initialize_chat_history()
            debug("Chat history initialized successfully")
        except Exception as e:
            error(f"Failed to initialize chat history: {str(e)}")
            st.error("Failed to initialize session. Please refresh the page.")
            st.stop()

        try:
            # Get last question for context
            info("Retrieving last question for context")
            last_question = get_last_question()
            debug(f"Last question detected: '{last_question}'")

            # Formulate query if there's previous context
            if last_question:
                try:
                    info("Formulating query based on previous context")
                    search_query = asyncio.run(
                        get_formulated_query(
                            previous_question=last_question,
                            current_quesion=search_query,
                        )
                    )
                    info(f"Formulated query: '{search_query}'")
                except Exception as e:
                    error(f"Error in get_formulated_query: {str(e)}")
                    warning("Using original search query due to formulation error")
            else:
                debug("No previous question found, using original query")

        except Exception as e:
            error(f"Error in query preparation phase: {str(e)}")
            # Continue with original query
            warning("Continuing with original search query")

        try:
            # First function call - detecting filters
            info("Starting Phase 1: Filter detection and market analysis")
            with st.spinner(
                "🔍 Detecting necessary filters and analyzing market signals..."
            ):
                try:
                    debug("Calling get_prospect_filters function")
                    (
                        businesses,
                        signals_description,
                        selected_signals,
                    ) = asyncio.run(get_prospect_filters(search_query))

                    info("get_prospect_filters completed successfully")
                    debug(
                        f"Results - businesses count: {len(businesses) if businesses else 0}"
                    )
                    debug(f"Results - signals_description: {signals_description}")
                    debug(
                        f"Results - selected_signals count: {len(selected_signals) if selected_signals else 0}"
                    )

                except Exception as e:
                    error(f"Error in get_prospect_filters: {str(e)}")
                    st.error("Failed to analyze market signals. Please try again.")
                    st.stop()

                try:
                    # Add to chat history
                    debug("Adding results to chat history")
                    add_to_chat_history(
                        HumanMessage(content=search_query),
                        AIMessage(content=json.dumps(selected_signals)),
                        search_query,
                    )
                    debug("Successfully added to chat history")
                except Exception as e:
                    error(f"Error adding to chat history: {str(e)}")
                    warning("Failed to save to chat history, continuing with search")

            try:
                st.success(
                    "✅ Market analysis complete! Found relevant business signals."
                )
                info("Phase 1 completed - Market analysis success message displayed")
            except Exception as e:
                error(f"Error displaying success message: {str(e)}")

        except Exception as e:
            error(f"Error in Phase 1 (filter detection): {str(e)}")
            st.error("Failed during market analysis phase. Please try again.")
            st.stop()

        try:
            # Second function call - getting prospects
            info("Starting Phase 2: Prospect matching")
            with st.spinner("🎯 Finding the best prospects based on your criteria..."):
                try:
                    debug("Calling get_main_prospects function")
                    final_output = asyncio.run(
                        get_main_prospects(
                            search_query,
                            signals_description,
                            selected_signals,
                            businesses,
                            PRODUCTS,
                        )
                    )

                    info("get_main_prospects completed successfully")
                    debug(
                        f"Final output count: {len(final_output) if final_output else 0}"
                    )

                    # Log the complete final output as JSON
                    debug_json(final_output, "FINAL_OUTPUT")

                except Exception as e:
                    error(f"Error in get_main_prospects: {str(e)}")
                    st.error("Failed to find prospects. Please try again.")
                    st.stop()

        except Exception as e:
            error(f"Error in Phase 2 (prospect matching): {str(e)}")
            st.error("Failed during prospect matching phase. Please try again.")
            st.stop()

        try:
            # Display results
            if final_output:
                info(f"Displaying {len(final_output)} prospects to user")
                st.success(f"🎉 Found {len(final_output)} high-quality prospects!")
                st.markdown("---")

                # Sort prospects by rank to ensure proper order
                sorted_prospects = sorted(
                    final_output, key=lambda x: x.get("rank", float("inf"))
                )

                # Display each prospect
                for prospect in sorted_prospects:
                    try:
                        rank = prospect.get("rank", "N/A")
                        debug(
                            f"Rendering prospect rank {rank}: {prospect.get('Company Name', 'Unknown')}"
                        )

                        # Create a container for each prospect with better structure
                        with st.container():
                            # Header section with company info
                            company_name = prospect.get(
                                "Company Name", "Unknown Company"
                            )
                            st.subheader(f"🏢 #{rank} - {company_name}")

                            # Basic info in columns
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.markdown(
                                    f"📍 **Location:** {prospect.get('City', 'N/A')}, {prospect.get('State', 'N/A')}"
                                )
                            with col2:
                                st.markdown(
                                    f"🏷️ **Category:** {prospect.get('Primary Category', 'N/A')}"
                                )
                            with col3:
                                if prospect.get("Website URL"):
                                    website_url = prospect["Website URL"]
                                    display_url = website_url.replace(
                                        "https://", ""
                                    ).replace("http://", "")
                                    st.markdown(
                                        f"🔗 [Visit Website](https://{display_url})"
                                    )
                                else:
                                    st.markdown("🔗 **Website:** Not Available")

                            st.markdown("")  # Add spacing

                            # Create tabs for better organization
                            tab1, tab2, tab3 = st.tabs(
                                ["🏆 Ranking", "📊 Analysis", "🎯 Product Strategy"]
                            )

                            with tab1:
                                if prospect.get("rank_reason"):
                                    st.markdown(
                                        "### Why this prospect ranks #{} 🥇".format(
                                            rank
                                        )
                                    )
                                    rank_reason = prospect.get(
                                        "rank_reason", "No ranking explanation provided"
                                    )
                                    st.info(rank_reason)
                                    debug(
                                        f"Prospect rank {rank} ranking reason displayed: {rank_reason[:50]}..."
                                    )
                                else:
                                    st.warning("No ranking explanation available")

                            with tab2:
                                st.markdown("### Detailed Business Analysis 📈")
                                reason = prospect.get(
                                    "Reason_selected", "No detailed analysis provided"
                                )
                                # Format the analysis text better
                                if reason:
                                    # Split by bullet points or dashes for better formatting
                                    if "- " in reason:
                                        analysis_points = reason.split("- ")
                                        st.markdown("**Key Analysis Points:**")
                                        for point in analysis_points[
                                            1:
                                        ]:  # Skip first empty item
                                            if point.strip():
                                                st.markdown(f"• {point.strip()}")
                                    else:
                                        st.markdown(reason)
                                else:
                                    st.warning("No detailed analysis available")
                                debug(
                                    f"Prospect rank {rank} detailed analysis displayed: {reason[:50]}..."
                                )

                            with tab3:
                                st.markdown(
                                    "### Recommended Products & Sales Strategy 💼"
                                )

                                if prospect.get("products_to_sell") or prospect.get(
                                    "reason_why_product_selected"
                                ):
                                    # Products section
                                    if prospect.get("products_to_sell"):
                                        products_to_sell = prospect.get(
                                            "products_to_sell", "No products specified"
                                        )
                                        st.markdown("#### 🛍️ **Recommended Products:**")

                                        # Split products by comma and display as badges
                                        if (
                                            isinstance(products_to_sell, str)
                                            and "," in products_to_sell
                                        ):
                                            products_list = [
                                                p.strip()
                                                for p in products_to_sell.split(",")
                                            ]
                                            product_cols = st.columns(
                                                len(products_list)
                                                if len(products_list) <= 3
                                                else 3
                                            )
                                            for i, product in enumerate(products_list):
                                                with product_cols[i % 3]:
                                                    st.success(f"✅ {product}")
                                        else:
                                            st.success(f"✅ {products_to_sell}")

                                        debug(
                                            f"Prospect rank {rank} products displayed: {products_to_sell}"
                                        )

                                    st.markdown("")  # Add spacing

                                    # Strategy reasoning section
                                    if prospect.get("reason_why_product_selected"):
                                        product_reason = prospect.get(
                                            "reason_why_product_selected",
                                            "No product reasoning provided",
                                        )
                                        st.markdown("#### 🎯 **Strategic Reasoning:**")

                                        # Format the reasoning better
                                        if "- " in product_reason:
                                            reason_points = product_reason.split("- ")
                                            for point in reason_points[
                                                1:
                                            ]:  # Skip first empty item
                                                if point.strip():
                                                    st.markdown(f"💡 {point.strip()}")
                                        else:
                                            st.info(product_reason)

                                        debug(
                                            f"Prospect rank {rank} product reasoning displayed: {product_reason[:50]}..."
                                        )
                                else:
                                    st.warning(
                                        "No product recommendations available for this prospect"
                                    )

                                # Add a call-to-action section
                                st.markdown("#### 📞 **Next Steps:**")
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    if prospect.get("Website URL"):
                                        website_url = prospect["Website URL"]
                                        display_url = website_url.replace(
                                            "https://", ""
                                        ).replace("http://", "")
                                        st.markdown(
                                            f"🔍 [Analyze Website](https://{display_url})"
                                        )
                                with col_b:
                                    st.markdown("📧 **Ready for outreach**")

                        # Add significant spacing between prospects
                        st.markdown("---")
                        st.markdown("")  # Extra spacing

                    except Exception as e:
                        error(
                            f"Error rendering prospect rank {prospect.get('rank', 'unknown')}: {str(e)}"
                        )
                        st.error("Error displaying prospect. Skipping to next.")
                        continue

                info("All prospects displayed successfully")

            else:
                warning("No prospects found for search query")
                st.warning(
                    "No prospects found matching your search criteria. Try refining your search query."
                )

        except Exception as e:
            error(f"Error in results display section: {str(e)}")
            st.error("Error occurred while displaying results.")

    else:
        warning("User submitted empty search query")
        st.warning("Please enter a search query to begin the prospect search.")

# Instructions section
try:
    st.markdown("---")
    st.subheader("ℹ️ How to Use")
    st.markdown("""
1. **Enter Search Query**: Describe the type of prospects you're looking for
   - Example: "companies which needs advertising help"
   - Example: "Companies which needs help related to social media services"
   - Example: "e-commerce businesses needing digital marketing help"

2. **Click Search**: The system will:
   - Analyze market signals and detect relevant filters
   - Find prospects matching your criteria with detailed reasoning
   - Recommend specific products and strategies for each prospect

3. **Review Results**: Each prospect includes:
   - Company name and website
   - Location and business category
   - Ranking explanation (why they rank where they do)
   - Detailed analysis of why they're a good fit
   - **Recommended products and strategic reasoning for outreach**
""")
    debug("Instructions section rendered successfully")
except Exception as e:
    error(f"Error rendering instructions section: {str(e)}")

info("Application fully loaded and ready for user interaction")
