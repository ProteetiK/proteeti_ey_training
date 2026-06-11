import json


def save_summary(
    summary_dict,
    output_file
):

    with open(
        output_file,
        "w"
    ) as f:

        json.dump(
            summary_dict,
            f,
            indent=4,
            default=str
        )