import streamlit as st
import asyncio

from src.intelligence import get_propsects
from logger import debug_json


st.set_page_config(page_title="Prospect Intelligence", page_icon="🎯", layout="wide")

# Navigation
if st.button("← Back to Home"):
    st.switch_page("main.py")

st.title("🎯 Prospect Intelligence")
st.markdown("---")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    st.markdown("Configure your prospect search parameters")

# Prefilled products data
PRODUCTS = {
    "Outreach Display": "Sinclair's Outreach Display revolutionizes advertising with their extensive broadcast reach. It helps businesses connect with consumers efficiently through captivating news, entertainment, and sports content.",
    "Social Marketing": "Sinclair's Social Marketing employs its expertise in broadcasting to develop powerful social media campaigns. We utilize captivating content to engage customers effectively and improve brand visibility.",
    "YouTube Marketing": "Sinclair's YouTube Marketing service uses their broadcast influence to make effective video campaigns that promote brands well. They use their expertise in engaging news, entertainment, and sports content to maximize brand exposure and reach more people through targeted YouTube ads.",
    "Owned and Operated Display and Video": "Sinclair's Owned and Operated Display and Video services offer unparalleled control over advertising strategies. With a focus on leveraging owned media, they deliver compelling visual promotions on diverse third-party platforms, coupled with engaging video content marketing. Engage audiences effectively and drive brand recognition through tailored, dynamic advertising solutions.",
    "Branded Content": "Sinclair's Branded Content service helps businesses build strong and trusted relationships with their target audience by creating compelling and personalized stories that are seamlessly integrated with Sinclair's engaging news, entertainment, and sports content.",
}

# Main interface
st.subheader("🔍 Prospect Search Parameters")

# Create three columns for inputs
col1, col2 = st.columns(2)

with col1:
    default_location = st.text_input(
        "Default Location (State)",
        placeholder="e.g., Texas, California, Florida",
        help="Enter the state where you want to search for prospects",
    )

with col2:
    default_category = st.text_input(
        "Default Category",
        placeholder="e.g., Automotive, Healthcare, Retail",
        help="Enter the business category to filter prospects",
    )

# Display available products
st.subheader("📦 Available Products")
st.markdown("**Sinclair's Marketing Solutions:**")

for i, (name, desc) in enumerate(PRODUCTS.items(), 1):
    with st.expander(f"{i}. {name}", expanded=True):
        st.markdown(desc)

# Search button
if st.button("🔍 Find Prospects", type="primary", use_container_width=True):
    if default_location and default_category:
        with st.spinner("Analyzing prospects..."):
            try:
                # Call your async function with prefilled products
                results = asyncio.run(
                    get_propsects(default_location, default_category, PRODUCTS)
                )
                debug_json(results, "NEW Intelligence results")
                if results:
                    st.success(
                        f"Found {len(results)} potential prospects using {len(PRODUCTS)} products!"
                    )
                    st.markdown("---")

                    # Sort results by rank before displaying
                    sorted_results = sorted(
                        results, key=lambda x: x.get("rank", float("inf"))
                    )

                    # Display results - Updated to handle new format
                    for prospect in sorted_results:
                        # Handle both old and new field name formats
                        company_name = prospect.get("Company Name") or prospect.get(
                            "Company_name", "Unknown Company"
                        )
                        rank = prospect.get("rank", "N/A")
                        rank_reason = prospect.get(
                            "rank_reason", "No ranking reason provided"
                        )
                        reason_selected = prospect.get(
                            "Reason_selected", "No detailed reason provided"
                        )

                        # New fields for location and website
                        website_url = prospect.get("Website URL", "")
                        city = prospect.get("City", "")
                        state = prospect.get("State", "")
                        primary_category = prospect.get("Primary Category", "")

                        # Company name as heading with rank
                        st.subheader(f"#{rank}. {company_name}")

                        # Create columns for company info
                        info_col1, info_col2, info_col3 = st.columns(3)

                        with info_col1:
                            if website_url:
                                st.markdown(
                                    f"🌐 **Website:** [{website_url}](https://{website_url})"
                                )

                        with info_col2:
                            if city and state:
                                st.markdown(f"📍 **Location:** {city}, {state}")
                            elif state:
                                st.markdown(f"📍 **State:** {state}")

                        with info_col3:
                            if primary_category:
                                st.markdown(f"🏢 **Category:** {primary_category}")

                        # Rank reason in a highlighted box
                        st.info(f"**Ranking Reason:** {rank_reason}")

                        # Reason selected as markdown
                        st.markdown(reason_selected)

                        # Add some spacing between prospects
                        if rank < len(sorted_results):
                            st.markdown("---")
                else:
                    st.warning("No prospects found matching your criteria.")

            except Exception as e:
                st.error(f"An error occurred while searching for prospects: {str(e)}")
                st.error(f"Error details: {type(e).__name__}")
    else:
        missing_fields = []
        if not default_location:
            missing_fields.append("Default Location")
        if not default_category:
            missing_fields.append("Default Category")

        st.warning(f"Please provide: {', '.join(missing_fields)}")

# Instructions
st.markdown("---")
st.subheader("ℹ️ How to Use")
st.markdown("""
1. **Enter Location**: Specify the state where you want to find prospects
2. **Enter Category**: Specify the business category to target
3. **Review Products**: All Sinclair marketing products are automatically included in the search
4. **Click Find Prospects**: The system will analyze potential customers using all configured products
5. **Review Results**: Each prospect will be displayed with their company name, location, website, and detailed reasoning for selection
""")
