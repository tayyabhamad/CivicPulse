"""Small dependency-free load generator for local HPA demonstrations."""
import argparse
import concurrent.futures
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("--url", default="http://civicpulse.local/api/stats")
parser.add_argument("--requests", type=int, default=200)
parser.add_argument("--workers", type=int, default=20)
args = parser.parse_args()

def hit(_: int) -> bool:
    try:
        with urllib.request.urlopen(args.url, timeout=5) as response:
            return response.status < 500
    except OSError:
        return False

with concurrent.futures.ThreadPoolExecutor(args.workers) as pool:
    results = list(pool.map(hit, range(args.requests)))
print(f"success={sum(results)} failed={len(results) - sum(results)}")
