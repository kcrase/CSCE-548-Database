# demo.py
# Unified demo — runs a full Create -> Read -> Update -> Read -> GetAll cycle
# for every domain object through whichever layer is selected.
#
# Usage:
#   LAYER=data     python demo.py   <- calls DataProvider directly
#   LAYER=business python demo.py   <- calls BusinessManager
#   LAYER=service  python demo.py   <- calls the running FastAPI service via HTTP
#
# Windows:
#   set LAYER=data     && python demo.py
#   set LAYER=business && python demo.py
#   set LAYER=service  && python demo.py
#
# For LAYER=service the API must already be running:
#   uvicorn main:app --reload --host 0.0.0.0 --port 8000
#
# Override the API base URL with:
#   set API_BASE=http://localhost:8000
#
# All test records are tagged [TEST] <LAYER> <RUN_ID> so every run is
# identifiable in the database and in screenshots.
# Only ApplicationStatus rows are deleted at the end; all other records
# are intentionally left in the database for visual verification.

from __future__ import annotations
import os
import sys
import time
import json
import requests
from typing import Optional

from app.data_provider import DataProvider, NotFoundError
from app.business_manager import BusinessManager
from app.models import (
    Application, ApplicationStatus, Company,
    Contact, JobPosting, StatusType,
)

# ── Layer selection ───────────────────────────────────────────────────────────
LAYER = os.environ.get("LAYER", "business").lower()
if LAYER not in {"data", "business", "service"}:
    print("ERROR: LAYER must be 'data', 'business', or 'service'")
    sys.exit(1)

API_BASE = os.environ.get("API_BASE", "http://localhost:8000").rstrip("/")

# ── DB connection settings (used by data / business layers only) ──────────────
DB_HOST     = os.environ.get("DB_HOST",     "localhost")
DB_USER     = os.environ.get("DB_USER",     "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "KeitC4658!")
DB_NAME     = os.environ.get("DB_NAME",     "job_tracker")
DB_PORT     = int(os.environ.get("DB_PORT", "3306"))

RUN_ID = str(int(time.time()))
W = 68


# ════════════════════════════════════════════════════════════════════════════
# Output helpers
# ════════════════════════════════════════════════════════════════════════════

def section(title: str):
    print(f"\n{'=' * W}")
    print(f"  {title}")
    print('=' * W)


def step(title: str):
    print(f"\n  -- {title}")


def show(tag: str, obj):
    """Pretty-print a domain object (slotted dataclass) or a dict (service layer)."""
    if obj is None:
        print(f"    [{tag}]  ->  None")
        return
    print(f"    [{tag}]")
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, dict):
                # Expand nested dict fully instead of just showing the id
                print(f"        {k:<26} =")
                for nk, nv in v.items():
                    print(f"            {nk:<22} = {nv!r}")
            else:
                print(f"        {k:<26} = {v!r}")
    else:
        try:
            fields = {s: getattr(obj, s) for s in obj.__slots__}
        except AttributeError:
            fields = vars(obj)
        for k, v in fields.items():
            if hasattr(v, "__slots__"):
                # Expand nested domain object fully instead of just showing the id
                print(f"        {k:<26} =")
                try:
                    inner_fields = {s: getattr(v, s) for s in v.__slots__}
                except AttributeError:
                    inner_fields = vars(v)
                for nk, nv in inner_fields.items():
                    print(f"            {nk:<22} = {nv!r}")
            else:
                print(f"        {k:<26} = {v!r}")


def ok(msg: str):
    print(f"    OK  {msg}")


# ════════════════════════════════════════════════════════════════════════════
# Layer Adapter
# Wraps all three layers behind one identical interface so the demo
# functions never need to know which layer they are talking to.
# ════════════════════════════════════════════════════════════════════════════

