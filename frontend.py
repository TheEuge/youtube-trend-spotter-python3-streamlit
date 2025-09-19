import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import streamlit.components.v1 as components

# FastAPI backend URL
BASE_URL = "http://localhost:3000"

st.set_page_config(page_title="YouTube Search Trend Spotter", layout="wide")
st.title("YouTube Search Trend Spotter")

# Function to display visualizations
def display_visualizations(data, title_prefix="Comparison"):
    term1, term2 = data["term1"], data["term2"]
    st.subheader(f"{title_prefix}: '{term1}' vs '{term2}'")

    # Prepare data for bar charts
    metrics_df = pd.DataFrame([
        {
            "Term": term1,
            "Total Results": data["stats1"]["totalResults"],
            "Total Views": data["stats1"]["totalViews"],
            "Average Views": data["stats1"]["averageViews"],
            "Total Likes": data["stats1"]["totalLikes"],
            "Average Likes": data["stats1"]["averageLikes"]
        },
        {
            "Term": term2,
            "Total Results": data["stats2"]["totalResults"],
            "Total Views": data["stats2"]["totalViews"],
            "Average Views": data["stats2"]["averageViews"],
            "Total Likes": data["stats2"]["totalLikes"],
            "Average Likes": data["stats2"]["averageLikes"]
        }
    ])

    # Bar chart for Total Results
    fig_results = px.bar(
        metrics_df,
        x="Term",
        y="Total Results",
        title="Total Number of Videos",
        labels={"Total Results": "Total Videos"},
        color="Term",
        barmode="group"
    )
    st.plotly_chart(fig_results, use_container_width=True)

    # Bar chart for Total and Average Views
    fig_views = go.Figure()
    fig_views.add_trace(go.Bar(
        x=metrics_df["Term"],
        y=metrics_df["Total Views"],
        name="Total Views",
        marker_color="blue"
    ))
    fig_views.add_trace(go.Bar(
        x=metrics_df["Term"],
        y=metrics_df["Average Views"],
        name="Average Views",
        marker_color="lightblue"
    ))
    fig_views.update_layout(
        title="Total and Average Views Comparison",
        barmode="group",
        yaxis_title="Views"
    )
    st.plotly_chart(fig_views, use_container_width=True)

    # Bar chart for Total and Average Likes
    fig_likes = go.Figure()
    fig_likes.add_trace(go.Bar(
        x=metrics_df["Term"],
        y=metrics_df["Total Likes"],
        name="Total Likes",
        marker_color="green"
    ))
    fig_likes.add_trace(go.Bar(
        x=metrics_df["Term"],
        y=metrics_df["Average Likes"],
        name="Average Likes",
        marker_color="lightgreen"
    ))
    fig_likes.update_layout(
        title="Total and Average Likes Comparison",
        barmode="group",
        yaxis_title="Likes"
    )
    st.plotly_chart(fig_likes, use_container_width=True)

    # Time-based scatter plot for release dates vs view counts
    df1 = pd.DataFrame(data["stats1"]["videos"])
    df1["Term"] = term1
    df2 = pd.DataFrame(data["stats2"]["videos"])
    df2["Term"] = term2
    combined_df = pd.concat([df1, df2])
    combined_df["publishedAt"] = pd.to_datetime(combined_df["publishedAt"])

    fig_time = px.scatter(
        combined_df,
        x="publishedAt",
        y="viewCount",
        color="Term",
        hover_data=["title"],
        title="Video Release Dates vs. View Counts",
        labels={"publishedAt": "Release Date", "viewCount": "View Count"}
    )
    st.plotly_chart(fig_time, use_container_width=True)

    # Display all 50 most relevant videos in tables with sortable columns
    st.subheader("Top 50 Most Relevant Videos")
    st.write(f"Showing up to 50 most relevant videos for each search term (retrieved via YouTube API with order=relevance, maxResults=50). Click column headers to sort.")

    # Helper function to create HTML table with pagination and sorting
    def create_html_table(df, page=1, per_page=10, table_id="table"):
        if df.empty:
            return "<p>No videos available.</p>"
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        df_page = df[start_idx:end_idx]
        html = f"""
        <style>
            #{table_id} {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
            #{table_id} th, #{table_id} td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            #{table_id} th {{ background-color: #f2f2f2; font-weight: bold; cursor: pointer; }}
            #{table_id} a {{ color: #1a0dab; text-decoration: none; }}
            #{table_id} a:hover {{ text-decoration: underline; }}
            #{table_id} .title-column {{ max-width: 300px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        </style>
        <table id="{table_id}">
            <tr>
                <th class="title-column" onclick="sortTable(0, '{table_id}')">Title</th>
                <th onclick="sortTable(1, '{table_id}')">Views</th>
                <th onclick="sortTable(2, '{table_id}')">Likes</th>
                <th onclick="sortTable(3, '{table_id}')">Published At</th>
            </tr>
        """
        for _, row in df_page.iterrows():
            title = row["title"].replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
            html += f"""
            <tr>
                <td class="title-column"><a href="https://youtu.be/{row['videoId']}" target="_blank">{title}</a></td>
                <td data-value="{row['viewCount']}">{row['viewCount']:,}</td>
                <td data-value="{row['likeCount']}">{row['likeCount']:,}</td>
                <td data-value="{row['publishedAt']}">{pd.to_datetime(row['publishedAt']).strftime('%Y-%m-%d')}</td>
            </tr>
            """
        html += "</table>"
        html += """
        <script>
            function sortTable(n, tableId) {
                var table, rows, switching = true, i, x, y, shouldSwitch, dir = "asc", switchcount = 0;
                table = document.getElementById(tableId);
                while (switching) {
                    switching = false;
                    rows = table.rows;
                    for (i = 1; i < (rows.length - 1); i++) {
                        shouldSwitch = false;
                        x = rows[i].getElementsByTagName("TD")[n];
                        y = rows[i + 1].getElementsByTagName("TD")[n];
                        var xValue = x.getAttribute("data-value") || x.innerText;
                        var yValue = y.getAttribute("data-value") || y.innerText;
                        if (n === 0) { // Title (string)
                            xValue = xValue.toLowerCase();
                            yValue = yValue.toLowerCase();
                        } else if (n === 3) { // Published At (date)
                            xValue = new Date(xValue);
                            yValue = new Date(yValue);
                        } else { // Views, Likes (number)
                            xValue = parseFloat(xValue.replace(/,/g, '')) || 0;
                            yValue = parseFloat(yValue.replace(/,/g, '')) || 0;
                        }
                        if (dir == "asc") {
                            if (xValue > yValue) {
                                shouldSwitch = true;
                                break;
                            }
                        } else if (dir == "desc") {
                            if (xValue < yValue) {
                                shouldSwitch = true;
                                break;
                            }
                        }
                    }
                    if (shouldSwitch) {
                        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                        switching = true;
                        switchcount++;
                    } else if (switchcount == 0 && dir == "asc") {
                        dir = "desc";
                        switching = true;
                    }
                }
            }
        </script>
        """
        return html

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**{term1} ({len(df1)} videos)**")
        df1_display = df1[["videoId", "title", "viewCount", "likeCount", "publishedAt"]]
        # Pagination for term1
        page1 = st.number_input(f"Page for {term1}", min_value=1, max_value=(len(df1) + 9) // 10, value=1, step=1, key=f"page_{term1}")
        components.html(create_html_table(df1_display, page=page1, table_id=f"table_{term1.replace(' ', '_')}"), height=400, scrolling=True)

    with col2:
        st.write(f"**{term2} ({len(df2)} videos)**")
        df2_display = df2[["videoId", "title", "viewCount", "likeCount", "publishedAt"]]
        # Pagination for term2
        page2 = st.number_input(f"Page for {term2}", min_value=1, max_value=(len(df2) + 9) // 10, value=1, step=1, key=f"page_{term2}")
        components.html(create_html_table(df2_display, page=page2, table_id=f"table_{term2.replace(' ', '_')}"), height=400, scrolling=True)

# Input fields for search terms
st.subheader("Compare New Search Terms")
col1, col2 = st.columns(2)
with col1:
    term1 = st.text_input("First search term", value="cat videos")
with col2:
    term2 = st.text_input("Second search term", value="dog videos")

# Button to trigger comparison
if st.button("Compare", key="compare"):
    if term1 and term2:
        with st.spinner("Fetching data from YouTube API..."):
            try:
                # Call the /api/compare endpoint
                response = requests.get(f"{BASE_URL}/api/compare", params={"term1": term1, "term2": term2})
                response.raise_for_status()
                data = response.json()

                # Store results in session state for saving
                st.session_state["last_results"] = data

                # Display visualizations
                display_visualizations(data)

            except requests.exceptions.RequestException as e:
                st.error(f"Error: {str(e)}")
    else:
        st.error("Please enter both search terms.")

# Save results section
if "last_results" in st.session_state and st.button("Save Results as JSON", key="save"):
    try:
        save_response = requests.post(f"{BASE_URL}/api/save-json", json=st.session_state["last_results"])
        save_response.raise_for_status()
        filename = save_response.json()["filename"]
        st.success(f"Results saved as {filename}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error saving results: {str(e)}")

# Load and visualize saved comparisons
st.subheader("Saved Comparisons")
try:
    list_response = requests.get(f"{BASE_URL}/api/list-json")
    list_response.raise_for_status()
    files = list_response.json()
    if files:
        selected_file = st.selectbox("Select a saved file to view", [""] + files, key="file_select")
        if selected_file:
            with st.spinner("Loading saved data..."):
                try:
                    load_response = requests.get(f"{BASE_URL}/api/load-json/{selected_file}")
                    load_response.raise_for_status()
                    loaded_data = load_response.json()
                    # Display visualizations for loaded data
                    display_visualizations(loaded_data, title_prefix=f"Loaded Comparison ({selected_file})")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error loading file: {str(e)}")
    else:
        st.write("No saved comparisons found.")
except requests.exceptions.RequestException as e:
    st.error(f"Error listing files: {str(e)}")

if __name__ == "__main__":
    st.write("Run this app with: streamlit run frontend.py")