import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv


def scrape_mbfc_daily_fact_checks(days=30, output_csv='mbfc_fact_checks.csv'):
    """
    Scrapes Media Bias Fact Check's Daily Vetted Fact Checks for the last `days` days
    and writes date, claim, and rating to a CSV file.

    :param days: Number of days to go back (default=30).
    :param output_csv: Filename/path for the output CSV (default='mbfc_fact_checks.csv').
    """

    all_fact_checks = []
    today = datetime.today()

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
                # For simplicity, let's map "FALSE" or "BLATANT LIE" to "False".
                # Otherwise, you could store the raw text.
                # Adjust as needed if you want "Mostly False", "True", etc.
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
                    claim = claim_cell

                all_fact_checks.append({
                    "date": date_to_scrape.strftime("%Y-%m-%d"),
                    "claim": claim,
                    "rating": rating
                })

        except requests.exceptions.RequestException as e:
            print(f"  -> Error retrieving {url}: {e}")

    # Write results to CSV
    if all_fact_checks:
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["date", "claim", "rating"])
            writer.writeheader()
            for entry in all_fact_checks:
                writer.writerow(entry)
        print(f"\nScraped {len(all_fact_checks)} fact checks in total. Saved to '{output_csv}'.")
    else:
        print("No fact checks were found in the last 30 days or no data to save.")


if __name__ == "__main__":
    scrape_mbfc_daily_fact_checks(days=30, output_csv='mbfc_fact_checks.csv')