class LayerAdapter:
    def __init__(self, dp: Optional[DataProvider], bm: Optional[BusinessManager]):
        self.dp = dp
        self.bm = bm

    # ── HTTP helpers (service layer only) ─────────────────────────────────────

    def _post(self, path: str, body: dict) -> dict:
        r = requests.post(f"{API_BASE}{path}", json=body)
        r.raise_for_status()
        return r.json()

    def _get(self, path: str):
        r = requests.get(f"{API_BASE}{path}")
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()

    def _put(self, path: str, body: dict) -> dict:
        r = requests.put(f"{API_BASE}{path}", json=body)
        r.raise_for_status()
        return r.json()

    def _delete(self, path: str):
        r = requests.delete(f"{API_BASE}{path}")
        if r.status_code == 404:
            raise NotFoundError(f"DELETE {path} -> 404")
        r.raise_for_status()

    # ── ID helper — works for both domain objects and dicts ───────────────────

    @staticmethod
    def _id(obj, field: str):
        return obj[field] if isinstance(obj, dict) else getattr(obj, field)

    # ════════════════════════════════════════════════════════════════════════
    # COMPANY
    # ════════════════════════════════════════════════════════════════════════

    def create_company(self, name, website, location):
        if LAYER == "data":
            return self.dp.CreateCompany(Company(None, name, website, location))
        if LAYER == "business":
            return self.bm.save_company(Company(None, name, website, location))
        return self._post("/api/companies", {
            "name": name, "website": website, "company_location": location,
        })

    def get_company(self, company_id: int):
        if LAYER == "data":     return self.dp.ReadCompanyByID(company_id)
        if LAYER == "business": return self.bm.get_company_by_id(company_id)
        return self._get(f"/api/companies/{company_id}")

    def update_company(self, obj, *, website=None, location=None):
        cid      = self._id(obj, "company_id")
        name     = obj["name"]            if isinstance(obj, dict) else obj.name
        website  = website  or (obj["website"]          if isinstance(obj, dict) else obj.website)
        location = location or (obj["company_location"] if isinstance(obj, dict) else obj.company_location)
        if LAYER == "data":
            c = self.dp.ReadCompanyByID(cid)
            c.company_location = location
            c.website = website
            self.dp.UpdateCompany(c)
            return self.dp.ReadCompanyByID(cid)
        if LAYER == "business":
            c = self.bm.get_company_by_id(cid)
            c.company_location = location
            c.website = website
            return self.bm.save_company(c)
        return self._put(f"/api/companies/{cid}", {
            "name": name, "website": website, "company_location": location,
        })

    def get_all_companies(self):
        if LAYER == "data":     return self.dp.ReadAllCompanies()
        if LAYER == "business": return self.bm.get_all_companies()
        return self._get("/api/companies")

    # ════════════════════════════════════════════════════════════════════════
    # CONTACT
    # ════════════════════════════════════════════════════════════════════════

    def create_contact(self, company_id, full_name, title, email, phone):
        if LAYER == "data":
            return self.dp.CreateContact(Contact(None, company_id, full_name, title, email, phone, None))
        if LAYER == "business":
            return self.bm.save_contact(Contact(None, company_id, full_name, title, email, phone, None))
        return self._post("/api/contacts", {
            "company_id": company_id, "full_name": full_name,
            "title": title, "email": email, "phone": phone, "linkedin": None,
        })

    def get_contact(self, contact_id: int):
        if LAYER == "data":     return self.dp.ReadContactByID(contact_id)
        if LAYER == "business": return self.bm.get_contact_by_id(contact_id)
        return self._get(f"/api/contacts/{contact_id}")

    def update_contact(self, obj, *, title=None, phone=None):
        ctid       = self._id(obj, "contact_id")
        company_id = obj["company_id"] if isinstance(obj, dict) else obj.company_id
        full_name  = obj["full_name"]  if isinstance(obj, dict) else obj.full_name
        email      = obj["email"]      if isinstance(obj, dict) else obj.email
        linkedin   = obj.get("linkedin") if isinstance(obj, dict) else obj.linkedin
        title      = title or (obj["title"] if isinstance(obj, dict) else obj.title)
        phone      = phone or (obj["phone"] if isinstance(obj, dict) else obj.phone)
        if LAYER == "data":
            c = self.dp.ReadContactByID(ctid)
            c.title = title
            c.phone = phone
            self.dp.UpdateContact(c)
            return self.dp.ReadContactByID(ctid)
        if LAYER == "business":
            c = self.bm.get_contact_by_id(ctid)
            c.title = title
            c.phone = phone
            return self.bm.save_contact(c)
        return self._put(f"/api/contacts/{ctid}", {
            "company_id": company_id, "full_name": full_name,
            "title": title, "email": email, "phone": phone, "linkedin": linkedin,
        })

    def get_all_contacts(self):
        if LAYER == "data":     return self.dp.ReadAllContacts()
        if LAYER == "business": return self.bm.get_all_contacts()
        return self._get("/api/contacts")

    # ════════════════════════════════════════════════════════════════════════
    # JOB POSTING
    # ════════════════════════════════════════════════════════════════════════

    def create_job(self, company_id, job_title, job_location, employment_type, job_url):
        if LAYER == "data":
            return self.dp.CreateJobPosting(
                JobPosting(None, company_id, job_title, job_location, employment_type, job_url, None, None))
        if LAYER == "business":
            return self.bm.save_job_posting(
                JobPosting(None, company_id, job_title, job_location, employment_type, job_url, None, None))
        return self._post("/api/job-postings", {
            "company_id": company_id, "job_title": job_title,
            "job_location": job_location, "employment_type": employment_type,
            "job_url": job_url, "salary": None, "posted_date": None,
        })

    def get_job(self, job_id: int):
        if LAYER == "data":     return self.dp.ReadJobPostingByID(job_id)
        if LAYER == "business": return self.bm.get_job_posting_by_id(job_id)
        return self._get(f"/api/job-postings/{job_id}")

    def update_job(self, obj, *, employment_type=None, job_location=None):
        jid            = self._id(obj, "job_id")
        company_id     = obj["company_id"]     if isinstance(obj, dict) else obj.company_id
        job_title      = obj["job_title"]      if isinstance(obj, dict) else obj.job_title
        job_url        = obj["job_url"]        if isinstance(obj, dict) else obj.job_url
        job_location   = job_location   or (obj["job_location"]   if isinstance(obj, dict) else obj.job_location)
        employment_type = employment_type or (obj["employment_type"] if isinstance(obj, dict) else obj.employment_type)
        if LAYER == "data":
            j = self.dp.ReadJobPostingByID(jid)
            j.employment_type = employment_type
            j.job_location = job_location
            self.dp.UpdateJobPosting(j)
            return self.dp.ReadJobPostingByID(jid)
        if LAYER == "business":
            j = self.bm.get_job_posting_by_id(jid)
            j.employment_type = employment_type
            j.job_location = job_location
            return self.bm.save_job_posting(j)
        return self._put(f"/api/job-postings/{jid}", {
            "company_id": company_id, "job_title": job_title,
            "job_location": job_location, "employment_type": employment_type,
            "job_url": job_url, "salary": None, "posted_date": None,
        })

    def get_all_jobs(self):
        if LAYER == "data":     return self.dp.ReadAllJobPostings()
        if LAYER == "business": return self.bm.get_all_job_postings()
        return self._get("/api/job-postings")

    # ════════════════════════════════════════════════════════════════════════
    # APPLICATION
    # ════════════════════════════════════════════════════════════════════════

    def create_application(self, job_id, source, priority):
        if LAYER == "data":
            return self.dp.CreateApplication(Application(None, job_id, None, source, priority, None))
        if LAYER == "business":
            return self.bm.save_application(Application(None, job_id, None, source, priority, None))
        return self._post("/api/applications", {
            "job_id": job_id, "source": source,
            "priority": priority, "applied_date": None, "resume": None,
        })

    def get_application(self, application_id: int):
        if LAYER == "data":     return self.dp.ReadApplicationByID(application_id)
        if LAYER == "business": return self.bm.get_application_by_id(application_id)
        return self._get(f"/api/applications/{application_id}")

    def update_application(self, obj, *, source=None, priority=None):
        aid      = self._id(obj, "application_id")
        job_id   = obj["job_id"]  if isinstance(obj, dict) else obj.job_id
        source   = source   or (obj["source"]   if isinstance(obj, dict) else obj.source)
        priority = priority or (obj["priority"] if isinstance(obj, dict) else obj.priority)
        if LAYER == "data":
            a = self.dp.ReadApplicationByID(aid)
            a.source = source
            a.priority = priority
            self.dp.UpdateApplication(a)
            return self.dp.ReadApplicationByID(aid)
        if LAYER == "business":
            a = self.bm.get_application_by_id(aid)
            a.source = source
            a.priority = priority
            return self.bm.save_application(a)
        return self._put(f"/api/applications/{aid}", {
            "job_id": job_id, "source": source, "priority": priority,
            "applied_date": None, "resume": None,
        })

    def get_all_applications(self):
        if LAYER == "data":     return self.dp.ReadAllApplications()
        if LAYER == "business": return self.bm.get_all_applications()
        return self._get("/api/applications")

    # ════════════════════════════════════════════════════════════════════════
    # APPLICATION STATUS
    # ════════════════════════════════════════════════════════════════════════

    def create_status(self, company, contact, job, app, status: StatusType):
        if LAYER == "data":
            return self.dp.CreateApplicationStatus(
                ApplicationStatus(company=company, contact=contact, job=job,
                                  application=app, status_id=None, status=status))
        if LAYER == "business":
            return self.bm.save_application_status(
                ApplicationStatus(company=company, contact=contact, job=job,
                                  application=app, status_id=None, status=status))
        return self._post("/api/application-statuses", {
            "company_id":     self._id(company, "company_id"),
            "contact_id":     self._id(contact, "contact_id") if contact else None,
            "job_id":         self._id(job, "job_id"),
            "application_id": self._id(app, "application_id"),
            "status":         status.value,
        })

    def get_status(self, status_id: int):
        if LAYER == "data":     return self.dp.ReadApplicationStatusByID(status_id)
        if LAYER == "business": return self.bm.get_application_status_by_id(status_id)
        return self._get(f"/api/application-statuses/{status_id}")

    def update_status(self, obj, company, contact, job, app, new_status: StatusType):
        sid = self._id(obj, "status_id")
        if LAYER == "data":
            s = self.dp.ReadApplicationStatusByID(sid)
            s.status = new_status
            self.dp.UpdateApplicationStatus(s)
            return self.dp.ReadApplicationStatusByID(sid)
        if LAYER == "business":
            s = self.bm.get_application_status_by_id(sid)
            s.status = new_status
            return self.bm.save_application_status(s)
        return self._put(f"/api/application-statuses/{sid}", {
            "company_id":     self._id(company, "company_id"),
            "contact_id":     self._id(contact, "contact_id") if contact else None,
            "job_id":         self._id(job, "job_id"),
            "application_id": self._id(app, "application_id"),
            "status":         new_status.value,
        })

    def delete_status(self, status_id: int):
        if LAYER == "data":     self.dp.DeleteApplicationStatus(status_id)
        elif LAYER == "business": self.bm.delete_application_status(status_id)
        else:                   self._delete(f"/api/application-statuses/{status_id}")

    def get_all_statuses(self):
        if LAYER == "data":     return self.dp.ReadAllApplicationStatuses()
        if LAYER == "business": return self.bm.get_all_application_statuses()
        return self._get("/api/application-statuses")


