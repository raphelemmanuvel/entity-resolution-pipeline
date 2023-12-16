import datetime
from web_crawler.items import CompanyInfoItems


class Parser:
    def __init__(self) -> None:
        """
        Initialize the Parser class.
        """
        pass

    def __normalize_text(self, text):
        """
        Normalize the given text by replacing newline characters and stripping leading/trailing spaces.

        Parameters:
        - text: The text to be normalized.
        """
        return text.replace("\n", " ").replace("\r", "").strip()

    def __snakecase(self, text):
        """
        Convert the given text to snake case by replacing spaces, hyphens, and multiple underscores.

        Parameters:
        - text: The text to be converted to snake case.
        """
        return text.replace(" ", "_").replace("-", "_").replace("___", "_").lower()

    def parse_data(self, company_filing_info, company_meta_info):
        """
        Parse filing information and company meta information, combining them into a structured output.

        Parameters:
        - company_filing_info: The filing information to be parsed.
        - company_meta_info: The meta information about the company.
        """
        filing_info = {
            self.__snakecase(info["LABEL"]): self.__normalize_text(info["VALUE"])
            for info in company_filing_info["DRAWER_DETAIL_LIST"]
        }
        company_meta_info_fmt = {
            self.__snakecase(key): value for key, value in company_meta_info.items()
        }
        company_meta_info_fmt.update(
            {
                "company_id": company_meta_info_fmt.pop("id"),
                "company_name": company_meta_info_fmt["title"][0],
                "retrieved_at": datetime.datetime.now(),  # Add meta-info
            }
        )
        company_info = company_meta_info_fmt | filing_info

        item = CompanyInfoItems()
        item.update(
            {
                field: company_info[field]
                for field in item.fields.keys()
                if field in company_info
            }
        )

        yield item
