# read_test.py
from __future__ import annotations

from typing import Iterable, Optional

from data_provider import DataProvider
from models import ApplicationStatus


# ---------------------------
# Configuration (EDIT THESE)
# ---------------------------
HOST = "localhost"
USER = "root"
PASSWORD = ""
DATABASE = "job_tracker"
PORT = 3306

# If True, prints ALL rows for each table.
# WARNING: This can be a lot of output (especially application_status).
PRINT_ALL_ROWS = True

# If PRINT_ALL_ROWS is False, this controls how many rows to print per table.
MAX_ROWS_WHEN_LIMITED = 10


# ---------------------------
# Printing helpers
# ---------------------------
def print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def print_records(
    title: str,
    records: list[object],
    *,
    limit: Optional[int] = None
) -> None:
    print_header(f"{title} — {len(records)} row(s)")
    if not records:
        print("(no rows)")
        return

    to_print = records if limit is None else records[:limit]
    for r in to_print:
        print(r)

    if limit is not None and len(records) > limit:
        print(f"... ({len(records) - limit} more not shown)")


def print_status_records(
    title: str,
    statuses: list[ApplicationStatus],
    *,
    limit: Optional[int] = None
) -> None:
    """
    ApplicationStatus objects contain nested objects (company/contact/job/application).
    Printing them raw can get noisy, so this prints a clean summary line per status.
    """
    print_header(f"{title} — {len(statuses)} row(s)")
    if not statuses:
        print("(no rows)")
        return

    to_print = statuses if limit is None else statuses[:limit]
    for s in to_print:
        contact_name = s.contact.full_name if s.contact else "None"
        print(
            f"status_id={s.status_id} | status={s.status.value} | "
            f"company={s.company.name} | job={s.job.job_title} | "
            f"application_id={s.application.application_id} | contact={contact_name}"
        )

    if limit is not None and len(statuses) > limit:
        print(f"... ({len(statuses) - limit} more not shown)")


def main() -> None:
    limit = None if PRINT_ALL_ROWS else MAX_ROWS_WHEN_LIMITED

    with DataProvider(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE,
        port=PORT,
    ) as dp:
        # ---------------------------
        # Read ALL rows from each table
        # ---------------------------
        companies = dp.ReadAllCompanies()
        contacts = dp.ReadAllContacts()
        jobs = dp.ReadAllJobPostings()
        applications = dp.ReadAllApplications()
        statuses = dp.ReadAllApplicationStatuses()

        print_records("COMPANY (ReadAllCompanies)", companies, limit=limit)
        print_records("CONTACT (ReadAllContacts)", contacts, limit=limit)
        print_records("JOB_POSTING (ReadAllJobPostings)", jobs, limit=limit)
        print_records("APPLICATION (ReadAllApplications)", applications, limit=limit)
        print_status_records("APPLICATION_STATUS (ReadAllApplicationStatuses)", statuses, limit=limit)

        # ---------------------------
        # Read ONE instance from each table (by ID)
        # Picks the first row's ID from each list to avoid assuming IDs exist.
        # ---------------------------
        print_header("ONE RECORD BY ID FROM EACH TABLE")

        if companies:
            one_company_id = companies[0].company_id
            one_company = dp.ReadCompanyByID(one_company_id)
            print("Company by ID:", one_company)

        if contacts:
            one_contact_id = contacts[0].contact_id
            one_contact = dp.ReadContactByID(one_contact_id)
            print("Contact by ID:", one_contact)

        if jobs:
            one_job_id = jobs[0].job_id
            one_job = dp.ReadJobPostingByID(one_job_id)
            print("JobPosting by ID:", one_job)

        if applications:
            one_application_id = applications[0].application_id
            one_application = dp.ReadApplicationByID(one_application_id)
            print("Application by ID:", one_application)

        if statuses:
            one_status_id = statuses[0].status_id
            one_status = dp.ReadApplicationStatusByID(one_status_id)
            print("\nApplicationStatus by ID (expanded objects):")
            if one_status is None:
                print("None (not found)")
            else:
                print("  status_id:", one_status.status_id)
                print("  status:", one_status.status.value)
                print("  company:", one_status.company)
                print("  job:", one_status.job)
                print("  application:", one_status.application)
                print("  contact:", one_status.contact)

        print_header("✅ READ TEST COMPLETE")


if __name__ == "__main__":
    main()
