import re
from datetime import date
from typing import Any, Dict, Optional
# ============================================================
# MONTH MAPPING
# ============================================================
MONTHS = {
          "january": 1,
          "february": 2,
          "march": 3,
          "april": 4,
          "may": 5,
          "june": 6,
          "july": 7,
          "august": 8,
          "september": 9,
          "october": 10,
          "november": 11,
          "december": 12,
          "jan": 1,
          "feb": 2,
          "mar": 3,
          "apr": 4,
          "jun": 6,
          "jul": 7,
          "aug": 8,
          "sep": 9,
          "sept": 9,
          "oct": 10,
          "nov": 11,
          "dec": 12,
}
# ============================================================
# NORMALIZE DATE TEXT
# ============================================================
def normalize_date_text(
          text: str
) -> str:
          """
          Normalize date text.
          Examples:
                    March 2025
                    March, 2025
                    03/2025
                    03-2025
          """
          if not text:
                    return ""
          text = str(text).lower().strip()
          # Normalize different dash characters.
          text = text.replace("–", "-")
          text = text.replace("—", "-")
          # Normalize whitespace.
          text = re.sub(
                    r"\s+",
                    " ",
                    text
          )
          return text
# ============================================================
# CHECK CURRENT / PRESENT
# ============================================================
def is_current_date(
          text: str
) -> bool:
          """
          Check whether text represents an ongoing/current role.
          """
          if not text:
                    return False
          normalized = normalize_date_text(
                    text
          )
          current_values = {
                    "present",
                    "current",
                    "currently",
                    "till date",
                    "to date",
                    "until now",
                    "now",
                    "ongoing",
                    "on-going",
                    "till now",
                    "up to now",
          }
          return normalized in current_values
# ============================================================
# PARSE MONTH + YEAR
# ============================================================
def parse_month_year(
          text: str
) -> Optional[date]:
          """
          Parse a date containing month + year or year only.
          Supported:
                    03/2025
                    3/2025
                    03-2025
                    3-2025
                    March 2025
                    Mar 2025
                    March, 2025
                    Mar, 2025
                    2025
                    2024
                    1999
          Returns:
                    datetime.date with first day of month.
          Returns None when no supported date is found.
          """
          if not text:
                    return None
          text = normalize_date_text(
                    text
          )
          if not text:
                    return None
          # ========================================================
          # NUMERIC MONTH + YEAR
          # ========================================================
          numeric_match = re.search(
                    r"\b(0?[1-9]|1[0-2])\s*[/\\-]\s*((?:19|20)\d{2})\b",
                    text
          )
          if numeric_match:
                    month = int(
                              numeric_match.group(1)
                    )
                    year = int(
                              numeric_match.group(2)
                    )
                    try:
                              return date(
                                        year,
                                        month,
                                        1
                              )
                    except ValueError:
                              return None
          # ========================================================
          # MONTH NAME + YEAR
          # ========================================================
          month_year_pattern = (
                    r"\b("
                    r"January|Jan|"
                    r"February|Feb|"
                    r"March|Mar|"
                    r"April|Apr|"
                    r"May|"
                    r"June|Jun|"
                    r"July|Jul|"
                    r"August|Aug|"
                    r"September|Sep|Sept|"
                    r"October|Oct|"
                    r"November|Nov|"
                    r"December|Dec"
                    r")"
                    r"\s*,?\s*"
                    r"((?:19|20)\d{2})\b"
          )
          month_year_match = re.search(
                    month_year_pattern,
                    text,
                    re.IGNORECASE
          )
          if month_year_match:
                    month_text = (
                              month_year_match
                              .group(1)
                              .lower()
                    )
                    year = int(
                              month_year_match.group(2)
                    )
                    month = MONTHS.get(
                              month_text
                    )
                    if month is not None:
                              try:
                                        return date(
                                                  year,
                                                  month,
                                                  1
                                        )
                              except ValueError:
                                        return None
          # ========================================================
          # YEAR ONLY
          # ========================================================
          year_match = re.search(
                    r"\b((?:19|20)\d{2})\b",
                    text
          )
          if year_match:
                    year = int(
                              year_match.group(1)
                    )
                    try:
                              return date(
                                        year,
                                        1,
                                        1
                              )
                    except ValueError:
                              return None
          return None
