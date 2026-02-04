from __future__ import annotations

from dataclasses import replace
from typing import Any, Callable, Optional, TypeVar

import mysql.connector
from mysql.connector.connection import MySQLConnection

from models import (
    Application,
    ApplicationStatus,
    Company,
    Contact,
    JobPosting,
    StatusType,
)

T = TypeVar("T")


class DataProvider:
    """
    Refinements vs earlier version:
      - Ensures SELECTs don't leave long-running transactions open when autocommit=False
      - UPDATE methods no longer return False when row exists but values didn't change
      - Dedupes long ApplicationStatus JOIN SQL
      - Adds small internal read helpers to reduce repetition (no new public features)
    """

    # Shared SELECT for ApplicationStatus object reconstruction
    _STATUS_JOIN_SELECT = """
        SELECT
          -- status row
          s.status_id AS s_status_id,
          s.status AS s_status,

          -- application row (aliased)
          a.application_id AS a_application_id,
          a.job_id AS a_job_id,
          a.applied_date AS a_applied_date,
          a.source AS a_source,
          a.priority AS a_priority,
          a.resume AS a_resume,

          -- job row (aliased)
          j.job_id AS j_job_id,
          j.company_id AS j_company_id,
          j.job_title AS j_job_title,
          j.job_location AS j_job_location,
          j.employment_type AS j_employment_type,
          j.job_url AS j_job_url,
          j.salary AS j_salary,
          j.posted_date AS j_posted_date,

          -- company row (aliased)
          c.company_id AS c_company_id,
          c.name AS c_name,
          c.website AS c_website,
          c.company_location AS c_company_location,

          -- contact row (nullable; aliased)
          ct.contact_id AS ct_contact_id,
          ct.company_id AS ct_company_id,
          ct.full_name AS ct_full_name,
          ct.title AS ct_title,
          ct.email AS ct_email,
          ct.phone AS ct_phone,
          ct.linkedin AS ct_linkedin

        FROM application_status s
        JOIN application a ON s.application_id = a.application_id
        JOIN job_posting j ON a.job_id = j.job_id
        JOIN company c ON j.company_id = c.company_id
        LEFT JOIN contact ct ON s.contact_id = ct.contact_id
    """

    def __init__(
        self,
        *,
        host: str,
        user: str,
        password: str,
        database: str,
        port: int = 3306,
    ) -> None:
        self._conn: MySQLConnection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
        )
        # Keeping your original design (explicit commit/rollback).
        self._conn.autocommit = False

    def close(self) -> None:
        if self._conn.is_connected():
            self._conn.close()

    def __enter__(self) -> "DataProvider":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # -------------------------
    # Internal helpers
    # -------------------------
    def _execute(
        self,
        sql: str,
        params: tuple[Any, ...] = (),
        *,
        fetchone: bool = False,
        fetchall: bool = False,
    ) -> Any:
        """
        SELECT helper. Ends the read transaction with rollback() when autocommit is off.
        """
        cur = self._conn.cursor(dictionary=True)
        try:
            cur.execute(sql, params)
            if fetchone:
                return cur.fetchone()
            if fetchall:
                return cur.fetchall()
            return None
        finally:
            cur.close()
            # IMPORTANT refinement: close the read-only transaction.
            # (Prevents long-running transactions during console use.)
            if not self._conn.autocommit:
                try:
                    self._conn.rollback()
                except Exception:
                    pass

    def _execute_write(self, sql: str, params: tuple[Any, ...] = ()) -> int:
        cur = self._conn.cursor()
        try:
            cur.execute(sql, params)
            self._conn.commit()
            return int(cur.lastrowid or 0)
        except Exception:
            self._conn.rollback()
            raise
        finally:
            cur.close()

    def _execute_update_delete(self, sql: str, params: tuple[Any, ...] = ()) -> int:
        """
        Returns rowcount so callers can distinguish:
          - 0 rows matched (not found) vs
          - 0 rows changed (values identical)
        """
        cur = self._conn.cursor()
        try:
            cur.execute(sql, params)
            rc = int(cur.rowcount or 0)
            self._conn.commit()
            return rc
        except Exception:
            self._conn.rollback()
            raise
        finally:
            cur.close()

    def _read_one(self, sql: str, params: tuple[Any, ...], mapper: Callable[[dict[str, Any]], T]) -> Optional[T]:
        row = self._execute(sql, params, fetchone=True)
        return None if row is None else mapper(row)

    def _read_many(self, sql: str, mapper: Callable[[dict[str, Any]], T]) -> list[T]:
        rows = self._execute(sql, fetchall=True) or []
        return [mapper(r) for r in rows]

    def _exists(self, table: str, pk_col: str, pk_value: int) -> bool:
        # Internal-only usage; safe since table/col are not user input in your code.
        sql = f"SELECT 1 FROM {table} WHERE {pk_col} = %s LIMIT 1"
        row = self._execute(sql, (pk_value,), fetchone=True)
        return row is not None

    # -------------------------
    # Row -> Object mappers
    # -------------------------
    @staticmethod
    def _company_from_row(row: dict[str, Any]) -> Company:
        return Company(
            company_id=row["company_id"],
            name=row["name"],
            website=row.get("website"),
            company_location=row.get("company_location"),
        )

    @staticmethod
    def _contact_from_row(row: dict[str, Any]) -> Contact:
        return Contact(
            contact_id=row["contact_id"],
            company_id=row["company_id"],
            full_name=row["full_name"],
            title=row.get("title"),
            email=row.get("email"),
            phone=row.get("phone"),
            linkedin=row.get("linkedin"),
        )

    @staticmethod
    def _job_posting_from_row(row: dict[str, Any]) -> JobPosting:
        return JobPosting(
            job_id=row["job_id"],
            company_id=row["company_id"],
            job_title=row["job_title"],
            job_location=row.get("job_location"),
            employment_type=row.get("employment_type"),
            job_url=row.get("job_url"),
            salary=row.get("salary"),
            posted_date=row.get("posted_date"),
        )

    @staticmethod
    def _application_from_row(row: dict[str, Any]) -> Application:
        return Application(
            application_id=row["application_id"],
            job_id=row["job_id"],
            applied_date=row.get("applied_date"),
            source=row.get("source"),
            priority=row.get("priority"),
            resume=row.get("resume"),
        )

    @staticmethod
    def _application_status_from_join_row(row: dict[str, Any]) -> ApplicationStatus:
        company = Company(
            company_id=row["c_company_id"],
            name=row["c_name"],
            website=row.get("c_website"),
            company_location=row.get("c_company_location"),
        )

        job = JobPosting(
            job_id=row["j_job_id"],
            company_id=row["j_company_id"],
            job_title=row["j_job_title"],
            job_location=row.get("j_job_location"),
            employment_type=row.get("j_employment_type"),
            job_url=row.get("j_job_url"),
            salary=row.get("j_salary"),
            posted_date=row.get("j_posted_date"),
        )

        application = Application(
            application_id=row["a_application_id"],
            job_id=row["a_job_id"],
            applied_date=row.get("a_applied_date"),
            source=row.get("a_source"),
            priority=row.get("a_priority"),
            resume=row.get("a_resume"),
        )

        if row.get("ct_contact_id") is None:
            contact = None
        else:
            contact = Contact(
                contact_id=row["ct_contact_id"],
                company_id=row["ct_company_id"],
                full_name=row["ct_full_name"],
                title=row.get("ct_title"),
                email=row.get("ct_email"),
                phone=row.get("ct_phone"),
                linkedin=row.get("ct_linkedin"),
            )

        return ApplicationStatus(
            company=company,
            contact=contact,
            job=job,
            application=application,
            status_id=row["s_status_id"],
            status=StatusType(row["s_status"]),
        )

    # ============================================================
    # 1) COMPANY CRUD
    # ============================================================
    def CreateCompany(self, company: Company) -> Company:
        sql = """
            INSERT INTO company (name, website, company_location)
            VALUES (%s, %s, %s)
        """
        new_id = self._execute_write(sql, (company.name, company.website, company.company_location))
        return replace(company, company_id=new_id)

    def ReadCompanyByID(self, company_id: int) -> Optional[Company]:
        sql = """
            SELECT company_id, name, website, company_location
            FROM company
            WHERE company_id = %s
        """
        return self._read_one(sql, (company_id,), self._company_from_row)

    def ReadAllCompanies(self) -> list[Company]:
        sql = """
            SELECT company_id, name, website, company_location
            FROM company
            ORDER BY company_id
        """
        return self._read_many(sql, self._company_from_row)

    def UpdateCompany(self, company: Company) -> bool:
        if company.company_id is None:
            raise ValueError("UpdateCompany requires company.company_id to be set.")
        sql = """
            UPDATE company
            SET name = %s, website = %s, company_location = %s
            WHERE company_id = %s
        """
        rc = self._execute_update_delete(sql, (company.name, company.website, company.company_location, company.company_id))
        if rc > 0:
            return True
        # rc==0 can mean "not found" OR "no changes"
        return self._exists("company", "company_id", company.company_id)

    def DeleteCompany(self, company_id: int) -> bool:
        sql = "DELETE FROM company WHERE company_id = %s"
        rc = self._execute_update_delete(sql, (company_id,))
        return rc > 0

    # ============================================================
    # 2) CONTACT CRUD
    # ============================================================
    def CreateContact(self, contact: Contact) -> Contact:
        sql = """
            INSERT INTO contact (company_id, full_name, title, email, phone, linkedin)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        new_id = self._execute_write(
            sql,
            (contact.company_id, contact.full_name, contact.title, contact.email, contact.phone, contact.linkedin),
        )
        return replace(contact, contact_id=new_id)

    def ReadContactByID(self, contact_id: int) -> Optional[Contact]:
        sql = """
            SELECT contact_id, company_id, full_name, title, email, phone, linkedin
            FROM contact
            WHERE contact_id = %s
        """
        return self._read_one(sql, (contact_id,), self._contact_from_row)

    def ReadAllContacts(self) -> list[Contact]:
        sql = """
            SELECT contact_id, company_id, full_name, title, email, phone, linkedin
            FROM contact
            ORDER BY contact_id
        """
        return self._read_many(sql, self._contact_from_row)

    def UpdateContact(self, contact: Contact) -> bool:
        if contact.contact_id is None:
            raise ValueError("UpdateContact requires contact.contact_id to be set.")
        sql = """
            UPDATE contact
            SET company_id = %s,
                full_name = %s,
                title = %s,
                email = %s,
                phone = %s,
                linkedin = %s
            WHERE contact_id = %s
        """
        rc = self._execute_update_delete(
            sql,
            (
                contact.company_id,
                contact.full_name,
                contact.title,
                contact.email,
                contact.phone,
                contact.linkedin,
                contact.contact_id,
            ),
        )
        if rc > 0:
            return True
        return self._exists("contact", "contact_id", contact.contact_id)

    def DeleteContact(self, contact_id: int) -> bool:
        sql = "DELETE FROM contact WHERE contact_id = %s"
        rc = self._execute_update_delete(sql, (contact_id,))
        return rc > 0

    # ============================================================
    # 3) JOB_POSTING CRUD
    # ============================================================
    def CreateJobPosting(self, job: JobPosting) -> JobPosting:
        sql = """
            INSERT INTO job_posting
              (company_id, job_title, job_location, employment_type, job_url, salary, posted_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        new_id = self._execute_write(
            sql,
            (
                job.company_id,
                job.job_title,
                job.job_location,
                job.employment_type,
                job.job_url,
                job.salary,
                job.posted_date,
            ),
        )
        return replace(job, job_id=new_id)

    def ReadJobPostingByID(self, job_id: int) -> Optional[JobPosting]:
        sql = """
            SELECT job_id, company_id, job_title, job_location, employment_type, job_url, salary, posted_date
            FROM job_posting
            WHERE job_id = %s
        """
        return self._read_one(sql, (job_id,), self._job_posting_from_row)

    def ReadAllJobPostings(self) -> list[JobPosting]:
        sql = """
            SELECT job_id, company_id, job_title, job_location, employment_type, job_url, salary, posted_date
            FROM job_posting
            ORDER BY job_id
        """
        return self._read_many(sql, self._job_posting_from_row)

    def UpdateJobPosting(self, job: JobPosting) -> bool:
        if job.job_id is None:
            raise ValueError("UpdateJobPosting requires job.job_id to be set.")
        sql = """
            UPDATE job_posting
            SET company_id = %s,
                job_title = %s,
                job_location = %s,
                employment_type = %s,
                job_url = %s,
                salary = %s,
                posted_date = %s
            WHERE job_id = %s
        """
        rc = self._execute_update_delete(
            sql,
            (
                job.company_id,
                job.job_title,
                job.job_location,
                job.employment_type,
                job.job_url,
                job.salary,
                job.posted_date,
                job.job_id,
            ),
        )
        if rc > 0:
            return True
        return self._exists("job_posting", "job_id", job.job_id)

    def DeleteJobPosting(self, job_id: int) -> bool:
        sql = "DELETE FROM job_posting WHERE job_id = %s"
        rc = self._execute_update_delete(sql, (job_id,))
        return rc > 0

    # ============================================================
    # 4) APPLICATION CRUD
    # ============================================================
    def CreateApplication(self, app: Application) -> Application:
        sql = """
            INSERT INTO application (job_id, applied_date, source, priority, resume)
            VALUES (%s, %s, %s, %s, %s)
        """
        new_id = self._execute_write(sql, (app.job_id, app.applied_date, app.source, app.priority, app.resume))
        return replace(app, application_id=new_id)

    def ReadApplicationByID(self, application_id: int) -> Optional[Application]:
        sql = """
            SELECT application_id, job_id, applied_date, source, priority, resume
            FROM application
            WHERE application_id = %s
        """
        return self._read_one(sql, (application_id,), self._application_from_row)

    def ReadAllApplications(self) -> list[Application]:
        sql = """
            SELECT application_id, job_id, applied_date, source, priority, resume
            FROM application
            ORDER BY application_id
        """
        return self._read_many(sql, self._application_from_row)

    def UpdateApplication(self, app: Application) -> bool:
        if app.application_id is None:
            raise ValueError("UpdateApplication requires app.application_id to be set.")
        sql = """
            UPDATE application
            SET job_id = %s,
                applied_date = %s,
                source = %s,
                priority = %s,
                resume = %s
            WHERE application_id = %s
        """
        rc = self._execute_update_delete(
            sql,
            (app.job_id, app.applied_date, app.source, app.priority, app.resume, app.application_id),
        )
        if rc > 0:
            return True
        return self._exists("application", "application_id", app.application_id)

    def DeleteApplication(self, application_id: int) -> bool:
        sql = "DELETE FROM application WHERE application_id = %s"
        rc = self._execute_update_delete(sql, (application_id,))
        return rc > 0

    # ============================================================
    # 5) APPLICATION_STATUS CRUD
    # ============================================================
    def CreateApplicationStatus(self, status: ApplicationStatus) -> ApplicationStatus:
        if status.application.application_id is None:
            raise ValueError("CreateApplicationStatus requires status.application.application_id to be set.")

        contact_id = None if status.contact is None else status.contact.contact_id
        if status.contact is not None and status.contact.contact_id is None:
            raise ValueError("CreateApplicationStatus: status.contact.contact_id must be set (or contact=None).")

        sql = """
            INSERT INTO application_status (application_id, contact_id, status)
            VALUES (%s, %s, %s)
        """
        new_id = self._execute_write(
            sql,
            (status.application.application_id, contact_id, status.status.value),
        )
        return replace(status, status_id=new_id)

    def ReadApplicationStatusByID(self, status_id: int) -> Optional[ApplicationStatus]:
        sql = self._STATUS_JOIN_SELECT + " WHERE s.status_id = %s"
        row = self._execute(sql, (status_id,), fetchone=True)
        return None if row is None else self._application_status_from_join_row(row)

    def ReadAllApplicationStatuses(self) -> list[ApplicationStatus]:
        sql = self._STATUS_JOIN_SELECT + " ORDER BY s.status_id"
        rows = self._execute(sql, fetchall=True) or []
        return [self._application_status_from_join_row(r) for r in rows]

    def UpdateApplicationStatus(self, status: ApplicationStatus) -> bool:
        if status.status_id is None:
            raise ValueError("UpdateApplicationStatus requires status.status_id to be set.")
        if status.application.application_id is None:
            raise ValueError("UpdateApplicationStatus requires status.application.application_id to be set.")

        contact_id = None if status.contact is None else status.contact.contact_id
        if status.contact is not None and status.contact.contact_id is None:
            raise ValueError("UpdateApplicationStatus: status.contact.contact_id must be set (or contact=None).")

        sql = """
            UPDATE application_status
            SET application_id = %s,
                contact_id = %s,
                status = %s
            WHERE status_id = %s
        """
        rc = self._execute_update_delete(
            sql,
            (status.application.application_id, contact_id, status.status.value, status.status_id),
        )
        if rc > 0:
            return True
        return self._exists("application_status", "status_id", status.status_id)

    def DeleteApplicationStatus(self, status_id: int) -> bool:
        sql = "DELETE FROM application_status WHERE status_id = %s"
        rc = self._execute_update_delete(sql, (status_id,))
        return rc > 0
