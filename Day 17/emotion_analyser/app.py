import asyncio
from youtube_emotion_analyzer import YouTubeEmotionAnalyzer
import os

HUME_API_KEY = os.getenv("HUME_API_KEY")

async def analyze_video():
    analyzer = YouTubeEmotionAnalyzer(
        hume_api_key=HUME_API_KEY,
        output_dir="./results"
    )

    video_path = analyzer.download_youtube_video(
        "https://youtube.com/shorts/dJFXhyzd2yY"
    )

    job_info = await analyzer.analyze_emotions(
        video_path,
        models_to_use=["face", "prosody", "burst"]
    )

    job_id = job_info["job_id"]

    print(f"Job ID: {job_id}")

    predictions = await analyzer.wait_for_results(job_id)

    summary = analyzer.process_predictions(predictions)

    analyzer.print_summary(summary)

    analyzer.save_results(summary, "analysis.json")


asyncio.run(analyze_video())