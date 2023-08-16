from scrapper import ProductScrapper


def main():
    # ProductScrapper().test_scraping()
    ProductScrapper().do_scraping(
        basket=True,
        micm=True,
        sirena=True,
        jumbo=True,
        nacional=False,
        upload_to_db=True,
        purge_db=False,
    )


if __name__ == "__main__":
    main()
