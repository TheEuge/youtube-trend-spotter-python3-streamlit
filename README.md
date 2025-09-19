# YouTube Trend Spotter Python

YouTube Trend Spotter Python is a Python3-based web application that allows users to compare two YouTube search terms by analyzing video statistics (total results, views, likes) and visualizing the data through interactive charts. The application retrieves the top 50 most relevant videos for each search term using the YouTube Data API, displays them in sortable tables with clickable links, and supports saving and loading comparison results as JSON files.

## Project Structure

- `main.py`: FastAPI backend to handle API requests, fetch data from the YouTube Data API, and manage JSON file operations.
- `frontend.py`: Streamlit frontend for user interaction, data visualization, and displaying video tables.
- `requirements.txt`: Python dependencies for the project.
- `.env`: Environment file for storing the YouTube API key.
- `README.md`: Project documentation (this file).

```bash
youtube-trend-spotter-python3-streamlit/
├── data/                       # Directory for saved JSON files
├── .env                        # Environment variables (API key)
├── main.py                     # FastAPI backend
├── frontend.py                 # Streamlit frontend
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

## Prerequisites

- Python 3.12
- A valid YouTube Data API key from the [Google Cloud Console](https://console.cloud.google.com/).
- A virtual environment for dependency management.
- Internet connection for API requests and running the application.

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/TheEuge/youtube-trend-spotter-python3-streamlit
   cd youtube-trend-spotter-python3-streamlit

2. **Set Up a Virtual Environment**

```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install Dependencies**

Install the required Python packages from requirements.txt:bash

```bash
pip install -r requirements.txt
```
```bash
fastapi==0.115.0
uvicorn==0.30.6
aiohttp==3.10.5
python-dotenv==1.0.1
streamlit==1.39.0
requests==2.32.3
pandas==2.2.3
plotly==5.24.1
```
4. **Configure the YouTube API Key**
Create a .env file in the project root and add your YouTube Data API key:

```bash
API_KEY=your_youtube_api_key_here
```

5. **Run the Backend**
Start the FastAPI backend in one terminal:

```bash
python3 main.py
```

The backend runs on http://localhost:3000.

6. **Run the Frontend**
In another terminal (within the same virtual environment):

```bash
streamlit run frontend.py
```
The frontend runs on http://localhost:8501.

7. **Access the Application**
**Backend API**: http://localhost:3000
**Frontend Interface**: Open http://localhost:8501 in a web browser.

# Usage

## Enter Search Terms
**Input two search terms** (e.g., "python tutorial" and "javascript tutorial") in the provided text fields.
**Click the "Compare" button** to fetch and analyze data from the YouTube Data API.

## View Results
**Visualizations**: 
- Interactive charts display:Total number of videos (bar chart).
- Total and average views/likes (grouped bar charts).
- Release dates vs. view counts (scatter plot).

**Video Tables**:
- Up to 50 most relevant videos per term are shown in tables with:Clickable title links to YouTube (https://youtu.be/{videoId}).
- Columns for Title, Views, Likes, and Published At, sortable by clicking headers.
- Pagination (10 videos per page) for better readability.

## **Save** and **Load** Comparisons
- Click "Save Results as JSON" to save the comparison data to a JSON file.
- Use the "Saved Comparisons" dropdown to load and visualize previously saved comparisons.

## Notes

**API Quota**: Each comparison consumes approximately 202 YouTube API quota units (100 per search().list × 2 + 1 per videos().list × 2). Ensure sufficient quota in the Google Cloud Console.

**Video Count**: The application retrieves up to 50 videos per term, but fewer may be returned depending on the search term and API response.

**Sorting**: Click column headers in the video tables to sort by Title (alphabetically), Views (numerically), Likes (numerically), or Published At (chronologically). Click again to toggle between ascending and descending order.

**Sample Datasets**
Sample JSON files are provided in the `data/` directory for testing and demonstration purposes.

## License

This project is licensed under the MIT License.

