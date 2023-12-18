import datetime
from web_crawler.items import CompanyInfoItem


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

    def parse_data(self, filing_info_data, meta_info_data):
        """
        Parse filing information and company meta information, combining them into a structured output.

        Parameters:
        - company_filing_info: The filing information to be parsed.
        - company_meta_info: The meta information about the company.
        """
        filing_info = {
            self.__snakecase(info["LABEL"]): self.__normalize_text(info["VALUE"])
            for info in filing_info_data["DRAWER_DETAIL_LIST"]
        }
        meta_info_formatted = {
            self.__snakecase(key): value for key, value in meta_info_data.items()
        }
        meta_info_formatted.update(
            {
                "company_id": meta_info_formatted.pop("id"),
                "company_name": meta_info_formatted["title"][0],
                "retrieved_at": datetime.datetime.now(),  # Add meta-info
            }
        )

        combined_info = meta_info_formatted | filing_info

        # Ensure all fields are present in parsed_data with default values of None
        parsed_data = {
            key: combined_info.get(key, None)
            for key in CompanyInfoItem.__annotations__.keys()
        }

        yield CompanyInfoItem(**parsed_data)