# ============================================================
# PARSE EXPERIENCE DATE
# ============================================================
def parse_experience_date(
          text: str
) -> Optional[date]:
          """
          Parse an experience date.
          Current keywords such as Present and Current
          return None because they are not calendar dates.
          """
          if not text:
                    return None
          text = normalize_date_text(
                    text
          )
          # Remove brackets.
          text = text.replace(
                    "[",
                    ""
          )
          text = text.replace(
                    "]",
                    ""
          )
          text = text.strip()
          # Present / Current is not a calendar date.
          if is_current_date(text):
                    return None
          return parse_month_year(
                    text
          )
# ============================================================
# CALCULATE MONTH DIFFERENCE
# ============================================================
def calculate_month_difference(
          start_date: Optional[date],
          end_date: Optional[date]
) -> int:
          """
          Calculate the number of whole calendar months
          between two dates.
          If either date is missing, duration is unknown,
          so return 0.
          """
          if not start_date or not end_date:
                    return 0
          months = (
                    (end_date.year - start_date.year)
                    * 12
                    +
                    (end_date.month - start_date.month)
          )
          return max(
                    months,
                    0
          )
# ============================================================
# CONVERT MONTHS TO YEARS
# ============================================================
def months_to_years(
          months: int
) -> float:
          """
          Convert months to years.
          """
          if not months:
                    return 0.0
          return round(
                    months / 12,
                    2
          )
def parse_duration_text(value: Any) -> Optional[int]:
    """Parse explicit experience durations into whole months.

    Supports values such as ``2 years``, ``18 months``,
    ``1 year 6 months``, and ``2.5 yrs``. Returns None if no
    supported duration unit is present.
    """
    if value is None:
        return None
    text = str(value).lower().strip()
    if not text:
        return None

    year_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?|y)\b", text
    )
    month_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:months?|mos?|mo)\b", text
    )
    if not year_match and not month_match:
        return None

    total_months = 0.0
    if year_match:
        total_months += float(year_match.group(1)) * 12
    if month_match:
        total_months += float(month_match.group(1))
    return max(0, round(total_months))


