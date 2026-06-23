def route(
    user_text: str
):

    text = user_text.lower()

    order_words = [
        "order",
        "buy",
        "purchase",
        "sku"
    ]

    support_words = [
        "broken",
        "issue",
        "problem",
        "flicker",
        "ticket"
    ]

    escalation_words = [
        "refund",
        "manager",
        "complaint",
        "escalate"
    ]

    if any(
        word in text
        for word in escalation_words
    ):
        return "escalation"

    if any(
        word in text
        for word in order_words
    ):
        return "order"

    if any(
        word in text
        for word in support_words
    ):
        return "support"

    return "faq"