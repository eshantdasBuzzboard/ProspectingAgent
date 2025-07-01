import streamlit as st
import asyncio
from src.filters import get_prospect_filters, get_main_prospects, get_formulated_query
import json

from src.session import (
    initialize_chat_history,
    add_to_chat_history,
    get_last_question,
)

from src.utils.constants import PRODUCTS
from langchain_core.messages import HumanMessage, AIMessage

# Import the simple logger
from logger import info, debug, debug_json, error

info("Application startup initiated - Filter Agent")

try:
    st.set_page_config(page_title="Filter Agent", page_icon="🔍", layout="wide")
    debug("Page config set successfully")
except Exception as e:
    error(f"Failed to set page config: {str(e)}")
    st.error("Failed to initialize page configuration")

# Minimal CSS for professional styling
st.markdown(
    """
<style>
.prospect-card {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid #e9ecef;
    margin-bottom: 2rem;
}

.rank-badge {
    background-color: #007bff;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    font-weight: bold;
    display: inline-block;
    margin-bottom: 1rem;
}

.company-header {
    color: #2c3e50 !important;
    font-weight: 600;
    font-size: 1.5rem;
    margin-bottom: 1rem;
    border-bottom: 2px solid #e9ecef;
    padding-bottom: 0.5rem;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.info-item {
    padding: 0.75rem;
    background-color: #ffffff;
    border-radius: 4px;
    border: 1px solid #e9ecef;
    color: #2c3e50;
}

.info-item strong {
    color: #2c3e50;
}

.info-item br + * {
    color: #2c3e50;
}

.product-badge {
    background-color: #28a745;
    color: white;
    padding: 0.4rem 0.8rem;
    border-radius: 4px;
    font-size: 0.85rem;
    margin: 0.2rem 0.2rem 0.2rem 0;
    display: inline-block;
    font-weight: 500;
}

.website-link {
    color: #007bff;
    text-decoration: none;
}

.website-link:hover {
    text-decoration: underline;
}

.results-summary {
    background-color: #28a745;
    color: white;
    padding: 1.5rem;
    border-radius: 8px;
    margin: 1.5rem 0;
    text-align: center;
}

.content-section {
    margin-bottom: 1.5rem;
    padding: 1rem;
    background-color: #f8f9fa;
    border-radius: 4px;
    border-left: 4px solid #007bff;
}
</style>
""",
    unsafe_allow_html=True,
)

# Navigation
try:
    if st.button("← Back to Home"):
        info("User clicked Back to Home button")
        st.switch_page("main.py")
except Exception as e:
    error(f"Navigation button error: {str(e)}")

# Header Section
st.title("🔍 Filter Agent")
st.markdown("**AI-powered prospect discovery and analysis platform**")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("🎯 Available Products")
    st.markdown("*Your marketing solutions portfolio*")

    for i, (product_name, product_description) in enumerate(PRODUCTS.items(), 1):
        with st.expander(f"{i}. {product_name}", expanded=False):
            st.write(product_description)

    st.markdown("---")
    st.markdown("### 📊 Search Guidelines")
    st.info("""
    **Effective search examples:**
    • Companies requiring advertising assistance
    • Organizations needing social media management
    • E-commerce businesses seeking digital marketing solutions
    """)

# Main Search Interface
st.subheader("🔍 Prospect Discovery")
st.markdown("Enter your search criteria to identify high-potential prospects")

# Search input
search_query = st.text_area(
    "**Search Query**",
    placeholder="""Example searches:
• Companies requiring advertising assistance
• Organizations needing social media management
• E-commerce businesses seeking digital marketing solutions""",
    height=100,
    help="Describe the type of prospects you are looking for in detail",
)