# ════════════════════════════════════════════════════════════════════════════
# Demo functions — layer-agnostic, use only the adapter
# ════════════════════════════════════════════════════════════════════════════

def demo_company(adapter: LayerAdapter):
    section(f"COMPANY  |  {LAYER.upper()} layer")

    step("CREATE")
    company = adapter.create_company(
        f"[TEST] {LAYER.title()} Co {RUN_ID}",
        f"https://{LAYER}.example", "Remote",
    )
    show("CREATED", company)

    step("READ  -- get by ID")
    cid = adapter._id(company, "company_id")
    fetched = adapter.get_company(cid)
    show("READ BY ID", fetched)

    step("UPDATE  -- company_location: 'Remote' -> 'Austin, TX'")
    updated = adapter.update_company(company, location="Austin, TX")
    show("READ AFTER UPDATE", updated)
    loc = updated["company_location"] if isinstance(updated, dict) else updated.company_location
    assert loc == "Austin, TX"
    ok("company_location updated correctly")

    step("GET ALL  (first 3 shown)")
    rows = adapter.get_all_companies()
    for c in rows[:3]:
        i = c["company_id"] if isinstance(c, dict) else c.company_id
        n = c["name"]       if isinstance(c, dict) else c.name
        print(f"        id={i:<4}  name={n!r}")
    print(f"        ... {len(rows)} total")
    ok(f"Company CRUD complete -- id={adapter._id(updated, 'company_id')} left in DB")
    return updated


