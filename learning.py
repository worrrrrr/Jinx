# learning.py

import json
import time
from datetime import datetime

from core.llm_core import JinxLLMCore


LOG_FILE = "logs/learning.jsonl"


def save_log(data):
    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            json.dumps(
                data,
                ensure_ascii=False
            ) + "\n"
        )


def main():

    core = JinxLLMCore()

    if not core.available:
        print("No provider found")
        return

    print("\nProviders:")

    for i, p in enumerate(
        core.provider_names,
        start=1
    ):
        print(f"{i}. {p}")

    idx = int(
        input("\nChoose Provider: ")
    ) - 1

    provider_name = core.provider_names[idx]

    provider = core.providers[
        provider_name
    ]

    print(
        f"\nUsing: {provider_name}"
    )

    while True:

        question = input(
            "\nQuestion: "
        ).strip()

        if question.lower() in [
            "exit",
            "quit"
        ]:
            break

        start = time.perf_counter()

        answer = provider.chat(
            prompt=question,
            temperature=0.3,
            max_tokens=1024
        )

        elapsed = (
            time.perf_counter()
            - start
        )

        print("\nAnswer:")
        print(answer)

        print(
            f"\nTime: {elapsed:.3f}s"
        )

        record = {

            "timestamp":
                datetime.now()
                .isoformat(),

            "provider":
                provider_name,

            "question":
                question,

            "answer":
                answer,

            "time":
                round(
                    elapsed,
                    3
                )

        }

        save_log(record)


if __name__ == "__main__":
    main()