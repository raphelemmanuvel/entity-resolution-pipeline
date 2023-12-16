import scrapy
from typing import List


def create_company_info_item_class(fields: List[str]) -> type:
    """
    Dynamically create a Scrapy Item class with fields specified in theor order.
    """

    class CompanyItem(scrapy.Item):
        pass

    # Dynamically add fields to the class based on the order
    CompanyItem.fields.update({field_name: scrapy.Field() for field_name in fields})

    return CompanyItem


fields: List[str] = [
    "company_id",
    "company_name",
    "title",
    "owner_name",
    "filing_type",
    "filing_date",
    "record_num",
    "status",
    "standing",
    "alert",
    "can_reinstate",
    "can_file_ar",
    "can_always_file_ar",
    "can_file_reinstatement",
    "standing_ar",
    "standing_ra",
    "standing_other",
    "formed_in",
    "term_of_duration",
    "initial_filing_date",
    "delayed_effective_date",
    "principal_address",
    "mailing_address",
    "ar_due_date",
    "registered_agent",
    "commercial_registered_agent",
    "retrieved_at",
]


CompanyInfoItems: type = create_company_info_item_class(fields)
