import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from datetime import datetime, timedelta
import csv
import pandas as pd


def scrape_mbfc_daily_fact_checks(days=30, output_csv='mbfc_fact_checks.csv'):
    """
    Scrapes Media Bias Fact Check's Daily Vetted Fact Checks for the last `days` days
    and writes date, claim, and rating to a CSV file.

    :param days: Number of days to go back (default=30).
    :param output_csv: Filename/path for the output CSV (default='mbfc_fact_checks.csv').
    """

    all_fact_checks = []
    today = datetime(2025, 4, 8)


    for i in range(days):
        date_to_scrape = today - timedelta(days=i)
        year_str = date_to_scrape.strftime('%Y')
        month_str = date_to_scrape.strftime('%m')
        day_str = date_to_scrape.strftime('%d')

        # Typical MBFC daily post pattern:
        # https://mediabiasfactcheck.com/yyyy/mm/dd/mbfcs-daily-vetted-fact-checks-for-mm-dd-yyyy/
        url = (
            f"https://mediabiasfactcheck.com/"
            f"{year_str}/{month_str}/{day_str}/"
            f"mbfcs-daily-vetted-fact-checks-for-{month_str}-{day_str}-{year_str}/"
        )

        print(f"Scraping {url}")
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                print(f"  -> Page not found or error (status code {response.status_code})")
                continue

            # Parse the HTML
            soup = BeautifulSoup(response.text, "html.parser")
            factcheck_table = soup.find("table", {"class": "alignleft", "border": "1"})
            if not factcheck_table:
                print("  -> Could not find the expected fact-check table.")
                continue

            # Extract rows from the table
            tbody = factcheck_table.find("tbody")
            if not tbody:
                print("  -> No <tbody> found in table.")
                continue

            rows = tbody.find_all("tr", recursive=False)
            if not rows:
                print("  -> No <tr> rows found in <tbody>.")
                continue

            for row in rows:
                tds = row.find_all("td", recursive=False)
                if len(tds) != 2:
                    continue

                # 1) Rating cell (left <td>)
                rating_cell = tds[0].get_text(separator=" ", strip=True)
                rating_upper = rating_cell.upper()
                if "FALSE" in rating_upper or "BLATANT" in rating_upper:
                    rating = "False"
                else:
                    rating = rating_cell

                # 2) Claim cell
                claim_cell = tds[1].get_text(separator=" ", strip=True)
                claim_prefix = "claim via social media:"
                idx = claim_cell.lower().find(claim_prefix)
                if idx != -1:
                    claim = claim_cell[idx + len(claim_prefix):].strip()
                else:
                    claim = claim_cell.strip()

                # Step: Remove trailing fact-check source explanations
                fact_checker_sources = [
                    "PolitiFact", "Politifact", "Lead Stories",
                    "Snopes", "Science Feedback", "TruthOrFiction",
                    "FactCheck.org", "Reuters Fact Check", "Check Your Facts",
                    "Logically Fact", "Newsweek rating"
                ]

                for source in fact_checker_sources:
                    source_idx = claim.find(source)
                    if source_idx != -1:
                        claim = claim[:source_idx].strip()
                        break  # Stop at the first source match

                # Optional: strip trailing punctuation or quotes
                claim = claim.strip('“”" ').rstrip(".") + "."
                if '(International:' in claim:
                    pass
                else:
                    all_fact_checks.append({
                        "date": date_to_scrape.strftime("%Y-%m-%d"),
                        "claim": claim,
                        "rating": rating
                    })
            fact_checker_sources = [
                "PolitiFact", "Politifact", "Snopes", "Science Feedback",
                "TruthOrFiction", "FactCheck.org", "Reuters Fact Check",
                "Logically Facts", "Lead Stories rating", "Newsweek rating",
                "Associated Press", "Australian Associated Press",
                "Check Your Fact", "AAP rating", "DW rating", "WKYC rating",
                "USA Today rating", "KSDK rating", "Full Fact rating"
            ]
            for source in fact_checker_sources:
                source_idx = claim.find(source)
                if source_idx != -1:
                    claim = claim[:source_idx].strip()
                    break
            claim = claim.strip('“”" ').rstrip(".") + "."
        except requests.exceptions.RequestException as e:
            print(f"  -> Error retrieving {url}: {e}")

    # Write results to CSV
    if all_fact_checks:
        df = pd.DataFrame(all_fact_checks)
        df.to_csv(output_csv.replace(".csv", ".tsv"), sep='\t', index=False, encoding='utf-8')
        print(f"\nScraped {len(all_fact_checks)} fact checks in total. Saved to '{output_csv}'.")
    else:
        print("No fact checks were found in the last 30 days or no data to save.")


if __name__ == "__main__":
    scrape_mbfc_daily_fact_checks(days=60, output_csv='fact_check_test.csv')
