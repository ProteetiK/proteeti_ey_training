from app.db import (
    init_db,
    seed_inventory,
    show_state
)

from app.vector_store import remember

from app.agent import agent

from app.config import LIVE


def seed_memories():

    remember(
        """
        Customer Sarah reported monitor flickering
        caused by a faulty HDMI cable.
        """
    )

    remember(
        """
        Refund requests over $500 require
        manager approval.
        """
    )

    remember(
        """
        MON-4 monitor occasionally experiences
        display issues due to cable quality.
        """
    )

    remember(
        """
        USB-C HUB-2 is currently out of stock.
        """
    )


def startup():

    print("\nInitializing database...")

    init_db()

    print("Seeding inventory...")

    seed_inventory()

    print("Seeding memory...")

    seed_memories()

    print(
        "\nMode:",
        "LIVE" if LIVE else "OFFLINE"
    )

    print(
        "\nSupport Agent Ready"
    )


def repl():

    session_id = "demo-user"

    while True:

        print()

        user_text = input(
            "User> "
        ).strip()

        if not user_text:
            continue

        if user_text.lower() in (
            "quit",
            "exit"
        ):
            break

        if user_text.lower() == "state":

            show_state()

            continue

        try:

            answer = agent(
                session_id=session_id,
                user_text=user_text
            )

            print()
            print("Agent>")
            print(answer)

        except KeyboardInterrupt:

            print()
            print("Interrupted")

        except Exception as e:

            print()
            print(
                "Error:",
                repr(e)
            )


if __name__ == "__main__":

    startup()

    repl()