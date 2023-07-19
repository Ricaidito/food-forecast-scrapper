from scrapper import ProductScrapper


def main():
    # ProductScrapper().test_scraping()
    ProductScrapper().do_scraping(
        basket=False,
        micm=False,
        sirena=False,
        jumbo=False,
        nacional=False,
        upload_to_db=True,
    )


if __name__ == "__main__":
    main()
