from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from src.db.session import get_session
from src.schemas.reports import (
    SummaryStats, WeeklySummary, MonthlySummary, 
    YearlySummary, DonorCollectionReport
)
from src.services.reports import report_service
from src.api.dependencies import get_current_user, RoleChecker
from src.models.user import User
import uuid
from datetime import date
from typing import List, Optional

router = APIRouter()

# Reports are generally readable by Admin, Committee, and Cashier
allow_read = RoleChecker(["super_admin", "admin", "committee", "cashier"])

@router.get("/summary", response_model=SummaryStats)
def get_summary_stats(
    *,
    session: Session = Depends(get_session),
    masjid_id: uuid.UUID,
    current_user: User = Depends(get_current_user)
):
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return report_service.get_dashboard_summary(session, masjid_id)

@router.get("/weekly", response_model=WeeklySummary)
def get_weekly_report(
    *,
    session: Session = Depends(get_session),
    masjid_id: uuid.UUID,
    start_date: date,
    current_user: User = Depends(get_current_user)
):
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return report_service.get_weekly_report(session, masjid_id, start_date)

@router.get("/monthly", response_model=MonthlySummary)
def get_monthly_report(
    *,
    session: Session = Depends(get_session),
    masjid_id: uuid.UUID,
    year: int,
    month: int,
    current_user: User = Depends(get_current_user)
):
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return report_service.get_monthly_report(session, masjid_id, year, month)

@router.get("/yearly", response_model=YearlySummary)
def get_yearly_report(
    *,
    session: Session = Depends(get_session),
    masjid_id: uuid.UUID,
    year: int,
    current_user: User = Depends(get_current_user)
):
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return report_service.get_yearly_report(session, masjid_id, year)

@router.get("/donors", response_model=DonorCollectionReport)
def get_donor_report(
    *,
    session: Session = Depends(get_session),
    masjid_id: uuid.UUID,
    month: str,  # YYYY-MM
    current_user: User = Depends(get_current_user)
):
    current_role = getattr(current_user, "_token_role", "viewer")
    current_masjid_id = getattr(current_user, "_token_masjid_id", None)

    if current_role != "super_admin" and str(current_masjid_id) != str(masjid_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return report_service.get_donor_collection_report(session, masjid_id, month)
