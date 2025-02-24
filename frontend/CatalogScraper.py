import csv
import requests
from bs4 import BeautifulSoup
import re

PREFIXS = [
    "ACCT",
    "ADPR",
    "ADVT",
    "AE",
    "AFAS",
    "AFST",
    "AGNR",
    "AI",
    "ALEC",
    "ANSC",
    "ANTH",
    "ARAB",
    "ARCH",
    "ARCN",
    "AREC",
    "ARED",
    "ART",
    "ARTA",
    "ARTB",
    "ARTC",
    "ARTD",
    "ARTH",
    "ARTM",
    "ARTN",
    "ASL",
    "ASST",
    "ASTR",
    "AUSP",
    "BAS",
    "BCMB",
    "BIOL",
    "BME",
    "BSE",
    "BUAD",
    "BULW",
    "CBE",
    "CCI",
    "CE",
    "CEM",
    "CHEM",
    "CHIN",
    "CLAS",
    "CMST",
    "CNST",
    "COSC",
    "COUN",
    "CSE",
    "CSM",
    "CYAL",
    "CYBR",
    "DATA",
    "DH",
    "DSGN",
    "ECE",
    "ECON",
    "EDDE",
    "EDPY",
    "EDUC",
    "EEB",
    "EEPS",
    "EF",
    "EI",
    "ELED",
    "ELI",
    "ELPS",
    "EMER",
    "ENED",
    "ENGL",
    "ENT",
    "ENVE",
    "EPP",
    "ESM",
    "ESS",
    "ETEC",
    "FDSC",
    "FINC",
    "FORS",
    "FREN",
    "FWF",
    "FYS",
    "GAME",
    "GEOG",
    "GERM",
    "GLBS",
    "GRDS",
    "HALS",
    "HBS",
    "HDFS",
    "HEBR",
    "HIAF",
    "HIAS",
    "HIEU",
    "HILA",
    "HIME",
    "HIST",
    "HIUS",
    "HONR",
    "HRM",
    "HTM",
    "IAC",
    "IARC",
    "IARN",
    "IB",
    "IE",
    "IEC",
    "INDS",
    "INMT",
    "INPG",
    "INSC",
    "INTE",
    "ITAL",
    "ITS",
    "JAPA",
    "JMED",
    "JST",
    "JUST",
    "KNS",
    "KORE",
    "LAC",
    "LAR",
    "LARN",
    "LING",
    "MARK",
    "MATH",
    "ME",
    "MEDU",
    "MEST",
    "MGT",
    "MICR",
    "MLS",
    "MLSL",
    "MRST",
    "MSE",
    "MUCO",
    "MUED",
    "MUEN",
    "MUIN",
    "MUJZ",
    "MUKB",
    "MUPF",
    "MUSC",
    "MUTC",
    "MUTH",
    "MUVC",
    "NE",
    "NEUR",
    "NORM",
    "NRSP",
    "NURS",
    "NUTR",
    "ORPM",
    "PBRL",
    "PERS",
    "PHIL",
    "PHYS",
    "PLSC",
    "POLS",
    "PORT",
    "PSYC",
    "PUBH",
    "PYED",
    "REED",
    "REST",
    "RMM",
    "RSM",
    "RUSS",
    "SCED",
    "SCM",
    "SOCI",
    "SOWK",
    "SPAN",
    "SPED",
    "SSCE",
    "STAT",
    "STHS",
    "SUST",
    "THEA",
    "TPTE",
    "TRNS",
    "UNHO",
    "UNST",
    "WFS",
    "WGS",
    "WLC",
    "WLEL",
]


def course_url(cat_id, course_id):
    return f"https://catalog.utk.edu/preview_course_nopop.php?catoid={cat_id}&coid={course_id}"


# Specify the URL


def get_major_url(major):
    return f"https://catalog.utk.edu/content.php?filter%5B27%5D={major}&filter%5B29%5D=&filter%5Bkeyword%5D=&filter%5B32%5D=1&filter%5Bcpage%5D=1&cur_cat_oid=51&expand=&navoid=10658&search_database=Filter#acalog_template_course_filter"


class Course:
    def __init__(self, cat_id, course_id):
        self.cat_id = cat_id
        self.prefix = ""
        self.course_id = course_id
        self.credits = 0
        self.description = ""
        self.repeat = ""
        self.restriction = ""
        self.pre_req = None
        self.core_req = None


COURSES = {}


# Send a GET request
def get_classes(url, des):
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Now you can work with the parsed HTML using BeautifulSoup
        mydivs = soup.find_all("td", class_="width")
        for info in mydivs:
            id = re.findall(r"'(\d*)',\s*'(\d*)'", str(info))[0]

            catalog_number = id[0]
            course_id = id[1]

            other = requests.get(course_url(catalog_number, course_id))
            s = BeautifulSoup(other.content, "html.parser")
            c = s.find_all("td", class_="block_content_outer")[0].find("p")
            w = re.sub(r"[^\x00-\x7F]+", " ", c.text)
            k = re.sub(r"(\.|\))([A-Z\(])", r"\1\n\2", w).split("\n")
            _info = re.findall(
                r"([A-Z]+)\s*(\d*[A-Z]?)\s*-\s*(.*?)\s*(\d-?\d?)\s*Credit Hours\s*(.*$)",
                k[0],
            )
            if len(_info) > 0:
                prefix, code, course_name, credit_hours, description = _info[0]

                print(prefix, code)
            core, pre = "", ""
            for i in range(1, len(k)):
                if re.match(r"\(RE\)\s*Prerequisite\(s\):", k[i]):
                    j = k[i].split("and")
                    for p in range(len(j)):
                        pre += " or ".join(
                            re.findall(r"\b([A-Z]+\s*\d+[A-Z]?)\b", j[p])
                        )
                        if p != len(j) - 1:
                            pre += " and "

                elif re.match(r"\(RE\)\s*Corequisite\(s\):", k[i]):
                    j = k[i].split("and")
                    for p in range(len(j)):
                        core += " or ".join(
                            re.findall(r"\b([A-Z]+\s*\d+[A-Z]?)\b", j[p])
                        )
                        if p != len(j) - 1:
                            core += " and "
            des.writerow(
                {
                    "prefix": prefix,
                    "code": code,
                    "course name": course_name,
                    "description": description,
                    "credit hours": credit_hours,
                    "pre reqs": pre,
                    "core reqs": core,
                }
            )  #     print(prefix, code)


with open("catalog.csv", "w", encoding="utf-8") as csvfile:
    fieldnames = [
        "prefix",
        "code",
        "course name",
        "description",
        "credit hours",
        "pre reqs",
        "core reqs",
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    for pre in PREFIXS:
        (get_classes(get_major_url(pre), writer))
