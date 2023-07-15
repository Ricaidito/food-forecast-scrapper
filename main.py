from scrapper import ProductScrapper


ProductScrapper().do_scraping(
    micm=True,
    sirena=True,
    jumbo=True,
    nacional=False,
    upload_to_db=True,
)
