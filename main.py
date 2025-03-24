from bs4 import BeautifulSoup
import json
from datetime import timedelta, datetime
import re
from collections import defaultdict


# Function to read HTML content from a file
def read_html_file(path):
    with open(path, 'r') as file:
        return file.read()

# Path to the HTML file
html_file_path = 'video-library.html'

# Read the HTML content from the file
html = read_html_file(html_file_path)

# Parse the HTML
soup = BeautifulSoup(html, 'html.parser')

# Use a CSS selector that matches div elements having all these classes.
video_containers = soup.select("div.group.relative.flex.cursor-pointer.flex-col.overflow-hidden.rounded-xl")

videos_info = []
for container in video_containers:
    video_data = {}
    
    # Extract the URL path from the anchor tag
    a_tag = container.find("a", href=True)
    video_data["url"] = a_tag["href"] if a_tag else None
    
    # Extract the video ID from the URL
    if video_data["url"]:
        match = re.search(r'/watch/(\d+)', video_data["url"])
        if match:
            video_data["id"] = match.group(1)
    
    # Extract the duration
    duration_tag = container.find("div", class_=lambda x: x and "group-hover:hidden" in x)
    video_data["duration"] = duration_tag.get_text(strip=True) if duration_tag else None
    
    # Extract the thumbnail image
    img_tag = container.find("img", alt="video-thumbnail")
    video_data["thumbnail"] = img_tag["src"] if img_tag else None

    # Extract the video
    video_data["video_asset"] = video_data["thumbnail"].replace("thumbnails", "recall").replace(".0000000.jpg", ".mp4")
    
    # Extract the title
    title_tag = container.find("h3")
    video_data["title"] = title_tag.get_text(strip=True) if title_tag else None
    
    # Extract the recorder/author
    author_span = container.find("span", class_="max-w-24")
    video_data["recorder"] = author_span.get_text(strip=True) if author_span else None
    
    # Extract the date
    blockquote = container.find("blockquote")
    if blockquote:
        date_text = blockquote.get_text(strip=True)
        # Extract date (typically at the end after a dot)
        date_match = re.search(r'\.(.+)$', date_text)
        if date_match:
            video_data["date"] = date_match.group(1).strip()
    
    # Extract avatar image
    avatar_img = container.find("img", alt="@video-user-avatar")
    video_data["avatar_url"] = avatar_img["src"] if avatar_img else None
    
    videos_info.append(video_data)

# Calculate total duration in seconds
def parse_duration(duration_str):
    """
    Convert a duration string into total seconds.
    Duration may be in MM:SS or HH:MM:SS format.
    """
    if not duration_str:
        return 0
        
    parts = duration_str.split(':')
    parts = [int(p) for p in parts]
    if len(parts) == 2:
        minutes, seconds = parts
        return minutes * 60 + seconds
    elif len(parts) == 3:
        hours, minutes, seconds = parts
        return hours * 3600 + minutes * 60 + seconds
    else:
        return 0

# Calculate total duration
total_seconds = sum(parse_duration(video.get("duration")) for video in videos_info)
hours = total_seconds // 3600
minutes = (total_seconds % 3600) // 60
seconds = total_seconds % 60
total_duration_formatted = f"{hours:02}:{minutes:02}:{seconds:02}"

# Create summary statistics
summary = {
    "total_videos": len(videos_info),
    "total_duration": total_duration_formatted,
    "total_duration_seconds": total_seconds,
    "recorders": {}
}

# Count videos by recorder
for video in videos_info:
    recorder = video.get("recorder", "Unknown")
    if recorder in summary["recorders"]:
        summary["recorders"][recorder] += 1
    else:
        summary["recorders"][recorder] = 1

# Sort the recorders by number of videos (descending)
summary["recorders"] = dict(sorted(summary["recorders"].items(), 
                                  key=lambda item: item[1], 
                                  reverse=True))

# Find the most recent date
dates = [video.get("date") for video in videos_info if video.get("date")]
if dates:
    summary["most_recent_date"] = max(dates, default=None)

# Output to JSON file
output = {
    "summary": summary,
    "videos": videos_info
}

