from scrapper import ProductScrapper


ProductScrapper().do_scraping(
    basket=False,
    micm=False,
    sirena=True,
    jumbo=False,
    nacional=False,
    upload_to_db=False,
)