def demo_contact(adapter: LayerAdapter, company):
    section(f"CONTACT  |  {LAYER.upper()} layer")

    step("CREATE")
    contact = adapter.create_contact(
        adapter._id(company, "company_id"),
        f"[TEST] {LAYER.title()} Contact {RUN_ID}",
        "Recruiter", f"{LAYER}@test.example", "555-0001",
    )
    show("CREATED", contact)

    step("READ  -- get by ID")
    ctid = adapter._id(contact, "contact_id")
    fetched = adapter.get_contact(ctid)
    show("READ BY ID", fetched)

    step("UPDATE  -- title: 'Recruiter' -> 'Senior Recruiter'")
    updated = adapter.update_contact(contact, title="Senior Recruiter", phone="555-9999")
    show("READ AFTER UPDATE", updated)
    title = updated["title"] if isinstance(updated, dict) else updated.title
    assert title == "Senior Recruiter"
    ok("title updated correctly")

    step("GET ALL  (first 3 shown)")
    rows = adapter.get_all_contacts()
    for ct in rows[:3]:
        i = ct["contact_id"] if isinstance(ct, dict) else ct.contact_id
        n = ct["full_name"]  if isinstance(ct, dict) else ct.full_name
        print(f"        id={i:<4}  name={n!r}")
    print(f"        ... {len(rows)} total")
    ok(f"Contact CRUD complete -- id={adapter._id(updated, 'contact_id')} left in DB")
    return updated


