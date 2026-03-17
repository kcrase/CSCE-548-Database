# tests/test_core.py
import os
import time
import pytest
from typing import Any

from app.data_provider import DataProvider, NotFoundError
from app.business_manager import BusinessManager
from app.models import (
    Company, Contact, JobPosting,
    Application, ApplicationStatus, StatusType,
)

# ── Layer selection ───────────────────────────────────────────────────────────
LAYER_UNDER_TEST = os.environ.get("LAYER", "business").lower()
if LAYER_UNDER_TEST not in {"data", "business"}:
    raise ValueError("LAYER must be 'data' or 'business'")

# ── DB config ─────────────────────────────────────────────────────────────────
DB_HOST     = os.environ.get("DB_HOST",     "localhost")
DB_USER     = os.environ.get("DB_USER",     "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "KeitC4658!")
DB_NAME     = os.environ.get("DB_NAME",     "job_tracker")
DB_PORT     = int(os.environ.get("DB_PORT", "3306"))


def unique_name(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000)}"


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def dp():
    provider = DataProvider(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
        database=DB_NAME, port=DB_PORT,
    )
    try:
        yield provider
    finally:
        try:
            provider.close()
        except Exception:
            pass


@pytest.fixture(scope="module")
def bm(dp):
    return BusinessManager(dp)


# ── Layer Adapter ─────────────────────────────────────────────────────────────

