import tabula
import pandas as pd
import numpy as np
from typing import List
from tqdm import tqdm
from functools import reduce
import locale
import unicodedata

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

# list of csv names and which page to extract a table from
DATA = [
    {"name": "02-03", "page": "13"},
    {"name": "03-04", "page": "13"},
    {"name": "04-05", "page": "13"},
    {"name": "05-06", "page": "11"},
    {"name": "06-07", "page": "11"},
    {"name": "07-08", "page": "11"},
    {"name": "08-09", "page": "11"},
    {"name": "09-10", "page": "11"},
    {"name": "10-11", "page": "7"},
    {"name": "11-12", "page": "7"},
    {"name": "12-13", "page": "8"},
    {"name": "13-14", "page": "7"},
    {"name": "14-15", "page": "7"},
    {"name": "15-16", "page": "7"},
    {"name": "16-17", "page": "7"},
    {"name": "17-18", "page": "8"},
    {"name": "18-19", "page": "8"},
    {"name": "19-20", "page": "7"},
    {"name": "20-21", "page": "7"},
]

## helper functions
def setTypes(df, stringColumns: List[str]):
    """
    fix any comma'ed numbers and set all numerical columns to int64 type,
    and all designated stringColumns to string type
    """
    return pd.merge(
        df[stringColumns],
        df.drop(columns=stringColumns)
        .astype("str")  # prevent errors with 0 being autocast to int
        .applymap(locale.atoi),  # comma'ed numbers
        left_index=True,
        right_index=True,
    ).astype(flattenDictionary([{c: pd.StringDtype()} for c in stringColumns]))


def flattenDictionary(d: List[dict]):
    """
    flatten a list of dicts into one dict
    """

    def f(x, y):
        x.update(y)
        return x

    return reduce(f, d)


def stateToDistrict(state):
    """
    returns the 1991-2005 district for a state
    """
    if state in ["DE", "E PA", "NJ"]:
        return "Atlantic"
    elif state in ["IL", "IA", "KS", "MO", "NE", "WI"]:
        return "Central"
    elif state == "MA":
        return "Massachusetts"
    elif state == "MI":
        return "Michigan"
    elif state in ["IN", "KY", "OH", "W PA", "WV"]:
        return "Mid-American"
    elif state in ["MN", "ND", "SD"]:
        return "Minnkota"
    elif state in ["CT", "ME", "NH", "RI", "VT"]:
        return "New England"
    elif state == "NY":
        return "New York"
    elif state in ["AK", "CA", "HI", "NV", "OR", "WA"]:
        return "Pacific"
    elif state in ["AZ", "CO", "ID", "MT", "NM", "OK", "TX", "UT", "WY"]:
        return "Rocky Mountain"
    elif state in [
        "AL",
        "AR",
        "DC",
        "FL",
        "GA",
        "LA",
        "MD",
        "MS",
        "NC",
        "SC",
        "TN",
        "VA",
    ]:
        return "Southeastern"


# processing functions


def tables_to_csvs(
    data: List, import_path: str = "./data/pdfs/", export_path: str = "./data/csvs/raw/"
):
    """
    extract tables from PDFs and convert into CSVs
    """
    for year in tqdm(data):
        tabula.convert_into(
            f"{import_path}{year['name']}.pdf",
            f"{export_path}{year['name']}.csv",
            output_format="csv",
            pages=year["page"],
        )


