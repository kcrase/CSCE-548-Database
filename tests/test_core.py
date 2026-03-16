# tests/test_core.py
import os
import time
import pytest
from typing import Any

from data_provider import DataProvider, NotFoundError
from business_manager import BusinessManager
from models import (
    Company,
    Contact,
    JobPosting,
    Application,
    ApplicationStatus,
    StatusType,
)

# -------------------------------------------------
# LAYER SELECTION (data or business only)
# -------------------------------------------------
LAYER_UNDER_TEST = os.environ.get("LAYER", "business").lower()
if LAYER_UNDER_TEST not in {"data", "business"}:
    raise ValueError("LAYER must be 'data' or 'business'")

# -------------------------------------------------
# DATABASE CONFIG
# -------------------------------------------------
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "KeitC4658!")
DB_NAME = os.environ.get("DB_NAME", "job_tracker")
DB_PORT = int(os.environ.get("DB_PORT", "3306"))


def unique_name(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000)}"


# -------------------------------------------------
# FIXTURES
# -------------------------------------------------
@pytest.fixture(scope="module")
def dp():
    dp = DataProvider(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
    )
    try:
        yield dp
    finally:
        try:
            dp.close()
        except Exception:
            pass


@pytest.fixture(scope="module")
def bm(dp):
    return BusinessManager(dp)


# -------------------------------------------------
# LAYER ADAPTER (with SAFE PRINTING)
# -------------------------------------------------
class LayerAdapter:
    def __init__(self, dp: DataProvider, bm: BusinessManager):
        self.dp = dp
        self.bm = bm
        self.layer = LAYER_UNDER_TEST

    # SAFE OBJECT PRINTING
    def _show(self, action: str, obj_name: str, obj: Any | None):
        print(f"\n[{self.layer.upper()}] {action} {obj_name}")

        if obj is None:
            print("   -> None")
            return

        # Try __dict__ first
        try:
            attrs = obj.__dict__
        except AttributeError:
            # Fallback for slotted or unusual objects
            try:
                attrs = {
                    attr: getattr(obj, attr)
                    for attr in dir(obj)
                    if not attr.startswith("_")
                    and not callable(getattr(obj, attr))
                }
            except Exception:
                print(f"   -> {obj}")
                return

        # Print key / identifying fields first, then others
        # (keeps output readable)
        keys_first = ["company_id", "contact_id", "job_id", "application_id", "status_id",
                      "company_name", "job_title", "title", "source", "status"]
        for k in keys_first:
            if k in attrs:
                print(f"   {k} = {attrs[k]}")
        for k, v in attrs.items():
            if k not in keys_first:
                print(f"   {k} = {v}")

    # -------------------------
    # COMPANY
    # -------------------------
    def create_company(self, company: Company) -> Company:
        if self.layer == "data":
            created = self.dp.CreateCompany(company)
        else:
            created = self.bm.save_company(company)
        self._show("CREATED", "Company", created)
        return created

    def get_company(self, company_id: int) -> Company | None:
        if self.layer == "data":
            obj = self.dp.ReadCompanyByID(company_id)
        else:
            obj = self.bm.get_company_by_id(company_id)
        self._show("READ", "Company", obj)
        return obj

    def update_company(self, company: Company):
        if self.layer == "data":
            obj = self.dp.UpdateCompany(company)
        else:
            obj = self.bm.save_company(company)
        self._show("UPDATED", "Company", company)
        return obj

    def delete_company(self, company_id: int):
        if self.layer == "data":
            self.dp.DeleteCompany(company_id)
        else:
            self.bm.delete_company(company_id)
        print(f"[{self.layer.upper()}] DELETED Company id={company_id}")

    # -------------------------
    # CONTACT
    # -------------------------
    def create_contact(self, contact: Contact) -> Contact:
        if self.layer == "data":
            created = self.dp.CreateContact(contact)
        else:
            created = self.bm.save_contact(contact)
        self._show("CREATED", "Contact", created)
        return created

    def get_contact(self, contact_id: int) -> Contact | None:
        if self.layer == "data":
            obj = self.dp.ReadContactByID(contact_id)
        else:
            obj = self.bm.get_contact_by_id(contact_id)
        self._show("READ", "Contact", obj)
        return obj

    def update_contact(self, contact: Contact):
        if self.layer == "data":
            obj = self.dp.UpdateContact(contact)
        else:
            obj = self.bm.save_contact(contact)
        self._show("UPDATED", "Contact", contact)
        return obj

    def delete_contact(self, contact_id: int):
        if self.layer == "data":
            self.dp.DeleteContact(contact_id)
        else:
            self.bm.delete_contact(contact_id)
        print(f"[{self.layer.upper()}] DELETED Contact id={contact_id}")

    # -------------------------
    # JOB POSTING
    # -------------------------
    def create_job(self, job: JobPosting) -> JobPosting:
        if self.layer == "data":
            created = self.dp.CreateJobPosting(job)
        else:
            created = self.bm.save_job_posting(job)
        self._show("CREATED", "JobPosting", created)
        return created

    def get_job(self, job_id: int) -> JobPosting | None:
        if self.layer == "data":
            obj = self.dp.ReadJobPostingByID(job_id)
        else:
            obj = self.bm.get_job_posting_by_id(job_id)
        self._show("READ", "JobPosting", obj)
        return obj

    def update_job(self, job: JobPosting):
        if self.layer == "data":
            obj = self.dp.UpdateJobPosting(job)
        else:
            obj = self.bm.save_job_posting(job)
        self._show("UPDATED", "JobPosting", job)
        return obj

    def delete_job(self, job_id: int):
        if self.layer == "data":
            self.dp.DeleteJobPosting(job_id)
        else:
            self.bm.delete_job_posting(job_id)
        print(f"[{self.layer.upper()}] DELETED JobPosting id={job_id}")

    # -------------------------
    # APPLICATION
    # -------------------------
    def create_application(self, application: Application) -> Application:
        if self.layer == "data":
            created = self.dp.CreateApplication(application)
        else:
            created = self.bm.save_application(application)
        self._show("CREATED", "Application", created)
        return created

    def get_application(self, application_id: int) -> Application | None:
        if self.layer == "data":
            obj = self.dp.ReadApplicationByID(application_id)
        else:
            obj = self.bm.get_application_by_id(application_id)
        self._show("READ", "Application", obj)
        return obj

    def update_application(self, application: Application):
        if self.layer == "data":
            obj = self.dp.UpdateApplication(application)
        else:
            obj = self.bm.save_application(application)
        self._show("UPDATED", "Application", application)
        return obj

    def delete_application(self, application_id: int):
        if self.layer == "data":
            self.dp.DeleteApplication(application_id)
        else:
            self.bm.delete_application(application_id)
        print(f"[{self.layer.upper()}] DELETED Application id={application_id}")

    # -------------------------
    # APPLICATION STATUS
    # -------------------------
    def create_status(self, status: ApplicationStatus) -> ApplicationStatus:
        if self.layer == "data":
            created = self.dp.CreateApplicationStatus(status)
        else:
            created = self.bm.save_application_status(status)
        self._show("CREATED", "ApplicationStatus", created)
        return created

    def get_status(self, status_id: int) -> ApplicationStatus | None:
        if self.layer == "data":
            obj = self.dp.ReadApplicationStatusByID(status_id)
        else:
            obj = self.bm.get_application_status_by_id(status_id)
        self._show("READ", "ApplicationStatus", obj)
        return obj

    def update_status(self, status: ApplicationStatus):
        if self.layer == "data":
            obj = self.dp.UpdateApplicationStatus(status)
        else:
            obj = self.bm.save_application_status(status)
        self._show("UPDATED", "ApplicationStatus", status)
        return obj

    def delete_status(self, status_id: int):
        if self.layer == "data":
            self.dp.DeleteApplicationStatus(status_id)
        else:
            self.bm.delete_application_status(status_id)
        print(f"[{self.layer.upper()}] DELETED ApplicationStatus id={status_id}")


