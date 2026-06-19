import os
import json
import asyncio
from pathlib import Path

import yt_dlp

from hume import AsyncHumeClient
from hume import HumeClient
from hume.expression_measurement.batch.types import (
    Models,
    Face,
    Prosody
)

class YouTubeEmotionAnalyzer:
    def __init__(
        self,
        hume_api_key: str,
        output_dir: str = "./results"
    ):
        self.client = AsyncHumeClient(api_key=hume_api_key)

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download_youtube_video(self, url: str) -> str:
        """
        Download YouTube video and return local path.
        """

        output_template = str(self.output_dir / "%(id)s.%(ext)s")

        ydl_opts = {
            "outtmpl": output_template,
            "format": "mp4/best"
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            video_id = info["id"]

            for file in self.output_dir.iterdir():
                if file.stem == video_id:
                    return str(file)

        raise RuntimeError("Downloaded file not found")

    async def analyze_emotions(
        self,
        video_path: str,
        models_to_use=None
    ):
        """
        Submit Hume job.
        """

        if models_to_use is None:
            models_to_use = ["face", "prosody"]

        config = Models()

        if "face" in models_to_use:
            config.face = Face()

        if "prosody" in models_to_use:
            config.prosody = Prosody()

        config = models

        job = await self.client.expression_measurement.batch.start_inference_job(
            files=[video_path],
            models=config,
        )

        return {
            "job_id": job.job_id,
            "status": "submitted"
        }

    async def wait_for_results(
        self,
        job_id: str,
        poll_interval: int = 10
    ):
        """
        Poll until Hume finishes.
        """

        while True:
            details = await self.client.expression_measurement.batch.get_job_details(
                job_id
            )

            state = details.state

            if state == "COMPLETED":
                break

            if state == "FAILED":
                raise RuntimeError(f"Job {job_id} failed")

            await asyncio.sleep(poll_interval)

        predictions = (
            await self.client.expression_measurement.batch.get_job_predictions(
                job_id
            )
        )

        return predictions

    def process_predictions(self, predictions):
        """
        Convert Hume output into readable summary.
        """

        emotion_totals = {}
        emotion_counts = {}

        try:
            results = predictions[0]["results"]["predictions"]

            for prediction in results:

                models = prediction.get("models", {})

                for model_name, model_data in models.items():

                    grouped = model_data.get("grouped_predictions", [])

                    for item in grouped:

                        emotions = item.get("predictions", [])

                        for emotion in emotions:
                            name = emotion["name"]
                            score = emotion["score"]

                            emotion_totals[name] = (
                                emotion_totals.get(name, 0) + score
                            )

                            emotion_counts[name] = (
                                emotion_counts.get(name, 0) + 1
                            )

        except Exception as e:
            return {
                "error": str(e)
            }

        averages = {
            k: emotion_totals[k] / emotion_counts[k]
            for k in emotion_totals
        }

        top_emotions = sorted(
            averages.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {
            "top_emotions": top_emotions,
            "emotion_count": len(averages),
        }

    def print_summary(self, summary):
        """
        Pretty print results.
        """

        print("\n=== Emotion Summary ===\n")

        for emotion, score in summary["top_emotions"]:
            print(f"{emotion:20} {score:.4f}")

    def save_results(
        self,
        results,
        filename="analysis.json"
    ):
        """
        Save JSON output.
        """

        path = self.output_dir / filename

        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                results,
                f,
                indent=2,
                ensure_ascii=False
            )

        return str(path)

