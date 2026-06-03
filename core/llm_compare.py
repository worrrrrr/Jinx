import json
import re
import time
from pathlib import Path
from datetime import datetime

from llm_core import JinxLLMCore


# =====================
# PATHS
# =====================

DATA_FILE = Path("data/benchmark_cases.json")

LOG_DIR = Path("logs/llm_compare")
LOG_DIR.mkdir(parents=True, exist_ok=True)

RAW_FILE = LOG_DIR / "raw.jsonl"
SUMMARY_FILE = LOG_DIR / "summary.json"
REPORT_FILE = LOG_DIR / "latest_report.md"


# =====================
# LOAD CASES
# =====================

with open(DATA_FILE, encoding="utf8") as f:
    TEST_CASES = json.load(f)


# =====================
# HELPERS
# =====================

def normalize(text):

    if text is None:
        return ""

    return str(text).lower().strip()


def evaluate(answer, expected_values):

    text = normalize(answer)

    for value in expected_values:

        if normalize(value) in text:
            return True

    return False


def bar(score, width=20):

    filled = int(width * score / 100)

    return (
        "█" * filled +
        "░" * (width - filled)
    )


def save_raw(record):

    with open(
        RAW_FILE,
        "a",
        encoding="utf8"
    ) as f:

        f.write(
            json.dumps(
                record,
                ensure_ascii=False
            ) + "\n"
        )


# =====================
# BENCHMARK
# =====================

def benchmark_provider(
    provider_name,
    provider
):

    total = len(TEST_CASES)

    passed = 0

    all_times = []

    category_stats = {}

    for case in TEST_CASES:

        start = time.perf_counter()

        answer = provider.chat(
            case["question"]
        )

        elapsed = (
            time.perf_counter()
            - start
        )

        success = evaluate(
            answer,
            case["expected"]
        )

        if success:
            passed += 1

        category = case["category"]

        if category not in category_stats:

            category_stats[category] = {
                "total": 0,
                "passed": 0
            }

        category_stats[category]["total"] += 1

        if success:
            category_stats[category]["passed"] += 1

        all_times.append(elapsed)

        save_raw({

            "timestamp":
            datetime.now().isoformat(),

            "provider":
            provider_name,

            "category":
            category,

            "question":
            case["question"],

            "expected":
            case["expected"],

            "answer":
            answer,

            "success":
            success,

            "time":
            round(elapsed, 3)
        })

    accuracy = (
        passed / total
    ) * 100

    avg_time = (
        sum(all_times)
        / len(all_times)
    )

    speed_score = min(
        100,
        round(
            100 / (avg_time + 1),
            2
        )
    )

    return {

        "accuracy":
        round(accuracy, 2),

        "speed":
        speed_score,

        "avg_time":
        round(avg_time, 3),

        "passed":
        passed,

        "failed":
        total - passed,

        "categories":
        category_stats
    }


# =====================
# REPORT
# =====================

def create_report(summary):

    lines = []

    lines.append(
        "# Jinx Benchmark\n"
    )

    lines.append(
        f"Generated: {datetime.now()}\n"
    )

    for provider, data in summary.items():

        lines.append(
            f"\n## {provider}\n"
        )

        lines.append(
            f"Accuracy {bar(data['accuracy'])} {data['accuracy']}%"
        )

        lines.append(
            f"Speed    {bar(data['speed'])} {data['speed']}%"
        )

        lines.append(
            f"Avg Time : {data['avg_time']}s"
        )

        lines.append(
            f"Passed   : {data['passed']}"
        )

        lines.append(
            f"Failed   : {data['failed']}"
        )

        lines.append("")

        lines.append(
            "### Categories"
        )

        for cat, stat in data["categories"].items():

            score = round(
                stat["passed"]
                / stat["total"]
                * 100,
                2
            )

            lines.append(
                f"- {cat}: {score}% ({stat['passed']}/{stat['total']})"
            )

    REPORT_FILE.write_text(
        "\n".join(lines),
        encoding="utf8"
    )


# =====================
# MAIN
# =====================

def main():

    core = JinxLLMCore()

    summary = {}

    print()
    print("=" * 60)
    print("JINX LLM COMPARE")
    print("=" * 60)

    for name, provider in core.providers.items():

        print()
        print(f"Testing: {name}")

        result = benchmark_provider(
            name,
            provider
        )

        summary[name] = result

        print(
            f"Accuracy {bar(result['accuracy'])} {result['accuracy']}%"
        )

        print(
            f"Speed    {bar(result['speed'])} {result['speed']}%"
        )

        print(
            f"Avg Time {result['avg_time']}s"
        )

    with open(
        SUMMARY_FILE,
        "w",
        encoding="utf8"
    ) as f:

        json.dump(
            summary,
            f,
            indent=2,
            ensure_ascii=False
        )

    create_report(summary)

    print()
    print("Saved:")
    print(SUMMARY_FILE)
    print(REPORT_FILE)


if __name__ == "__main__":
    main()