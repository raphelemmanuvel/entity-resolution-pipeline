from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CompanyInfoItem:
    company_id: str
    company_name: str
    title: str
    owner_name: str
    filing_type: str
    filing_date: str
    record_num: str
    status: str
    standing: str
    alert: bool
    can_reinstate: bool
    can_file_ar: bool
    can_always_file_ar: bool
    can_file_reinstatement: bool
    standing_ar: str
    standing_ra: str
    standing_other: str
    formed_in: str
    term_of_duration: str
    initial_filing_date: str
    delayed_effective_date: str
    principal_address: str
    mailing_address: str
    ar_due_date: str
    registered_agent: str
    commercial_registered_agent: str
    retrieved_at: datetime
