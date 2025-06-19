import streamlit as st
import asyncio


from typing import Any


async def main() -> Any:
    st.set_page_config(page_title="AI Agent Hub", page_icon="🤖", layout="wide")

    st.title("🤖 AI Agent Hub")
    st.markdown("Choose your AI agent to get started:")

    # Create two columns for the agent options
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🧠 Intelligence Agent")
        st.markdown("Advanced AI capabilities for complex tasks")
        if st.button(
            "Launch Intelligence Agent", key="intel_agent", use_container_width=True
        ):
            st.switch_page("pages/intelligence_agent.py")

    with col2:
        st.markdown("### 🔍 Filter Agent")
        st.markdown("Specialized filtering and data processing")
        if st.button(
            "Launch Filter Agent", key="filter_agent", use_container_width=True
        ):
            st.switch_page("pages/filter_agent.py")


if __name__ == "__main__":
    asyncio.run(main())
