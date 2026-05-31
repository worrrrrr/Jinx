from core.orchestrator import Orchestrator


def main():
    system = Orchestrator()

    print("JINX runtime started")

    while True:
        text = input(">> ")
        if text.lower() in ["exit", "quit"]:
            break

        output = system.run(text)
        print(output)


if __name__ == "__main__":
    main()