def clean_csv(
    name,
    import_path: str = "./data/csvs/raw/",
    export_path: str = "./data/csvs/cleaned/",
):
    """
    take a csv and fix any formatting issues from reading in the PDFs
    """
    if name != "05-06":
        df = pd.read_csv(f"{import_path}{name}.csv")

        if name in ["02-03", "03-04", "04-05"]:
            df = setTypes(df, ["STATE"])
        elif name in ["06-07", "07-08", "12-13", "15-16"]:
            df = setTypes(df, ["District", "State"])
        elif name in ["08-09", "09-10", "10-11", "11-12"]:
            df = df.iloc[:-2]
            df["19"] = df["19"].astype("int64")
            df = setTypes(df, ["District", "State"])
        elif name in ["13-14", "14-15", "16-17"]:
            # totals is correct; preserve and drop from rest of df
            totals = df.iloc[-1, :-1]
            df = df.iloc[:-1]
            # fix column names
            if name == "13-14":
                df = df.drop(
                    columns=[
                        "Total",
                        "State",
                        "20&over",
                        "13-14",
                        "11-12",
                        "9-10",
                        "Unnamed: 18",
                    ]
                ).rename(
                    columns={
                        "Unnamed: 2": "State",
                        "Unnamed: 4": "Total",
                        "19": "20&over",
                        "17-18": "19",
                        "15-16": "17-18",
                        "Unnamed: 9": "15-16",
                        "Unnamed: 11": "13-14",
                        "Unnamed: 13": "11-12",
                        "7-8": "9-10",
                        "6&U": "7-8",
                        "Unnamed: 17": "6&U",
                    }
                )

            if name == "14-15" or name == "16-17":
                if name == "14-15":
                    df = df.drop(columns="State").rename(
                        columns={"Unnamed: 2": "State"}
                    )
                c = df.iloc[:, 2:].columns
                colNames = flattenDictionary([{x: y} for x, y in zip(c[1:], c)])
                df = df.drop(columns="Total").rename(columns=colNames)

            def fixColumns(columnName):
                # https://stackoverflow.com/a/17116976
                s = df[columnName].str.split("\r").apply(pd.Series, 1).stack()
                s.name = columnName
                return s.reset_index(drop=True)

            df = (
                pd.concat([fixColumns(c) for c in df.columns], axis=1)
                .append(totals[list(df.columns)])
                .reset_index(drop=True)
            )
            df = setTypes(df, ["District", "State"])

        elif name in ["17-18", "18-19", "19-20", "20-21"]:
            # everyone hates dash variants; what Is the diff between a dash and a hyphen
            df = df.applymap(
                lambda x: str(x)
                .encode("utf-8")
                .replace(b"\xe2\x80\x90", b"-")
                .decode("utf-8")
            )
            df.columns = df.columns.map(
                lambda x: x.encode("utf-8")
                .replace(b"\xe2\x80\x90", b"-")
                .decode("utf-8")
            )
            df = setTypes(df.replace("-", "0"), ["District", "State"])
    elif name == "05-06":
        df1 = (
            pd.read_csv(f"{import_path}{name}.csv", dtype="object", nrows=20)
            .dropna(how="all")
            .dropna(how="all", axis="columns")
            .drop(1)
            .transpose()
            .reset_index(drop=True)
            .drop(0)
        )
        df2 = (
            pd.read_csv(f"{import_path}{name}.csv", dtype="object", skiprows=20)
            .dropna(how="all")
            .dropna(how="all", axis="columns")
            .transpose()
            .iloc[:-1]
        )

        df1.columns = df2.columns = [
            "20&Over",
            "19",
            "17-18",
            "15-16",
            "13-14",
            "11-12",
            "9-10",
            "7-8",
            "6&U",
            "Total",
        ]
        df1["State"] = [
            "AL",
            "AK",
            "AZ",
            "AR",
            "CA",
            "CO",
            "CT",
            "DE",
            "DC",
            "FL",
            "GA",
            "HI",
            "ID",
            "IL",
            "IN",
            "IA",
            "KS",
            "KY",
            "LA",
            "ME",
            "MD",
            "MA",
            "MI",
            "MN",
            "MS",
            "MO",
        ]
        df2["State"] = [
            "MT",
            "NE",
            "NV",
            "NH",
            "NJ",
            "NM",
            "NY",
            "NC",
            "ND",
            "OH",
            "OK",
            "OR",
            "E PA",
            "W PA",
            "RI",
            "SC",
            "SD",
            "TN",
            "TX",
            "UT",
            "VT",
            "VA",
            "WA",
            "WV",
            "WI",
            "WY",
        ]
        df = pd.concat([df1, df2]).reset_index(drop=True)
        df["District"] = df["State"].apply(stateToDistrict)
        df = setTypes(df, ["District", "State"])
    df.to_csv(f"{export_path}{name}.csv", index=False)


def clean_csvs(data):
    """
    clean all csvs
    """
    for year in tqdm(data):
        clean_csv(year["name"])


def combine_table(full_df, name, import_path: str = "data/csvs/cleaned/"):
    """
    merge two yearly tables into one table
    """
    df = pd.read_csv(f"{import_path}{name}.csv")
    if name in [
        "08-09",
        "09-10",
        "10-11",
        "11-12",
        "12-13",
        "13-14",
        "14-15",
        "15-16",
    ]:
        # adding back Hawaii
        df.loc[len(df.index)] = ["Pacific", "HI"] + [0] * 10
        df = df.sort_values("District")

    # standardize column names
    df = df.rename(columns={"20&over": "20&Over"})
    if name != "05-06":
        # get rid of total row, which is always last
        df = df.iloc[:-1]

    df.insert(0, "Year", "20" + name[:2])
    return pd.concat([full_df, df])