with open('video_library_data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Successfully extracted information for {len(videos_info)} videos.")
print(f"Total duration: {total_duration_formatted}")
print(f"Output saved to video_library_data.json")



# src="https://d3vine8rxbrpok.cloudfront.net/139/415/videos/2e74469b-415e-46f5-91bb-b395ead99c73/recall/2e74469b-415e-46f5-91bb-b395ead99c73.mp4"

# https://d3vine8rxbrpok.cloudfront.net/139/415/videos/2e74469b-415e-46f5-91bb-b395ead99c73/thumbnails/2e74469b-415e-46f5-91bb-b395ead99c73.0000000.jpg









# # ------------- GET AGGREGATED STATS

# call_stats = {}

# for call in videos_info:
#     user_id = call['user_id']
#     duration = call['duration']/60
#     started = call['year_month']

#     year_month = started


#     if user_id not in call_stats:
#         call_stats[user_id] = {"total_duration": 0, "call_count": 0, "months": set()}
    
#     call_stats[user_id]["total_duration"] += duration
#     call_stats[user_id]["call_count"] += 1
#     call_stats[user_id]["months"].add(year_month)  # Ensure this line is correctly adding months

# # Calculate month_count and avg_calls_per_user_per_month for each user
# for user_id, stats in call_stats.items():
#     month_count = len(stats["months"])  # Correctly access 'months' before deletion
#     stats["month_count"] = month_count
#     stats["avg_calls_per_user_per_month"] = round(stats["call_count"] / month_count,1) if month_count else 0
#     del stats["months"]  # Delete 'months' after its use

# # Calculate the average call duration for each user
# for user_id, stats in call_stats.items():
#     stats["avg_duration_per_call_per_user"] = round(stats["total_duration"] / stats["call_count"],1)

# # Output the calculated statistics per user
# for user_id, stats in call_stats.items():
#     print(f"User ID: {user_id}, {stats['call_count']} calls, {stats['avg_duration_per_call_per_user']}min on average, on {stats['month_count']} months")

# # Calculate totals
# total_calls = sum(stats['call_count'] for stats in call_stats.values())
# total_duration = round(sum(stats['total_duration'] for stats in call_stats.values()),1)/60
# total_month_counts = sum(stats['month_count'] for stats in call_stats.values())
# user_count = len(call_stats)

# print(f"Total calls: {total_calls}")
# print(f"total_duration: {total_duration}")

# average_duration_per_call = round(total_duration / total_calls,1) if total_calls else 0
# average_calls_per_user = total_calls / user_count if user_count else 0
# average_calls_per_user_per_month = round(total_calls / total_month_counts,1) if total_month_counts else 0

# print(f"Average Duration per Call Overall: {average_duration_per_call}h")
# print(f"Average Number of Calls per User: {average_calls_per_user}")
# print(f"Average Number of Calls per User per Month: {average_calls_per_user_per_month}")

# average_duration_per_user_per_month = average_duration_per_call*average_calls_per_user_per_month
# print(f"Average duration per user and per month: {average_duration_per_user_per_month}h")

# # --------- GET STATS PER USER

# # videos_info = [
# #     {'video_url': '/watch/415672', 'duration': 5800, 'user_id': '415', 'year_month': '2024-04'},
# #     {'video_url': '/watch/415673', 'duration': 3600, 'user_id': '415', 'year_month': '2024-04'},
# #     {'video_url': '/watch/415674', 'duration': 2900, 'user_id': '416', 'year_month': '2024-04'},
# #     {'video_url': '/watch/415675', 'duration': 4800, 'user_id': '416', 'year_month': '2024-05'}
# # ]

# # Using defaultdict to store sum of durations and count of videos
# results = defaultdict(lambda: {'total_duration': 0, 'video_count': 0})

# # Iterate over each video entry
# for video in videos_info:
#     key = (video['user_id'], video['year_month'])
#     results[key]['total_duration'] += video['duration']
#     results[key]['video_count'] += 1

# # Printing results
# for key, value in results.items():
#     user_id, year_month = key
#     print(f"User ID: {user_id}, Year-Month: {year_month}, Total Duration: {round(value['total_duration']/3600,1)}, Video Count: {value['video_count']}")