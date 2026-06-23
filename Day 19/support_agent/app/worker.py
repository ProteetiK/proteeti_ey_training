from app.tools import run_worker


def process_background_jobs():

    processed = run_worker()

    if processed:
        print(
            f"[worker] processed "
            f"{processed} jobs"
        )

    return processed