# -------------------------------------------------
# ADAPTER FIXTURE
# -------------------------------------------------
@pytest.fixture(scope="module")
def adapter(dp, bm):
    return LayerAdapter(dp, bm)


# -------------------------------------------------
# HELPER SEED FUNCTIONS (use adapter)
# -------------------------------------------------
def seed_company(adapter: LayerAdapter) -> Company:
    c = Company(None, unique_name("SeedCo"), "https://seed.example", "Remote")
    return adapter.create_company(c)


def seed_contact(adapter: LayerAdapter, company_id: int) -> Contact:
    ct = Contact(None, company_id, unique_name("SeedContact"), "Engineer", "c@example.com", "555-5555", None)
    return adapter.create_contact(ct)


def seed_job(adapter: LayerAdapter, company_id: int) -> JobPosting:
    j = JobPosting(None, company_id, unique_name("SeedJob"), "Remote", "Full-time", "https://job.example", None, None)
    return adapter.create_job(j)


def seed_application(adapter: LayerAdapter, job_id: int) -> Application:
    a = Application(None, job_id, None, "LinkedIn", 5, None)
    return adapter.create_application(a)


def seed_status(adapter: LayerAdapter, company: Company, job: JobPosting, application: Application, contact: Contact | None) -> ApplicationStatus:
    status = ApplicationStatus(
        company=company,
        contact=contact,
        job=job,
        application=application,
        status_id=None,
        status=StatusType.SAVED,
    )
    return adapter.create_status(status)


# -------------------------------------------------
# CRUD TESTS
# -------------------------------------------------
class TestFullCRUDAllDomains:
    def test_company_crud(self, adapter: LayerAdapter):
        print("\n========== COMPANY CRUD ==========")
        c = adapter.create_company(
            Company(None, unique_name("TestCo"), "https://test.com", "Remote")
        )
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
        comp = seed_company(adapter)
        contact = seed_contact(adapter, comp.company_id)
        job = seed_job(adapter, comp.company_id)
        app = seed_application(adapter, job.job_id)

        status = seed_status(adapter, comp, job, app, contact)
        adapter.get_status(status.status_id)

        status.status = StatusType.INTERVIEW
        adapter.update_status(status)
        adapter.get_status(status.status_id)

        # create another status and delete it
        new_status = ApplicationStatus(company=comp, contact=None, job=job, application=app, status_id=None, status=StatusType.SCREEN)
        created_new = adapter.create_status(new_status)
        adapter.delete_status(created_new.status_id)
        assert adapter.get_status(created_new.status_id) is None

        with pytest.raises(NotFoundError):
            adapter.delete_status(created_new.status_id)