def demo_job_posting(adapter: LayerAdapter, company):
    section(f"JOB POSTING  |  {LAYER.upper()} layer")

    step("CREATE")
    job = adapter.create_job(
        adapter._id(company, "company_id"),
        f"[TEST] {LAYER.title()} Engineer {RUN_ID}",
        "Remote", "Full-time", f"https://jobs.{LAYER}.example",
    )
    show("CREATED", job)

    step("READ  -- get by ID")
    jid = adapter._id(job, "job_id")
    fetched = adapter.get_job(jid)
    show("READ BY ID", fetched)

    step("UPDATE  -- employment_type: 'Full-time' -> 'Contract'")
    updated = adapter.update_job(job, employment_type="Contract")
    show("READ AFTER UPDATE", updated)
    etype = updated["employment_type"] if isinstance(updated, dict) else updated.employment_type
    assert etype == "Contract"
    ok("employment_type updated correctly")

    step("GET ALL  (first 3 shown)")
    rows = adapter.get_all_jobs()
    for j in rows[:3]:
        i = j["job_id"]    if isinstance(j, dict) else j.job_id
        t = j["job_title"] if isinstance(j, dict) else j.job_title
        print(f"        id={i:<4}  title={t!r}")
    print(f"        ... {len(rows)} total")
    ok(f"JobPosting CRUD complete -- id={adapter._id(updated, 'job_id')} left in DB")
    return updated


def demo_application(adapter: LayerAdapter, job):
    section(f"APPLICATION  |  {LAYER.upper()} layer")

    step("CREATE")
    app = adapter.create_application(
        adapter._id(job, "job_id"),
        f"[TEST] {LAYER.title()} LinkedIn", 3,
    )
    show("CREATED", app)

    step("READ  -- get by ID")
    aid = adapter._id(app, "application_id")
    fetched = adapter.get_application(aid)
    show("READ BY ID", fetched)

    step("UPDATE  -- source updated | priority: 3 -> 1")
    updated = adapter.update_application(app, source=f"[TEST] {LAYER.title()} Referral", priority=1)
    show("READ AFTER UPDATE", updated)
    pri = updated["priority"] if isinstance(updated, dict) else updated.priority
    src = updated["source"]   if isinstance(updated, dict) else updated.source
    assert pri == 1 and "Referral" in src
    ok("source and priority updated correctly")

    step("GET ALL  (first 3 shown)")
    rows = adapter.get_all_applications()
    for a in rows[:3]:
        i = a["application_id"] if isinstance(a, dict) else a.application_id
        s = a["source"]         if isinstance(a, dict) else a.source
        print(f"        id={i:<4}  source={s!r}")
    print(f"        ... {len(rows)} total")
    ok(f"Application CRUD complete -- id={adapter._id(updated, 'application_id')} left in DB")
    return updated