class LayerAdapter:
    def __init__(self, dp: DataProvider, bm: BusinessManager):
        self.dp = dp
        self.bm = bm
        self.layer = LAYER_UNDER_TEST

    def _show(self, action: str, obj_name: str, obj: Any | None):
        print(f"\n[{self.layer.upper()}] {action} {obj_name}")
        if obj is None:
            print("   -> None")
            return
        try:
            attrs = {s: getattr(obj, s) for s in obj.__slots__}
        except AttributeError:
            try:
                attrs = obj.__dict__
            except AttributeError:
                print(f"   -> {obj}")
                return
        keys_first = ["company_id", "contact_id", "job_id", "application_id",
                      "status_id", "company_name", "job_title", "title", "source", "status"]
        for k in keys_first:
            if k in attrs:
                print(f"   {k} = {attrs[k]}")
        for k, v in attrs.items():
            if k not in keys_first:
                print(f"   {k} = {v}")

    # ── Company ───────────────────────────────────────────────────────────────

    def create_company(self, company: Company) -> Company:
        created = self.dp.CreateCompany(company) if self.layer == "data" else self.bm.save_company(company)
        self._show("CREATED", "Company", created)
        return created

    def get_company(self, company_id: int) -> Company | None:
        obj = self.dp.ReadCompanyByID(company_id) if self.layer == "data" else self.bm.get_company_by_id(company_id)
        self._show("READ", "Company", obj)
        return obj

    def update_company(self, company: Company):
        obj = self.dp.UpdateCompany(company) if self.layer == "data" else self.bm.save_company(company)
        self._show("UPDATED", "Company", company)
        return obj

    def delete_company(self, company_id: int):
        self.dp.DeleteCompany(company_id) if self.layer == "data" else self.bm.delete_company(company_id)
        print(f"[{self.layer.upper()}] DELETED Company id={company_id}")

    # ── Contact ───────────────────────────────────────────────────────────────

    def create_contact(self, contact: Contact) -> Contact:
        created = self.dp.CreateContact(contact) if self.layer == "data" else self.bm.save_contact(contact)
        self._show("CREATED", "Contact", created)
        return created

    def get_contact(self, contact_id: int) -> Contact | None:
        obj = self.dp.ReadContactByID(contact_id) if self.layer == "data" else self.bm.get_contact_by_id(contact_id)
        self._show("READ", "Contact", obj)
        return obj

    def update_contact(self, contact: Contact):
        obj = self.dp.UpdateContact(contact) if self.layer == "data" else self.bm.save_contact(contact)
        self._show("UPDATED", "Contact", contact)
        return obj

    def delete_contact(self, contact_id: int):
        self.dp.DeleteContact(contact_id) if self.layer == "data" else self.bm.delete_contact(contact_id)
        print(f"[{self.layer.upper()}] DELETED Contact id={contact_id}")

    # ── JobPosting ────────────────────────────────────────────────────────────

    def create_job(self, job: JobPosting) -> JobPosting:
        created = self.dp.CreateJobPosting(job) if self.layer == "data" else self.bm.save_job_posting(job)
        self._show("CREATED", "JobPosting", created)
        return created

    def get_job(self, job_id: int) -> JobPosting | None:
        obj = self.dp.ReadJobPostingByID(job_id) if self.layer == "data" else self.bm.get_job_posting_by_id(job_id)
        self._show("READ", "JobPosting", obj)
        return obj

    def update_job(self, job: JobPosting):
        obj = self.dp.UpdateJobPosting(job) if self.layer == "data" else self.bm.save_job_posting(job)
        self._show("UPDATED", "JobPosting", job)
        return obj

    def delete_job(self, job_id: int):
        self.dp.DeleteJobPosting(job_id) if self.layer == "data" else self.bm.delete_job_posting(job_id)
        print(f"[{self.layer.upper()}] DELETED JobPosting id={job_id}")

    # ── Application ───────────────────────────────────────────────────────────

    def create_application(self, application: Application) -> Application:
        created = self.dp.CreateApplication(application) if self.layer == "data" else self.bm.save_application(application)
        self._show("CREATED", "Application", created)
        return created

    def get_application(self, application_id: int) -> Application | None:
        obj = self.dp.ReadApplicationByID(application_id) if self.layer == "data" else self.bm.get_application_by_id(application_id)
        self._show("READ", "Application", obj)
        return obj

    def update_application(self, application: Application):
        obj = self.dp.UpdateApplication(application) if self.layer == "data" else self.bm.save_application(application)
        self._show("UPDATED", "Application", application)
        return obj

    def delete_application(self, application_id: int):
        self.dp.DeleteApplication(application_id) if self.layer == "data" else self.bm.delete_application(application_id)
        print(f"[{self.layer.upper()}] DELETED Application id={application_id}")

    # ── ApplicationStatus ─────────────────────────────────────────────────────

    def create_status(self, status: ApplicationStatus) -> ApplicationStatus:
        created = self.dp.CreateApplicationStatus(status) if self.layer == "data" else self.bm.save_application_status(status)
        self._show("CREATED", "ApplicationStatus", created)
        return created

    def get_status(self, status_id: int) -> ApplicationStatus | None:
        obj = self.dp.ReadApplicationStatusByID(status_id) if self.layer == "data" else self.bm.get_application_status_by_id(status_id)
        self._show("READ", "ApplicationStatus", obj)
        return obj

    def update_status(self, status: ApplicationStatus):
        obj = self.dp.UpdateApplicationStatus(status) if self.layer == "data" else self.bm.save_application_status(status)
        self._show("UPDATED", "ApplicationStatus", status)
        return obj

    def delete_status(self, status_id: int):
        self.dp.DeleteApplicationStatus(status_id) if self.layer == "data" else self.bm.delete_application_status(status_id)
        print(f"[{self.layer.upper()}] DELETED ApplicationStatus id={status_id}")


# ── Adapter fixture ───────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def adapter(dp, bm):
    return LayerAdapter(dp, bm)


# ── Seed helpers ──────────────────────────────────────────────────────────────

def seed_company(adapter: LayerAdapter) -> Company:
    return adapter.create_company(Company(None, unique_name("SeedCo"), "https://seed.example", "Remote"))

def seed_contact(adapter: LayerAdapter, company_id: int) -> Contact:
    return adapter.create_contact(Contact(None, company_id, unique_name("SeedContact"), "Engineer", "c@example.com", "555-5555", None))

