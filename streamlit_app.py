"""
Streamlit Dashboard — deployable version of the News Scraper dashboard.
Run locally with: streamlit run streamlit_app.py
Or deploy for free at https://share.streamlit.io

NOTE: On free cloud hosting, the database resets whenever the app restarts/
redeploys (the filesystem isn't permanent). Use the "Scrape Now" button
below to fetch fresh articles whenever you (or a visitor) open the app.
"""

import pandas as pd
import streamlit as st

import database
import duplicates
import scraper

st.set_page_config(page_title="News Scraper Dashboard", page_icon="📰", layout="wide")
database.init_db()

# --- Custom styling ---
st.markdown("""
<style>
    .block-container { padding-top: 3.5rem; }
    .article-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 10px;
    }
    .article-card a { font-size: 17px; font-weight: 600; text-decoration: none; color: #1a1a2e; }
    .article-card a:hover { color: #2563eb; }
    .source-badge {
        display: inline-block;
        background: #eef2ff;
        color: #2563eb;
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 8px;
    }
    .meta-text { color: #6b7280; font-size: 12px; }
    .cluster-card {
        background: white;
        border-left: 4px solid #2563eb;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 14px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
</style>
""", unsafe_allow_html=True)

SOURCE_ICONS = {
    "BBC News": "🟥",
    "Dawn News": "🟩",
    "Al Jazeera": "🟨",
    "CNN": "🟦",
    "Geo News": "🟪",
}

# --- Sidebar controls ---
with st.sidebar:
    st.title("📰 News Scraper")
    st.caption("Multi-source scraper with analytics and related-story detection.")

    if st.button("🔄 Scrape Now", use_container_width=True, type="primary"):
        with st.spinner("Fetching latest articles from all sources..."):
            scraper.main()
        st.success("Done! Data refreshed below.")

    st.divider()
    keyword = st.text_input("🔍 Search headlines", placeholder="e.g. AI, cricket, elections...")
    all_sources = database.get_sources()
    source_filter = st.selectbox("Filter by source", ["All"] + all_sources)

    st.divider()
    st.caption("Built with Python, BeautifulSoup, SQLite & Streamlit")
    st.caption("[View source on GitHub](https://github.com/Hamid953-cloud/News-Scraper)")

# --- Top metrics row ---
# --- Top metrics row ---
total = database.count_articles()
source_counts = dict(database.get_source_counts())

metric_cols = st.columns(len(source_counts) + 1)
metric_cols[0].metric("Total Articles", total)
for i, (src, count) in enumerate(source_counts.items()):
    icon = SOURCE_ICONS.get(src, "📰")
    metric_cols[i + 1].metric(f"{icon} {src}", count)

st.markdown("")  # spacing

tab1, tab2, tab3 = st.tabs(["🗞️ Articles", "📊 Analytics", "🔗 Related Stories"])

# --- Tab 1: Article list ---
with tab1:
    source_arg = "" if source_filter == "All" else source_filter
    articles = database.search_articles(keyword=keyword, source=source_arg)
    st.caption(f"Showing {len(articles)} article(s)")

    if not articles:
        st.info("No articles found. Try 'Scrape Now' in the sidebar, or adjust your search/filter.")
    else:
        for a in articles[:100]:  # cap for performance
            icon = SOURCE_ICONS.get(a["source"], "📰")
            st.markdown(f"""
            <div class="article-card">
                <a href="{a['link']}" target="_blank">{a['title']}</a><br>
                <span class="source-badge">{icon} {a['source']}</span>
                <span class="meta-text">{a['date']}</span>
            </div>
            """, unsafe_allow_html=True)

# --- Tab 2: Analytics ---
with tab2:
    if total == 0:
        st.info("No data yet. Click 'Scrape Now' in the sidebar first.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Articles per Source")
            sc = database.get_source_counts()
            df1 = pd.DataFrame(sc, columns=["Source", "Count"]).set_index("Source")
            st.bar_chart(df1, color="#2563eb")

        with col2:
            st.subheader("Articles Scraped per Day (last 7 days)")
            dc = database.get_daily_counts(days=7)
            df2 = pd.DataFrame(dc, columns=["Date", "Count"]).set_index("Date")
            st.line_chart(df2, color="#2563eb")

# --- Tab 3: Related stories ---
with tab3:
    all_articles = database.get_all_articles()
    clusters = duplicates.find_related_stories(all_articles)
    st.caption(f"{len(clusters)} group(s) of related stories found (same event, multiple sources)")

    if not clusters:
        st.info("No related stories found yet. This grows as more sources cover the same events.")
    else:
        for cluster in clusters:
            sources_line = " ".join(f"{SOURCE_ICONS.get(a['source'], '📰')} {a['source']}" for a in cluster)
            rows = "".join(
                f'<div><a href="{a["link"]}" target="_blank">{a["title"]}</a> '
                f'<span class="source-badge">{SOURCE_ICONS.get(a["source"], "📰")} {a["source"]}</span></div><br>'
                for a in cluster
            )
            st.markdown(f"""
            <div class="cluster-card">
                <div class="meta-text" style="text-transform:uppercase; font-weight:700; color:#2563eb; margin-bottom:8px;">
                    {len(cluster)} sources covering this story
                </div>
                {rows}
            </div>
            """, unsafe_allow_html=True)