def combine_tables(
    data,
    import_path: str = "data/csvs/cleaned/",
    export_path: str = "data/csvs/merged/girls-women-by-district-by-state.csv",
):
    """
    combine all tables
    """
    # 04-05 csv contains all data from 1991
    full_df = pd.read_csv(f"{import_path}04-05.csv").rename(columns={"STATE": "State"})
    full_df = full_df[full_df.apply(lambda x: x != "TOTAL")].dropna()
    full_df = pd.melt(full_df, id_vars="State", var_name="Year", value_name="Total")
    full_df["Year"] = full_df["Year"].map(
        lambda x: "20" + x[:2] if x[0] == "0" else "19" + x[:2]
    )
    # lack of PA split in data pre '05 makes districts hard to parse
    # full_df.insert(0, "District", full_df["State"].apply(stateToDistrict))
    full_df.insert(0, "District", pd.NA)

    full_df.insert(0, "Year", full_df.pop("Year"))
    df_cols = pd.DataFrame(
        [[pd.NA] * 9] * full_df.shape[0],
        columns=[
            "20&Over",
            "19",
            "17-18",
            "15-16",
            "13-14",
            "11-12",
            "9-10",
            "7-8",
            "6&U",
        ],
    )
    full_df = pd.concat([full_df, df_cols], axis=1)

    for file in tqdm(data):
        if file["name"] not in ["02-03", "03-04", "04-05"]:
            full_df = combine_table(full_df, file["name"])
    full_df = full_df.sort_values(["Year", "District"]).reset_index(drop=True)
    full_df.to_csv(export_path, index=False)
    full_df.to_pickle("./data/pkls/girls-women-by-district-by-state.pkl")


def state_change_tables():
    """
    calculate the percent and absolute change between years for states
    """
    full_df = pd.read_pickle("./data/pkls/girls-women-by-district-by-state.pkl")

    l = [
        ("pct_change_91-04", True),
        ("abs_change_91-04", False),
        ("pct_change_06-20", True),
        ("abs_change_06-20", False),
    ]
    for (name, bool) in l:
        years = name[-5:]
        if years == "91-04":
            df = full_df[(full_df.Year.apply(int) < 2005) & (full_df.Year != "1990")]
        elif years == "06-20":
            df = full_df[full_df.Year.apply(int) >= 2006]
        df = df.apply(change, args=(years, bool, full_df, "State"), axis="columns")
        if years == "91-04":
            df = df[["Year", "State", "Total"]]
        df.to_csv(f"./data/csvs/merged/{name}.csv", index=False)
        df.to_pickle(f"./data/pkls/{name}.pkl")


def district_tables():
    """
    calculate the percent and absolute change between years for districts
    (only after 2007)
    """
    full_df = pd.read_pickle("./data/pkls/girls-women-by-district-by-state.pkl")
    new_dist_df = (
        full_df[full_df.Year.astype("int") >= 2007]
        .astype("int", errors="ignore")
        .drop(columns=["State"])
        .groupby(by=["Year", "District"])
        .sum(numeric_only=False)
        .reset_index()
    )
    l = [
        ("pct_change_districts", True),
        ("abs_change_districts", False),
    ]
    for (name, bool) in l:
        df = new_dist_df[new_dist_df.Year.astype("int") >= 2008].apply(
            change, args=("districts", bool, new_dist_df, "District"), axis="columns"
        )
        df.to_csv(f"./data/csvs/merged/{name}.csv", index=False)
        df.to_pickle(f"./data/pkls/{name}.pkl")


def change(
    row,
    years,
    percentBool,
    full_df,
    groupCol,
):
    """
    helper function for calculating the change between two years
    """
    newRow = row
    prevYearRow = full_df[
        (full_df.Year == str(int(row.Year) - 1)) & (full_df[groupCol] == row[groupCol])
    ].squeeze()

    def calculateChange(newRow, column):
        try:
            if percentBool:
                newRow[column] = (
                    (row[column] - prevYearRow[column]) / prevYearRow[column]
                ) * 100
            else:
                newRow[column] = row[column] - prevYearRow[column]
        except:
            newRow[column] = np.nan
        return newRow

    newRow = calculateChange(newRow, "Total")
    if years == "06-20":
        for column in row.index[4:]:
            newRow = calculateChange(newRow, column)
    elif years == "districts":
        for column in row.index[3:]:
            newRow = calculateChange(newRow, column)
    return newRow


# run entire data process
if __name__ == "__main__":
    tables_to_csvs(DATA)
    clean_csvs(DATA)
    combine_tables(DATA)
    state_change_tables()
    district_tables()
