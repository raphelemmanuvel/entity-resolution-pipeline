import scrapy
import json
from .parser import Parser
from .helpers.constants import (
    SOURCE_BASE_URL,
    OWNER_STATUS_API_URL,
    FILING_DETAIL_API_BASE_URL,
    DEFAULT_SOURCE_TYPE_ID,
)


class RestSpider(scrapy.Spider):
    """
    Scrapy spider for fetching data from the North Dakota Secretary of State website REST API's.
    """

    name = "rest_spider"

    def __init__(self, search_param: str):
        """
        Initialize the RestSpider with the specified search parameter.

        Parameters:
        - search_param (str): The parameter used for searching active companies.
        """
        super().__init__()
        self.search_param: str = search_param
        self.parser: Parser = Parser()

    def start_requests(self):
        """
        Start the requests by initiating a search for active companies.
        """
        self.logger.info(
            f"Pulling active companies list starting with letter: {self.search_param}..."
        )
        payload = {
            "SEARCH_VALUE": f"{self.search_param}",
            "STARTS_WITH_YN": "true",
            "ACTIVE_ONLY_YN": True,
        }
        yield scrapy.Request(
            url=f"{SOURCE_BASE_URL}/api/Records/businesssearch",
            method="POST",
            body=json.dumps(payload),
            callback=self.handle_active_companies_list,
        )

    def handle_active_companies_list(self, response):
        """
        Retrieve a list of active companies based on the search parameter.

        Parameters:
        - response: The response object containing information about active companies.
        """
        active_companies = response.json().get("rows", {})

        for company_id, company_meta_info in active_companies.items():
            if (
                company_meta_info["TITLE"][0]
                .lower()
                .startswith(self.search_param.lower())
            ):
                payload = {
                    "SOURCE_TYPE_ID": DEFAULT_SOURCE_TYPE_ID,
                    "SOURCE_ID": company_id,
                }

                yield scrapy.Request(
                    url=OWNER_STATUS_API_URL,
                    method="POST",
                    body=json.dumps(payload),
                    meta={
                        "company_id": company_id,
                        "company_meta_info": company_meta_info,
                    },
                    callback=self.handle_owner_status,
                )

    def handle_owner_status(self, response):
        """
        Get owner status and initiate a request to retrieve company filing info.
        """
        owner_status: str = str(response.json()).lower()
        company_id: str = response.meta["company_id"]

        yield scrapy.Request(
            url=f"{FILING_DETAIL_API_BASE_URL}/{company_id}/{owner_status}",
            method="GET",
            meta=response.meta,
            callback=self.retrieve_company_filing_info,
        )

    def retrieve_company_filing_info(self, response):
        """
        Retrieve detailed filing information for a specific company.

        Parameters:
        - response: The response object containing detailed filing information.
        """
        company_filing_info_json, company_meta_info = (
            response.json(),
            response.meta["company_meta_info"],
        )
        yield from self.parser.parse_data(company_filing_info_json, company_meta_info)

    def closed(self, reason):
        """
        Finalize the spider when it is closed.

        Parameters:
        - reason: The reason for closing the spider.
        """
        self.logger.info("Done...")
