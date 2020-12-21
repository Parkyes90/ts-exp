import os
from collections import defaultdict

import pandas as pd

from src.career_experiences.constants import CAREER_EXP_INPUTS_DIR


def read_files():
    return os.listdir(CAREER_EXP_INPUTS_DIR)


def get_survey_map_excel(path):
    df = pd.read_excel(path).fillna("")
    columns = df.columns
    survey_map = {}
    for column in columns[1:]:

        rows = df[column].loc[df[column] != ""]
        total_row_count = len(rows)
        unique_select = set()
        select_count_map = defaultdict(int)
        for row in rows:
            if isinstance(row, str) and "," in row:
                for r in row.split(","):
                    unique_select.add(r.strip())
                    select_count_map[r] += 1
            else:
                select_count_map[row] += 1
                unique_select.add(row)
        unique_select_count = len(unique_select)
        frequency = unique_select_count / total_row_count
        is_subject = frequency >= 0.15
        if not is_subject:
            survey_map[column] = select_count_map

    return survey_map


def process_survey_map(survey_map):
    print(survey_map)


def parse():
    files = read_files()
    for file in files[:1]:
        survey_map = get_survey_map_excel(
            os.path.join(CAREER_EXP_INPUTS_DIR, file)
        )
        process_survey_map(survey_map)


def main():
    parse()


if __name__ == "__main__":
    main()
