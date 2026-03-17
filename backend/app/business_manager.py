# app/business_manager.py
from typing import Optional, List

from app.data_provider import DataProvider
from app.models import Company, Contact, JobPosting, Application, ApplicationStatus


def _is_new(val: Optional[int]) -> bool:
    return val is None or val == 0


class BusinessManager:
    def __init__(self, provider: DataProvider):
        self._dp = provider

    # ── Company ───────────────────────────────────────────────────────────────

    def save_company(self, company: Company) -> Company:
        if _is_new(company.company_id):
            return self._dp.CreateCompany(company)
        self._dp.UpdateCompany(company)
        return company

    def delete_company(self, company_id: int) -> None:
        self._dp.DeleteCompany(company_id)

    def get_company_by_id(self, company_id: int) -> Optional[Company]:
        return self._dp.ReadCompanyByID(company_id)

    def get_all_companies(self) -> List[Company]:
        return self._dp.ReadAllCompanies()

    # ── Contact ───────────────────────────────────────────────────────────────

    def save_contact(self, contact: Contact) -> Contact:
        if _is_new(contact.contact_id):
            return self._dp.CreateContact(contact)
        self._dp.UpdateContact(contact)
        return contact

    def delete_contact(self, contact_id: int) -> None:
        self._dp.DeleteContact(contact_id)

    def get_contact_by_id(self, contact_id: int) -> Optional[Contact]:
        return self._dp.ReadContactByID(contact_id)

    def get_all_contacts(self) -> List[Contact]:
        return self._dp.ReadAllContacts()

    # ── JobPosting ────────────────────────────────────────────────────────────

    def save_job_posting(self, job: JobPosting) -> JobPosting:
        if _is_new(job.job_id):
            return self._dp.CreateJobPosting(job)
        self._dp.UpdateJobPosting(job)
        return job

    def delete_job_posting(self, job_id: int) -> None:
        self._dp.DeleteJobPosting(job_id)

    def get_job_posting_by_id(self, job_id: int) -> Optional[JobPosting]:
        return self._dp.ReadJobPostingByID(job_id)

    def get_all_job_postings(self) -> List[JobPosting]:
        return self._dp.ReadAllJobPostings()

    # ── Application ───────────────────────────────────────────────────────────

    def save_application(self, app: Application) -> Application:
        if _is_new(app.application_id):
            return self._dp.CreateApplication(app)
        self._dp.UpdateApplication(app)
        return app

    def delete_application(self, application_id: int) -> None:
        self._dp.DeleteApplication(application_id)

    def get_application_by_id(self, application_id: int) -> Optional[Application]:
        return self._dp.ReadApplicationByID(application_id)

    def get_all_applications(self) -> List[Application]:
        return self._dp.ReadAllApplications()

    # ── ApplicationStatus ─────────────────────────────────────────────────────

    def save_application_status(self, status: ApplicationStatus) -> ApplicationStatus:
        if _is_new(status.status_id):
            return self._dp.CreateApplicationStatus(status)
        self._dp.UpdateApplicationStatus(status)
        return status

    def delete_application_status(self, status_id: int) -> None:
        self._dp.DeleteApplicationStatus(status_id)

    def get_application_status_by_id(self, status_id: int) -> Optional[ApplicationStatus]:
        return self._dp.ReadApplicationStatusByID(status_id)

    def get_all_application_statuses(self) -> List[ApplicationStatus]:
        return self._dp.ReadAllApplicationStatuses()
