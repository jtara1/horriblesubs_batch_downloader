# from scrapy.crawler import CrawlerProcess

from settings import main_settings
# from shows_spider import HorribleSubsShowsSpider
from shows_scraper import ShowsScraper
from show_selector import ShowSelector
from episodes_scraper import HorribleSubsEpisodesScraper

import os
import sys
import time


def get_command_line_arguments():
    """Returns all cli args joins with '-' char if there are any, otherwise returns the empty string"""
    if len(sys.argv) > 1:
        return "-".join(sys.argv[1:])
    else:
        return ""


def get_age_of_file(file):
    """Returns how much time has passed since the file's creation time in hours"""
    python_version = sys.version[0]
    FileNotFoundException = OSError if python_version == '2' else FileNotFoundException
    try:
        file_stats = os.stat(file)
        file_age = time.time() - file_stats.st_ctime  # time in seconds
        return file_age / 3600
    except FileNotFoundException:
        return sys.maxsize


def main():
    def create_new_file(file_path):
        if not os.path.isdir(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        with open(file_path, 'w') as f:
            f.write('')

    # use cli args if provided
    cli_args_concatenated = get_command_line_arguments()
    if cli_args_concatenated:
        search_key_word = cli_args_concatenated
    else:
        search_key_word = raw_input("Enter anime to download from HorribleSubs: ")

    # search_key_word = '91-days'
    print("Searching for {} ...".format(search_key_word))

    # output file for shows spider
    shows_file_path = os.path.join(os.getcwd(), 'tmp/shows.txt')
    file_age = get_age_of_file(shows_file_path)

    # the file containing the list of shows does not exist or is expired
    if file_age > main_settings['show_list_expiration']:
        create_new_file(shows_file_path)

        scrapy_settings = {
            'USER_AGENT': '''Mozilla/5.0 (X11;
                Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36''',
            'LOG_STDOUT': False,
            'LOG_FILE': None,
            # 'ITEM_PIPELINES': {'horriblesubs_shows_spider.PrintItemsPipeline': 100},
            'FEED_URI': 'file:///' + shows_file_path,
            'FEED_FORMAT': 'json',
            }

        # start crawling with the shows spider
        # process = CrawlerProcess(scrapy_settings)
        # process.crawl(HorribleSubsShowsSpider)
        # process.start()

        shows_scraper = ShowsScraper()
        shows_scraper.save_shows_to_file(file=shows_file_path)

    # get url of show user searched for
    show_selector = ShowSelector(shows_file=shows_file_path, search_key_word=search_key_word)
    show_url = show_selector.get_desired_show_url()

    # scrape the episodes and download all of them in the highest resolution available
    ep_scraper = HorribleSubsEpisodesScraper(show_url=show_url, debug=True)
    user_input = raw_input("Press enter to proceed to download or [n]o to cancel: ")
    if user_input == "":
        ep_scraper.download()


if __name__ == "__main__":
    main()
