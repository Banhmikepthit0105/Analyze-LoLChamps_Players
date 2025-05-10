import requests
from bs4 import BeautifulSoup
import csv

def crawl_player_stats(year, csv_filename):
    seasons = ['Spring', 'Summer', 'Winter']
    tours = ['Promotion', 'Season', 'Playoffs',]

    for season in seasons:
        for tour in tours:

            url = f'https://lol.fandom.com/wiki/VCS/{year}_Season/{season}_{tour}/Champion_Statistics'
            table_class = "wikitable sortable spstats plainlinks hoverable-rows"

            try:
                # Send a GET request to the URL
                response = requests.get(url)
                response.raise_for_status()  # Check for HTTP errors

                # Parse the HTML content with BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find the table with the specified class
                table = soup.find('table', class_=table_class)
                if not table:
                    raise ValueError("No table found with the specified class.")

                rows = table.find_all('tr')[5:]

                # Extract data rows
                data_rows = []

                for row in rows:

                    row_data = [year, f'{season}_{tour}']

                    # For the 'Team' and 'Player' values, you might be referring to the first cell's link attributes.
                    # Extract the first cell (assuming it's a td) and get the link title.
                    first_td = row.find('td')

                    champion = first_td.find('span', class_='markup-object-name').get_text(strip=True)

                    row_data.append(champion)

                    # Now extract data from cells 2 to the second-last cell.
                    # Adjust the slicing based on your table's structure.
                    td_cells = row.find_all('td')

                    if len(td_cells) >= 3:  # Ensure there are enough cells
                        for cell in td_cells[1:-1]:
                            row_data.append(cell.get_text(strip=True))
                        # Extract the last cell's spans for 'champs'
                        last_cell = td_cells[-1]

                        champs = [span.get('title') for span in last_cell.find_all('span')]
                        row_data.append(champs)
                    else:
                        # If the structure is not as expected, skip this row or handle accordingly.
                        continue

                    data_rows.append(row_data)

                # Write the data to a CSV file

                with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)

                    # Write each row of data
                    writer.writerows(data_rows)

                print(f"{year} {season} {tour} successfully saved to {csv_filename}")

            except Exception as e:
                print(f"An error occurred: {e}")

def main():
    with open('champion_stats.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        headers = ['Year', 'Tournamment', 'Champion','G','PB','B','GP','By','W','L','WR','K','D','A','KDA','CS','CS/M','G','G/M','DMG','DMG/M','KPAR','KS','GS','As']
        writer.writerow(headers)
    
    for year in range(2018,2025):
        crawl_player_stats(year, 'champion_stats.csv')

if __name__ == '__main__':
    main()