# CELE: Social Platform Policy Blog

Scraper's for policy blogs for Meta/Facebook, Twitter/X, and Google.

There are two version of the scraper output:
- Summary: only outputs the metadata for each blog post, including any data available in the top level URL. This version outputs as a CSV by default but can be output as JSON with the `output_json` argument in the `BlogScraper.scrape_data` method.
- Detailed: includes the same data as the summary view and the full text of the blog post. This view outputs as JSON.

To update:

1. Manually download the html source from:
    - https://blog.google/outreach-initiatives/public-policy
    - https://www.facebook.com/formedia/blog
    - https://blog.twitter.com

2. Place outputs in `output/`
3. Run `python run_scrapers.py`. Make sure to edit the parameters in `run_scraper.py` if anything in the websites' HTML changes.

Notes:
- The facebook blog seems to have inconsistent div classes/ids for the main text, so the detailed data version is very noisy

Below is a list for future improvements based on needs.
- Develop online scraping. This currently runs offline, due to differences in lazy loading with each platform
- Incrementally add new blog posts, ignore existing blog posts
- Implement abstract classes formally
- Formal logging
- Export to BigQuery