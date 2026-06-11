from pathlib import Path


def generate_markdown_report(
    report_data,
    output_file
):

    lines = []

    lines.append(
        "# Time Series EDA Report\n"
    )

    for section, data in report_data.items():

        lines.append(
            f"## {section}\n"
        )

        lines.append(
            f"{data}\n"
        )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "\n".join(lines)
        )