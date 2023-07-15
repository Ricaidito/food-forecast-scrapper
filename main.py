from scrapper import ProductScrapper


def main():
    ProductScrapper().do_scraping(
        basket=False,
        micm=False,
        sirena=True,
        jumbo=False,
        nacional=False,
        upload_to_db=False,
    )


if __name__ == "__main__":
    main()
