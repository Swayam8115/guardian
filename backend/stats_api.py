from fastapi import APIRouter
from database.db import SessionLocal
from database.models import FIRModel
from datetime import datetime, timedelta, date
from collections import Counter
from typing import Optional

router = APIRouter()


@router.get("/stats")
def get_stats():
    db = SessionLocal()
    try:
        date_rows = db.query(FIRModel.date_of_filing).filter(FIRModel.date_of_filing != None).all()
        year_months = [d[0][:7] for d in date_rows if d[0] and len(d[0]) >= 7]
        if not year_months:
            return {"error": "No data"}
        latest_ym = max(year_months)
        month_label = datetime.strptime(latest_ym, "%Y-%m").strftime("%B %Y")

        month_records = db.query(FIRModel).filter(
            FIRModel.date_of_filing.like(f"{latest_ym}%")
        ).all()
        total = len(month_records)

        district_counts = Counter(r.district for r in month_records if r.district)
        if district_counts:
            top_district, top_district_count = district_counts.most_common(1)[0]
        else:
            top_district, top_district_count = "N/A", 0
        top_district_pct = round(top_district_count / total * 100, 1) if total else 0

        cat_counts = Counter()
        for r in month_records:
            if r.crime_categories:
                for cat in r.crime_categories:
                    cat_counts[cat.strip()] += 1
        if cat_counts:
            top_crime, top_crime_count = cat_counts.most_common(1)[0]
        else:
            top_crime, top_crime_count = "N/A", 0
        top_crime_pct = round(top_crime_count / total * 100, 1) if total else 0

        return {
            "month_label": month_label,
            "total_month": total,
            "top_district": top_district,
            "top_district_count": top_district_count,
            "top_district_pct": top_district_pct,
            "top_crime": top_crime,
            "top_crime_count": top_crime_count,
            "top_crime_pct": top_crime_pct,
        }
    finally:
        db.close()


@router.get("/crime-distribution")
def get_crime_distribution():
    db = SessionLocal()
    try:
        rows = db.query(FIRModel.crime_categories).all()
        counter = Counter()
        for (cats,) in rows:
            if cats:
                for cat in cats:
                    counter[cat.strip()] += 1
        return [{"category": k, "count": v} for k, v in counter.most_common()]
    finally:
        db.close()


@router.get("/available-years")
def get_available_years():
    db = SessionLocal()
    try:
        rows = db.query(FIRModel.date_of_filing).all()
        years = set()
        for (d,) in rows:
            if d and len(d) >= 4:
                try:
                    years.add(int(d[:4]))
                except ValueError:
                    pass
        return sorted(years, reverse=True)
    finally:
        db.close()


@router.get("/frequency-trend")
def get_frequency_trend(
    period: str = "week",
    year: Optional[int] = None,
    month: Optional[int] = None,
):
    db = SessionLocal()
    try:
        rows = db.query(FIRModel.date_of_filing, FIRModel.crime_categories).all()

        # Top 3 crime categories across all data
        all_cats = Counter()
        for _, cats in rows:
            if cats:
                for c in cats:
                    all_cats[c.strip()] += 1
        top3 = [c for c, _ in all_cats.most_common(3)]

        if year and month:
            # ── Specific month: daily counts ────────────────────────────────
            prefix = f"{year:04d}-{month:02d}"
            data: dict = {}
            for filing_date, cats in rows:
                if not filing_date or filing_date[:7] != prefix:
                    continue
                day = filing_date[:10]
                if day not in data:
                    data[day] = {c: 0 for c in top3}
                if cats:
                    for c in cats:
                        c = c.strip()
                        if c in data[day]:
                            data[day][c] += 1

        elif year:
            # ── Full year: monthly counts ────────────────────────────────────
            prefix = f"{year:04d}"
            data = {}
            for filing_date, cats in rows:
                if not filing_date or filing_date[:4] != prefix:
                    continue
                key = filing_date[:7]   # YYYY-MM
                if key not in data:
                    data[key] = {c: 0 for c in top3}
                if cats:
                    for c in cats:
                        c = c.strip()
                        if c in data[key]:
                            data[key][c] += 1

        else:
            # ── Default: last N days ─────────────────────────────────────────
            days = 7 if period == "week" else 30
            since = (date.today() - timedelta(days=days)).isoformat()
            data = {}
            for filing_date, cats in rows:
                if not filing_date:
                    continue
                day = filing_date[:10]
                if day < since:
                    continue
                if day not in data:
                    data[day] = {c: 0 for c in top3}
                if cats:
                    for c in cats:
                        c = c.strip()
                        if c in data[day]:
                            data[day][c] += 1

        result = []
        for key in sorted(data.keys()):
            for cat in top3:
                result.append({"date": key, "category": cat, "count": data[key].get(cat, 0)})
        return result
    finally:
        db.close()
