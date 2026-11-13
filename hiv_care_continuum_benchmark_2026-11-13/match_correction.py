"""Live, archived: identify the intended 'Dunlop 2022' (Table S3) whose article reference (no. 98)
is a 1980 chlamydia paper. Search OpenAlex for Dunlop-authored 2022 HIV works in Africa, then
resolve the candidate whose attributes fit Table S3 (South Africa; urban; 2004-2018; 168 months;
children under 15 on ART) by its DOI."""
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import match_benchmark as mb  # noqa: E402


def main():
    mb.pilot_credentials.load_key()
    mb.get("correction_search_dunlop_2022", "https://api.openalex.org/works?per_page=10&select=" + mb.FIELDS +
           "&filter=raw_author_name.search:Dunlop,publication_year:2022,title_and_abstract.search:" + urllib.parse.quote("HIV Africa"), auth=True)
    r = mb.get("correction_doi_HIV-098", "https://api.openalex.org/works/doi:10.7196/samj.2022.v112i5.16277?select=" + mb.FIELDS)
    print(r["id"], r["display_name"])


if __name__ == "__main__":
    main()
