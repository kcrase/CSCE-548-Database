import time

from data_provider import DataProvider
from models import Company, ApplicationStatus, StatusType


def main() -> None:
    # CHANGE THESE to match your MySQL setup
    HOST = "localhost"
    USER = "root"
    PASSWORD = ""
    DATABASE = "job_tracker"
    PORT = 3306

    dp = DataProvider(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE,
        port=PORT,
    )

    try:
        # 1) Basic read test (proves connection + SELECT works)
        companies = dp.ReadAllCompanies()
        print("Companies:", len(companies))
        print("First company:", companies[0])

        # 2) ReadByID test
        c1 = dp.ReadCompanyByID(1)
        print("Company #1:", c1)

        # 3) CRUD test on Company (insert -> read -> update -> delete)
        unique_name = f"Test Company {int(time.time())}"
        created = dp.CreateCompany(Company(None, unique_name, "https://test.example.com", "Remote"))
        print("Inserted company_id:", created.company_id)

        updated_company = Company(created.company_id, unique_name, "https://test.example.com", "Austin, TX")
        ok_update = dp.UpdateCompany(updated_company)
        print("UpdateCompany returned:", ok_update)

        fetched = dp.ReadCompanyByID(created.company_id)
        print("Fetched after update:", fetched)

        ok_delete = dp.DeleteCompany(created.company_id)
        print("DeleteCompany returned:", ok_delete)

        # 4) Test ApplicationStatus JOIN reconstruction (proves multi-table mapping works)
        st = dp.ReadApplicationStatusByID(1)
        print("Status #1:")
        print("  status:", st.status)
        print("  company:", st.company.name)
        print("  job:", st.job.job_title)
        print("  application_id:", st.application.application_id)
        print("  contact:", st.contact.full_name if st.contact else None)

        # 5) Test Create/Delete ApplicationStatus (uses existing seeded application/contact)
        app = dp.ReadApplicationByID(1)
        job = dp.ReadJobPostingByID(app.job_id)
        company = dp.ReadCompanyByID(job.company_id)
        contact = dp.ReadContactByID(1)

        new_status = ApplicationStatus(
            company=company,
            contact=contact,
            job=job,
            application=app,
            status_id=None,
            status=StatusType.SCREEN,
        )

        created_status = dp.CreateApplicationStatus(new_status)
        print("Inserted status_id:", created_status.status_id)

        ok_delete_status = dp.DeleteApplicationStatus(created_status.status_id)
        print("Deleted inserted status:", ok_delete_status)

        print("\n✅ Smoke test completed successfully.")

    finally:
        dp.close()


if __name__ == "__main__":
    main()