# ============================================================
# EXTRACT EXPERIENCE PERIOD
# ============================================================
def extract_experience_period(
          experience: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
          """
          Extract and normalize an experience period.
          Supports:
                    {
                              "dates": {
                                        "start": "03/2025",
                                        "end": "Present",
                                        "current": True
                              }
                    }
          and:
                    {
                              "start": "03/2025",
                              "end": "Present",
                              "current": True
                    }
          Important:
                    An experience may have a valid start date
                    but no end date.
                    Example:
                              [April 2025]
                    In that case:
                              start = April 2025
                              end = None
                              current = False
                    We do NOT invent an end date.
          """
          if not isinstance(
                    experience,
                    dict
          ):
                    return None
          # ========================================================
          # GET DATE INFORMATION
          # ========================================================
          dates = experience.get(
                    "dates"
          )
          if isinstance(
                    dates,
                    dict
          ):
                    start_text = dates.get(
                              "start"
                    )
                    end_text = dates.get(
                              "end"
                    )
                    current = dates.get(
                              "current",
                              False
                    )
          else:
                    start_text = experience.get(
                              "start"
                    )
                    end_text = experience.get(
                              "end"
                    )
                    current = experience.get(
                              "current",
                              False
                    )
          # ========================================================
          # VALIDATE START
          # ========================================================
          if not start_text:
                    return None
          start_text = str(
                    start_text
          ).strip()
          if not start_text:
                    return None
          # ========================================================
          # PARSE START DATE
          # ========================================================
          start_date = parse_experience_date(
                    start_text
          )
          if start_date is None:
                    return None
          # ========================================================
          # DETERMINE CURRENT STATUS
          # ========================================================
          if current is True:
                    is_current = True
          elif (
                    isinstance(
                              end_text,
                              str
                    )
                    and
                    is_current_date(
                              end_text
                    )
          ):
                    is_current = True
          else:
                    is_current = False
          # ========================================================
          # CURRENT ROLE
          # ========================================================
          if is_current:
                    end_date = date.today()
          # ========================================================
          # EXPLICIT END DATE
          # ========================================================
          elif end_text:
                    end_text = str(
                              end_text
                    ).strip()
                    if not end_text:
                              end_date = None
                    elif is_current_date(
                              end_text
                    ):
                              is_current = True
                              end_date = date.today()
                    else:
                              end_date = parse_experience_date(
                                        end_text
                              )
          # ========================================================
          # NO END DATE
          # ========================================================
          else:
                    end_date = None
          # ========================================================
          # VALIDATE PERIOD
          # ========================================================
          if (
                    end_date is not None
                    and
                    end_date < start_date
          ):
                    return None
          # ========================================================
          # RETURN NORMALIZED PERIOD
          # ========================================================
          return {
                    "start": start_date,
                    "end": end_date,
                    "current": is_current,
          }
# ============================================================
# CALCULATE TOTAL EXPERIENCE
# ============================================================

def calculate_total_experience(
    experiences: list
) -> Optional[float]:
    """Calculate total experience from dates or explicit durations.

    Overlapping dated roles are merged. For undated roles, use an explicit
    duration when available, including a numeric ``years`` field.
    """
    if not experiences:
        return None

    dated_periods = []
    explicit_duration_months = 0
    found_any_duration = False

    for experience in experiences:
        if not isinstance(experience, dict):
            continue

        period = extract_experience_period(experience)

        if period and period.get("end") is not None:
            dated_periods.append(period)
            found_any_duration = True
            continue

        duration_value = experience.get("duration")
        if duration_value is None:
            duration_value = experience.get("duration_text")

        duration_months = parse_duration_text(duration_value)

        # Support numeric or numeric-string years from resume parsers.
        if duration_months is None:
            years_value = experience.get("years")
            if years_value is not None:
                try:
                    years = float(years_value)
                    if years >= 0:
                        duration_months = round(years * 12)
                except (TypeError, ValueError):
                    pass

        if duration_months is not None:
            explicit_duration_months += duration_months
            found_any_duration = True

    total_months = explicit_duration_months

    if dated_periods:
        dated_periods.sort(key=lambda item: item["start"])
        merged = []

        for period in dated_periods:
            if not merged:
                merged.append({
                    "start": period["start"],
                    "end": period["end"],
                })
                continue

            previous = merged[-1]

            if period["start"] <= previous["end"]:
                if period["end"] > previous["end"]:
                    previous["end"] = period["end"]
            else:
                merged.append({
                    "start": period["start"],
                    "end": period["end"],
                })

        for period in merged:
            total_months += calculate_month_difference(
                period["start"], period["end"]
            )

    if not found_any_duration:
        return None

    return months_to_years(total_months)

# ============================================================
# CALCULATE INDIVIDUAL EXPERIENCE DETAILS
# ============================================================

def calculate_experience_details(
    experiences: list
) -> list:
    """Return normalized duration details for each experience entry."""
    if not experiences:
        return []

    details = []

    for experience in experiences:
        if not isinstance(experience, dict):
            continue

        period = extract_experience_period(experience)

        if period and period.get("end") is not None:
            start_date = period.get("start")
            end_date = period.get("end")
            current = period.get("current", False)
            duration_months = calculate_month_difference(
                start_date, end_date
            )
            formatted_start = (
                start_date.isoformat() if start_date else None
            )
            formatted_end = (
                "Present" if current else end_date.isoformat()
            )
        else:
            duration_value = experience.get("duration")
            if duration_value is None:
                duration_value = experience.get("duration_text")

            parsed_months = parse_duration_text(duration_value)

            if parsed_months is None:
                years_value = experience.get("years")
                try:
                    parsed_months = (
                        round(float(years_value) * 12)
                        if years_value is not None
                        and float(years_value) >= 0
                        else None
                    )
                except (TypeError, ValueError):
                    parsed_months = None

            if parsed_months is None:
                if not period:
                    # Keep the role visible even when its duration is unknown.
                    duration_months = 0
                else:
                    duration_months = 0
            else:
                duration_months = parsed_months

            start_date = period.get("start") if period else None
            end_date = period.get("end") if period else None
            current = period.get("current", False) if period else False
            formatted_start = (
                start_date.isoformat() if start_date else None
            )

            if current:
                formatted_end = "Present"
            elif end_date is not None:
                formatted_end = end_date.isoformat()
            else:
                formatted_end = None

        details.append({
            "job_title": (
                experience.get("job_title")
                or experience.get("title")
                or experience.get("role")
                or experience.get("position")
            ),
            "company": experience.get("company"),
            "location": experience.get("location"),
            "start": formatted_start,
            "end": formatted_end,
            "current": current,
            "duration_months": duration_months,
            "duration_years": months_to_years(duration_months),
        })

    return details


# ============================================================
# MATCH EXPERIENCE
# ============================================================
def match_experience(
          resume: dict,
          required_experience: dict | None
) -> dict:
          """
          Match candidate experience against job requirements.
          """
          # ========================================================
          # NO EXPERIENCE REQUIREMENT
          # ========================================================
          if not required_experience:
                    return {
                              "status": "not_required",
                              "required_years": None,
                              "candidate_years": None,
                              "experience_details": [],
                    }
          required_years = (
                    required_experience.get(
                              "minimum_years"
                    )
          )
          # ========================================================
          # REQUIREMENT EXISTS BUT YEARS UNKNOWN
          # ========================================================
          if required_years is None:
                    return {
                              "status": "unknown",
                              "required_years": None,
                              "candidate_years": None,
                              "experience_details": [],
                    }
          # ========================================================
          # NO RESUME
          # ========================================================
          if not resume:
                    return {
                              "status": "unknown",
                              "required_years": required_years,
                              "candidate_years": None,
                              "experience_details": [],
                    }
          # ========================================================
          # RESUME EXPERIENCE
          # ========================================================
          experiences = resume.get(
                    "experience",
                    []
          )
          if not isinstance(
                    experiences,
                    list
          ):
                    experiences = []

          if not experiences:
                    return {
                            "status": "missing",
                            "required_years": required_years,
                            "candidate_years": 0.0,
                            "experience_details": [],
                    }
                            
          # ========================================================
          # INDIVIDUAL EXPERIENCE DETAILS
          # ========================================================
          experience_details = (
                    calculate_experience_details(
                              experiences
                    )
          )
          # ========================================================
          # TOTAL CANDIDATE EXPERIENCE
          # ========================================================
          candidate_years = (
                    calculate_total_experience(
                              experiences
                    )
          )
          # ========================================================
          # CANNOT DETERMINE EXPERIENCE
          # ========================================================
          if candidate_years is None:
                    return {
                              "status": "unknown",
                              "required_years": required_years,
                              "candidate_years": None,
                              "experience_details": (
                                        experience_details
                              ),
                    }
          # ========================================================
          # COMPARE CANDIDATE VS REQUIREMENT
          # ========================================================
          if candidate_years >= required_years:
                    status = "matched"
          elif candidate_years > 0:
                    status = "partial"
          else:
                    status = "missing"
          # ========================================================
          # FINAL RESULT
          # ========================================================
          return {
                    "status": status,
                    "required_years": required_years,
                    "candidate_years": candidate_years,
                    "experience_details": (
                              experience_details
                    ),
          }
