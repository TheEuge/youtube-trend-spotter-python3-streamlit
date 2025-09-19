from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import aiohttp
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime
import json
from pathlib import Path

# Initialize FastAPI app
app = FastAPI()

# Load environment variables
load_dotenv()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load API key from environment variable
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("Error: API_KEY is not set in .env file")

# Set up data directory
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.json()

@app.get("/api/compare")
async def compare(term1: str, term2: str):
    if not term1 or not term2:
        raise HTTPException(status_code=400, detail="Both term1 and term2 are required")

    try:
        async with aiohttp.ClientSession() as session:
            # Single search().list call for each term
            search_url1 = f"https://www.googleapis.com/youtube/v3/search?part=id,snippet&q={term1}&type=video&maxResults=50&order=relevance&key={API_KEY}"
            search_url2 = f"https://www.googleapis.com/youtube/v3/search?part=id,snippet&q={term2}&type=video&maxResults=50&order=relevance&key={API_KEY}"

            response1, response2 = await asyncio.gather(
                fetch_url(session, search_url1),
                fetch_url(session, search_url2)
            )

            # Check for API errors
            if "error" in response1 or "error" in response2:
                error_message = response1.get("error", {}).get("message") or response2.get("error", {}).get("message") or "YouTube API error"
                raise Exception(error_message)

            # Extract totalResults and video IDs
            total_results1 = response1["pageInfo"]["totalResults"]
            total_results2 = response2["pageInfo"]["totalResults"]
            video_ids1 = ",".join(item["id"]["videoId"] for item in response1["items"])
            video_ids2 = ",".join(item["id"]["videoId"] for item in response2["items"])

            # Single videos().list call for each term
            video_url1 = f"https://www.googleapis.com/youtube/v3/videos?part=statistics,snippet&id={video_ids1}&key={API_KEY}"
            video_url2 = f"https://www.googleapis.com/youtube/v3/videos?part=statistics,snippet&id={video_ids2}&key={API_KEY}"

            video_response1, video_response2 = await asyncio.gather(
                fetch_url(session, video_url1),
                fetch_url(session, video_url2)
            )

            # Check for API errors
            if "error" in video_response1 or "error" in video_response2:
                error_message = video_response1.get("error", {}).get("message") or video_response2.get("error", {}).get("message") or "YouTube API error"
                raise Exception(error_message)

            # Process stats for term1
            stats1 = {
                "totalResults": total_results1,
                "totalViews": 0,
                "averageViews": 0.0,
                "totalLikes": 0,
                "averageLikes": 0.0,
                "videos": [
                    {
                        "videoId": item["id"],
                        "title": item["snippet"]["title"],
                        "viewCount": int(item["statistics"].get("viewCount", 0)),
                        "likeCount": int(item["statistics"].get("likeCount", 0)),
                        "publishedAt": item["snippet"]["publishedAt"]
                    } for item in video_response1["items"]
                ]
            }
            video_count1 = len(stats1["videos"])
            if video_count1 > 0:
                stats1["totalViews"] = sum(video["viewCount"] for video in stats1["videos"])
                stats1["averageViews"] = stats1["totalViews"] / video_count1
                stats1["totalLikes"] = sum(video["likeCount"] for video in stats1["videos"])
                stats1["averageLikes"] = stats1["totalLikes"] / video_count1

            # Process stats for term2
            stats2 = {
                "totalResults": total_results2,
                "totalViews": 0,
                "averageViews": 0.0,
                "totalLikes": 0,
                "averageLikes": 0.0,
                "videos": [
                    {
                        "videoId": item["id"],
                        "title": item["snippet"]["title"],
                        "viewCount": int(item["statistics"].get("viewCount", 0)),
                        "likeCount": int(item["statistics"].get("likeCount", 0)),
                        "publishedAt": item["snippet"]["publishedAt"]
                    } for item in video_response2["items"]
                ]
            }
            video_count2 = len(stats2["videos"])
            if video_count2 > 0:
                stats2["totalViews"] = sum(video["viewCount"] for video in stats2["videos"])
                stats2["averageViews"] = stats2["totalViews"] / video_count2
                stats2["totalLikes"] = sum(video["likeCount"] for video in stats2["videos"])
                stats2["averageLikes"] = stats2["totalLikes"] / video_count2

            return {
                "term1": term1,
                "term2": term2,
                "stats1": stats1,
                "stats2": stats2
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"YouTube API error: {str(e)}")

@app.post("/api/save-json")
async def save_json(data: dict):
    try:
        timestamp = datetime.now().isoformat().replace(":", "-").replace(".", "-")
        filename = f"comparison-{timestamp}.json"
        file_path = DATA_DIR / filename
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        return {"filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save JSON: {str(e)}")

@app.get("/api/load-json/{filename}")
async def load_json(filename: str):
    try:
        file_path = DATA_DIR / filename
        with open(file_path, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load JSON: {str(e)}")

@app.get("/api/list-json")
async def list_json():
    try:
        files = [f.name for f in DATA_DIR.glob("*.json")]
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list JSON files: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=3000)