# Search button
if st.button("🚀 Find Prospects", type="primary", use_container_width=True):
    info(f"Search button clicked with query: '{search_query}'")

    if search_query:
        # Initialize session
        try:
            initialize_chat_history()
            last_question = get_last_question()

            if last_question:
                search_query = asyncio.run(
                    get_formulated_query(
                        previous_question=last_question,
                        current_quesion=search_query,
                    )
                )
        except Exception as e:
            error(f"Session initialization error: {str(e)}")

        # Phase 1: Market Analysis
        try:
            with st.spinner(
                "🔍 **Phase 1:** Analyzing market signals and detecting filters..."
            ):
                (businesses, signals_description, selected_signals) = asyncio.run(
                    get_prospect_filters(search_query)
                )

                add_to_chat_history(
                    HumanMessage(content=search_query),
                    AIMessage(content=json.dumps(selected_signals)),
                    search_query,
                )

            st.success(
                "✅ **Phase 1 Complete:** Market analysis completed successfully"
            )

        except Exception as e:
            error(f"Phase 1 error: {str(e)}")
            st.error("❌ Market analysis failed. Please try again.")
            st.stop()

        # Phase 2: Prospect Matching
        try:
            with st.spinner("🎯 **Phase 2:** Finding and ranking prospects..."):
                final_output = asyncio.run(
                    get_main_prospects(
                        search_query,
                        signals_description,
                        selected_signals,
                        businesses,
                        PRODUCTS,
                    )
                )
                debug_json(final_output, "FINAL_OUTPUT")

            st.success("✅ **Phase 2 Complete:** Prospect matching completed")

        except Exception as e:
            error(f"Phase 2 error: {str(e)}")
            st.error("❌ Prospect matching failed. Please try again.")
            st.stop()

        # Results Display
        if final_output:
            st.markdown("---")

            # Results summary
            st.markdown(
                f"""
                <div class="results-summary">
                    <h3>🎉 Discovery Complete</h3>
                    <p>Found {len(final_output)} qualified prospects ranked by potential value</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Sort prospects by rank
            sorted_prospects = sorted(
                final_output, key=lambda x: x.get("rank", float("inf"))
            )

            # Display prospects
            for i, prospect in enumerate(sorted_prospects):
                rank = prospect.get("rank", "N/A")
                company_name = prospect.get("Company Name", "Unknown Company")

                # Prospect Card Container
                st.markdown(
                    f"""
                    <div class="prospect-card">
                        <div class="rank-badge">Rank #{rank}</div>
                        <h2 class="company-header">{company_name}</h2>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Company Information Grid
                st.markdown('<div class="info-grid">', unsafe_allow_html=True)

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.markdown(
                        f"""
                        <div class="info-item">
                            <strong>📍 Location</strong><br>
                            {prospect.get("City", "N/A")}, {prospect.get("State", "N/A")}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with col2:
                    st.markdown(
                        f"""
                        <div class="info-item">
                            <strong>🏢 Category</strong><br>
                            {prospect.get("Primary Category", "N/A")}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with col3:
                    website = prospect.get("Website URL", "")
                    if website:
                        clean_url = website.replace("https://", "").replace(
                            "http://", ""
                        )
                        website_display = f'<a href="https://{clean_url}" target="_blank" class="website-link">{clean_url}</a>'
                    else:
                        website_display = "Not available"

                    st.markdown(
                        f"""
                        <div class="info-item">
                            <strong>🌐 Website</strong><br>
                            {website_display}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with col4:
                    st.markdown(
                        f"""
                        <div class="info-item">
                            <strong>⭐ Rank Score</strong><br>
                            #{rank} of {len(final_output)}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown("</div>", unsafe_allow_html=True)

                # Spacing before tabs
                st.markdown("<br>", unsafe_allow_html=True)

                # Tabbed Content
                tab1, tab2, tab3 = st.tabs(
                    ["🏆 Ranking Analysis", "📊 Business Profile", "🎯 Sales Strategy"]
                )

                with tab1:
                    st.markdown('<div class="content-section">', unsafe_allow_html=True)
                    st.markdown(f"### Ranking Analysis - Position #{rank}")
                    rank_reason = prospect.get(
                        "rank_reason", "No ranking explanation provided"
                    )
                    st.info(rank_reason)
                    st.markdown("</div>", unsafe_allow_html=True)

                with tab2:
                    st.markdown('<div class="content-section">', unsafe_allow_html=True)
                    st.markdown("### Business Profile Analysis")
                    reason = prospect.get(
                        "Reason_selected", "No detailed analysis provided"
                    )

                    if "###" in reason:
                        # Parse structured content
                        sections = reason.split("###")
                        for section in sections[1:]:  # Skip first empty section
                            if section.strip():
                                lines = section.strip().split("\n")
                                section_title = lines[0].strip()
                                section_content = "\n".join(lines[1:]).strip()

                                st.markdown(f"**{section_title}**")
                                if section_content:
                                    st.markdown(section_content)
                                st.markdown("")
                    else:
                        st.markdown(reason)
                    st.markdown("</div>", unsafe_allow_html=True)

                with tab3:
                    st.markdown('<div class="content-section">', unsafe_allow_html=True)
                    st.markdown("### Recommended Sales Strategy")

                    # Products section
                    products_to_sell = prospect.get("products_to_sell", "")
                    if products_to_sell:
                        st.markdown("**🛍️ Recommended Products:**")

                        if (
                            isinstance(products_to_sell, str)
                            and "," in products_to_sell
                        ):
                            products_list = [
                                p.strip() for p in products_to_sell.split(",")
                            ]
                            product_html = "<div style='margin: 1rem 0;'>"
                            for product in products_list:
                                product_html += (
                                    f'<span class="product-badge">{product}</span>'
                                )
                            product_html += "</div>"
                            st.markdown(product_html, unsafe_allow_html=True)
                        else:
                            st.markdown(
                                f'<div style="margin: 1rem 0;"><span class="product-badge">{products_to_sell}</span></div>',
                                unsafe_allow_html=True,
                            )

                    # Strategy reasoning
                    product_reason = prospect.get("reason_why_product_selected", "")
                    if product_reason:
                        st.markdown("**🎯 Strategic Rationale:**")
                        st.markdown(product_reason)

                    # Call to action
                    st.markdown("---")
                    st.markdown("**📞 Next Steps:**")

                    action_col1, action_col2 = st.columns(2)
                    with action_col1:
                        if prospect.get("Website URL"):
                            website_url = prospect["Website URL"]
                            clean_url = website_url.replace("https://", "").replace(
                                "http://", ""
                            )
                            st.link_button("🔍 Analyze Website", f"https://{clean_url}")

                    with action_col2:
                        st.markdown("📧 **Ready for outreach**")

                    st.markdown("</div>", unsafe_allow_html=True)

                # Separator between prospects
                if i < len(sorted_prospects) - 1:
                    st.markdown("---")
                    st.markdown("<br>", unsafe_allow_html=True)

        else:
            st.warning(
                "🔍 No prospects found matching your criteria. Please refine your search query."
            )

    else:
        st.warning("⚠️ Please enter a search query to begin the prospect search.")

# Instructions Section
st.markdown("---")
st.subheader("📖 User Guide")

instructions_col1, instructions_col2 = st.columns(2)

with instructions_col1:
    st.markdown("""
    #### 🔍 **Search Process**
    1. **Enter Query**: Describe your target prospects
    2. **AI Analysis**: System analyzes market signals
    3. **Prospect Matching**: Identifies best-fit companies
    4. **Results Review**: Examine ranked prospects
    """)

with instructions_col2:
    st.markdown("""
    #### 📊 **Deliverables**
    • **Ranked prospects** with detailed analysis
    • **Business intelligence** and market signals
    • **Product recommendations** for each prospect
    • **Strategic approach** for engagement
    """)

st.markdown("""
#### 💡 **Best Practices**
- Specify industry, location, or business characteristics
- Include pain points or challenges you address
- Use descriptive language for your ideal customer profile
""")

info("Application fully loaded and ready for user interaction")
