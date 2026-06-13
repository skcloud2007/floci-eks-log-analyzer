import os
import re
from collections import Counter

import boto3
from fastapi import FastAPI, Query

app = FastAPI(title="Floci EKS Log Analyzer")

S3_BUCKET = os.getenv("S3_BUCKET", "SKM-Bucket")
S3_KEY = os.getenv("S3_KEY", "apache_logs")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "http://host.docker.internal:4566")

s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT_URL,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
)

log_pattern = re.compile(
    r'^(\S+)\s+\S+\s+\S+\s+\[[^\]]+\]\s+"([A-Z]+)\s+(\S+)\s+HTTP/[0-9.]+"\s+(\d{3})'
)

def parse_line(line: str):
    match = log_pattern.search(line)

    if not match:
        return None

    return {
        "ip": match.group(1),
        "method": match.group(2),
        "url": match.group(3),
        "status": match.group(4),
        "raw": line,
    }

def read_log_lines():
    obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_KEY)

    for raw_line in obj["Body"].iter_lines():
        yield raw_line.decode("utf-8", errors="ignore")

@app.get("/")
def home():
    return {
        "message": "Floci EKS Log Analyzer is running",
        "bucket": S3_BUCKET,
        "key": S3_KEY,
    }

@app.get("/top-ips")
def top_ips(limit: int = Query(default=10, ge=1, le=100)):
    counter = Counter()

    for line in read_log_lines():
        data = parse_line(line)
        if data:
            counter[data["ip"]] += 1

    return counter.most_common(limit)

@app.get("/top-urls")
def top_urls(limit: int = Query(default=10, ge=1, le=100)):
    counter = Counter()

    for line in read_log_lines():
        data = parse_line(line)
        if data:
            counter[data["url"]] += 1

    return counter.most_common(limit)

@app.get("/status-codes")
def status_codes():
    counter = Counter()

    for line in read_log_lines():
        data = parse_line(line)
        if data:
            counter[data["status"]] += 1

    return dict(counter)

@app.get("/error-ips")
def error_ips(limit: int = Query(default=10, ge=1, le=100)):
    counter = Counter()

    for line in read_log_lines():
        data = parse_line(line)

        if data and data["status"].startswith(("4", "5")):
            counter[data["ip"]] += 1

    return counter.most_common(limit)

@app.get("/summary")
def summary():
    total = 0
    ip_counter = Counter()
    url_counter = Counter()
    status_counter = Counter()

    for line in read_log_lines():
        data = parse_line(line)

        if data:
            total += 1
            ip_counter[data["ip"]] += 1
            url_counter[data["url"]] += 1
            status_counter[data["status"]] += 1

    return {
        "total_parsed_requests": total,
        "top_5_ips": ip_counter.most_common(5),
        "top_5_urls": url_counter.most_common(5),
        "status_codes": dict(status_counter),
    }
