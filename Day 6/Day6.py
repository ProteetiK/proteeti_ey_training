import argparse
parser = argparse.ArgumentParser(
        description="Process a list of integers and return sum or max."
    )
parser.add_argument(
        "integers",
        metavar="N",
        type=int,
        nargs=
        "+",  # one or more values
        help="an integer for the accumulator"
)
parser.add_argument(
        "--sum",
        dest="accumulate",
        action="store_const",
        const=sum,
        default=max,
        help="sum the integers (default: find the max)"
)
args = parser.parse_args(['1', '2', '3'])
result = args.accumulate(args.integers)
print(f"Result: {result}")




import schedule
import time
from datetime import datetime
def task_every_5_seconds():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Task executed every 5 seconds.")
schedule.every(5).seconds.do(task_every_5_seconds)
print("Scheduler started. Press Ctrl+C to stop.")
try:
    while True:
        schedule.run_pending()
        time.sleep(1)           
except KeyboardInterrupt:
    print("\nScheduler stopped by user.")




import subprocess
result = subprocess.run("dir", capture_output=True, text=True, shell=True)
print(result.stdout)
print("Output:", result.stdout)
if result.returncode != 0:
    print("Error:", result.stderr)



import os
from crontab import CronTab
current_user = os.getlogin()
cron = CronTab(user=current_user)
job = cron.new(command='echo hello_world')
job.minute.every(1)

cron.write()