def demo_application_status(adapter: LayerAdapter, company, contact, job, app):
    section(f"APPLICATION STATUS  |  {LAYER.upper()} layer")

    step("CREATE  -- status=SAVED")
    ast = adapter.create_status(company, contact, job, app, StatusType.SAVED)
    show("CREATED", ast)
    sid = adapter._id(ast, "status_id")

    step("READ  -- get by ID (nested objects expanded)")
    fetched = adapter.get_status(sid)
    show("READ BY ID", fetched)
    if isinstance(fetched, dict):
        print(f"        nested company  -> id={fetched['company']['company_id']}")
        print(f"        nested contact  -> id={fetched['contact']['contact_id']}")
        print(f"        nested job      -> id={fetched['job']['job_id']}")
        print(f"        nested app      -> id={fetched['application']['application_id']}")
    else:
        print(f"        nested company  -> id={fetched.company.company_id}")
        print(f"        nested contact  -> id={fetched.contact.contact_id if fetched.contact else None}")
        print(f"        nested job      -> id={fetched.job.job_id}")
        print(f"        nested app      -> id={fetched.application.application_id}")

    step("UPDATE  -- status: SAVED -> INTERVIEW")
    updated = adapter.update_status(ast, company, contact, job, app, StatusType.INTERVIEW)
    show("READ AFTER UPDATE", updated)
    new_val = updated["status"] if isinstance(updated, dict) else updated.status.value
    assert new_val == "INTERVIEW"
    ok("status updated to INTERVIEW correctly")

    step("GET ALL  (all rows)")
    rows = adapter.get_all_statuses()
    for s in rows:
        if isinstance(s, dict):
            print(f"        id={s['status_id']:<4}  status={s['status']:<12}  company={s['company']['name']!r}")
        else:
            print(f"        id={s.status_id:<4}  status={s.status.value:<12}  company={s.company.name!r}")
    print(f"        ({len(rows)} total)")

    step("DELETE  -- ApplicationStatus only")
    adapter.delete_status(sid)
    gone = adapter.get_status(sid)
    assert gone is None
    ok(f"ApplicationStatus id={sid} deleted -- confirmed None / 404 on re-read")

    try:
        adapter.delete_status(sid)
        print("    !!  Expected error on second delete -- not raised!")
    except (NotFoundError, requests.HTTPError):
        ok("Second delete correctly raised an error")


# ════════════════════════════════════════════════════════════════════════════
# Entry point
# ════════════════════════════════════════════════════════════════════════════

def main():
    dp, bm = None, None

    if LAYER in {"data", "business"}:
        dp = DataProvider(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
            database=DB_NAME, port=DB_PORT,
        )
        bm = BusinessManager(dp)

    if LAYER == "service":
        try:
            r = requests.get(f"{API_BASE}/")
            r.raise_for_status()
        except Exception:
            print(f"\n  !!  Cannot reach API at {API_BASE}")
            print("      Start it first:  uvicorn main:app --reload --host 0.0.0.0 --port 8000\n")
            sys.exit(1)

    adapter = LayerAdapter(dp, bm)

    print(f"\n{'=' * W}")
    print(f"  Job Tracker -- Full CRUD Demo")
    print(f"  Layer  : {LAYER.upper()}")
    print(f"  Run ID : {RUN_ID}")
    if LAYER == "service":
        print(f"  API    : {API_BASE}")
    print(f"  [TEST] records are left in DB (except ApplicationStatus)")
    print(f"{'=' * W}")

    company = demo_company(adapter)
    contact = demo_contact(adapter, company)
    job     = demo_job_posting(adapter, company)
    app     = demo_application(adapter, job)
    demo_application_status(adapter, company, contact, job, app)

    print(f"\n{'=' * W}")
    print(f"  All assertions passed.")
    print(f"  Layer tested : {LAYER.upper()}")
    print(f"  Run ID       : {RUN_ID}")
    print(f"{'=' * W}\n")

    if dp:
        dp.close()


if __name__ == "__main__":
    main()
