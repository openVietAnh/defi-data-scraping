# defi-scraping

Scraping and Querying Decentralized Finance's Information on the blockchain

# How to update data to current time

- Final data is in csvData/5-minutes-mark
- 5 minutes mark data is calculated from reserveInfo/<token>-full-info.csv
- token-full-info is calculated from token-info and tokenPriceinUSD/token-usd-price
  - token-info is merged from tokenUserCount, depositer, borrower and token_TLV_USD
  - WETH USD price is calculated from usd ETH price
  - other tokens USD price is calculated from token price in ETH
- token_TVL_USD is calculated from token_processed_info
- token_processed_info is calculated from token_raw_info
