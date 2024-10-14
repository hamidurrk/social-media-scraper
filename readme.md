# Facebook Profile Scraper

Welcome to the Facebook Profile Scraper! This repository contains the code for a web scraping tool that can extract data from Facebook profiles.

## Features

It can currently do the following tasks:

- Extract posts from a profile's timeline including date and time
- Scrape number of comments, reactions, and shares for each post
- Download the image in .jpg format if there's any
- Save the scraped data to a SQLite database and image files in the local directory

## Installation

1. Clone the repository: `git clone https://github.com/hamidurrk/social-media-scraper.git.git`
2. Install the required dependencies: `pip install -r requirements.txt`

## Usage

1. Create a file named `credential.txt` in your local machine and add the path.
2. Open `credential.txt` and add your Facebook password.
3. Run the script: `python src/main.py`


## Contributing

Contributions are welcome! Please open an issue or a pull request if you have any suggestions or improvements.

## Acknowledgments

- [Selenium](https://www.selenium.dev/) for providing the web automation framework.
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) for parsing HTML and XML.
- [SQLite](https://www.sqlite.org/) for the database management system.