def seed_job(adapter: LayerAdapter, company_id: int) -> JobPosting:
    return adapter.create_job(JobPosting(None, company_id, unique_name("SeedJob"), "Remote", "Full-time", "https://job.example", None, None))

def seed_application(adapter: LayerAdapter, job_id: int) -> Application:
    return adapter.create_application(Application(None, job_id, None, "LinkedIn", 5, None))

def seed_status(adapter: LayerAdapter, company: Company, job: JobPosting,
                application: Application, contact: Contact | None) -> ApplicationStatus:
    return adapter.create_status(ApplicationStatus(
        company=company, contact=contact, job=job,
        application=application, status_id=None, status=StatusType.SAVED,
    ))


# ── CRUD Tests ────────────────────────────────────────────────────────────────

class TestFullCRUDAllDomains:

    def test_company_crud(self, adapter: LayerAdapter):
        print("\n========== COMPANY CRUD ==========")
        c = adapter.create_company(Company(None, unique_name("TestCo"), "https://test.com", "Remote"))
        adapter.get_company(c.company_id)
        c.company_location = "UpdatedLocation"
        adapter.update_company(c)
        adapter.get_company(c.company_id)
        adapter.delete_company(c.company_id)
        assert adapter.get_company(c.company_id) is None
        with pytest.raises(NotFoundError):
            adapter.delete_company(c.company_id)

    def test_contact_crud(self, adapter: LayerAdapter):
        print("\n========== CONTACT CRUD ==========")
        comp = seed_company(adapter)
        contact = seed_contact(adapter, comp.company_id)
        adapter.get_contact(contact.contact_id)
        contact.title = "UpdatedTitle"
        adapter.update_contact(contact)
        adapter.get_contact(contact.contact_id)
        adapter.delete_contact(contact.contact_id)
        assert adapter.get_contact(contact.contact_id) is None
        with pytest.raises(NotFoundError):
            adapter.delete_contact(contact.contact_id)

    def test_job_posting_crud(self, adapter: LayerAdapter):
        print("\n========== JOB POSTING CRUD ==========")
        comp = seed_company(adapter)
        job = seed_job(adapter, comp.company_id)
        adapter.get_job(job.job_id)
        job.job_title = "UpdatedJob"
        adapter.update_job(job)
        adapter.get_job(job.job_id)
        adapter.delete_job(job.job_id)
        assert adapter.get_job(job.job_id) is None
        with pytest.raises(NotFoundError):
            adapter.delete_job(job.job_id)

    def test_application_crud(self, adapter: LayerAdapter):
        print("\n========== APPLICATION CRUD ==========")
        comp = seed_company(adapter)
        job = seed_job(adapter, comp.company_id)
        app = seed_application(adapter, job.job_id)
        adapter.get_application(app.application_id)
        app.source = "UpdatedSource"
        adapter.update_application(app)
        adapter.get_application(app.application_id)
        adapter.delete_application(app.application_id)
        assert adapter.get_application(app.application_id) is None
        with pytest.raises(NotFoundError):
            adapter.delete_application(app.application_id)

    def test_application_status_crud(self, adapter: LayerAdapter):
        print("\n========== APPLICATION STATUS CRUD ==========")
        comp    = seed_company(adapter)
        contact = seed_contact(adapter, comp.company_id)
        job     = seed_job(adapter, comp.company_id)
        app     = seed_application(adapter, job.job_id)
        status  = seed_status(adapter, comp, job, app, contact)
        adapter.get_status(status.status_id)
        status.status = StatusType.INTERVIEW
        adapter.update_status(status)
        adapter.get_status(status.status_id)
        new_status = adapter.create_status(
            ApplicationStatus(company=comp, contact=None, job=job,
                              application=app, status_id=None, status=StatusType.SCREEN)
        )
        adapter.delete_status(new_status.status_id)
        assert adapter.get_status(new_status.status_id) is None
        with pytest.raises(NotFoundError):
            adapter.delete_status(new_status.status_id)
