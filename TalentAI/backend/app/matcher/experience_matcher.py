import re
from datetime import date
from typing import Optional


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
    "dec": 12
}


# ============================================================
# NORMALIZE DATE TEXT
# ============================================================

def normalize_date_text(text: str) -> str:

    if not text:
        return ""

    text = text.lower().strip()

    text = text.replace("–", "-")
    text = text.replace("—", "-")

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text


# ============================================================
# CHECK CURRENT / PRESENT
# ============================================================

def is_current_date(text: str) -> bool:

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
        "now"
    }

    return normalized in current_values


# ============================================================
# PARSE MONTH + YEAR
# ============================================================

def parse_month_year(
    text: str
) -> Optional[date]:

    if not text:
        return None

    text = normalize_date_text(
        text
    )

    # --------------------------------------------------------
    # Month + Year
    # --------------------------------------------------------

    match = re.search(
        r"\b("
        r"january|february|march|april|may|june|"
        r"july|august|september|october|november|december|"
        r"jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec"
        r")\s+"
        r"(19|20)\d{2}\b",
        text,
        re.IGNORECASE
    )

    if match:

        month_name = match.group(1).lower()

        year = int(
            match.group(0)[-4:]
        )

        month = MONTHS.get(
            month_name
        )

        if month:

            return date(
                year,
                month,
                1
            )

    # --------------------------------------------------------
    # Year only
    # --------------------------------------------------------

    match = re.search(
        r"\b(19|20)\d{2}\b",
        text
    )

    if match:

        year = int(
            match.group(0)
        )

        return date(
            year,
            1,
            1
        )

    return None


# ============================================================
# PARSE EXPERIENCE DATE
# ============================================================

def parse_experience_date(
    text: str
) -> Optional[date]:

    if not text:
        return None

    text = normalize_date_text(
        text
    )

    # Remove brackets
    text = text.replace(
        "[",
        ""
    ).replace(
        "]",
        ""
    )

    # Present / Current is not a calendar date
    if is_current_date(text):

        return None

    return parse_month_year(
        text
    )


# ============================================================
# CALCULATE MONTH DIFFERENCE
# ============================================================

def calculate_month_difference(
    start_date: date,
    end_date: date
) -> int:

    if not start_date or not end_date:
        return 0

    months = (
        (end_date.year - start_date.year) * 12
        + (end_date.month - start_date.month)
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

    return round(
        months / 12,
        2
    )


# ============================================================
# EXTRACT EXPERIENCE PERIOD
# ============================================================

def extract_experience_period(
    experience: dict
):

    if not isinstance(
        experience,
        dict
    ):
        return None

    dates = experience.get(
        "dates",
        {}
    )

    if not isinstance(
        dates,
        dict
    ):
        return None

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

    # --------------------------------------------------------
    # Start date is mandatory
    # --------------------------------------------------------

    if not start_text:
        return None

    start_date = parse_experience_date(
        str(start_text)
    )

    if not start_date:
        return None

    # --------------------------------------------------------
    # CURRENT EXPERIENCE
    #
    # Example:
    #
    # April 2025 - Present
    #
    # The parser should provide:
    #
    # current = True
    #
    # We calculate duration until today.
    # --------------------------------------------------------

    if current is True:

        end_date = date.today()

        if end_date < start_date:
            return None

        return {
            "start": start_date,
            "end": end_date,
            "current": True
        }

    # --------------------------------------------------------
    # EXPLICIT PRESENT / CURRENT
    #
    # Backward compatibility in case the parser gives:
    #
    # end = "Present"
    # --------------------------------------------------------

    if end_text and is_current_date(
        str(end_text)
    ):

        end_date = date.today()

        if end_date < start_date:
            return None

        return {
            "start": start_date,
            "end": end_date,
            "current": True
        }

    # --------------------------------------------------------
    # UNKNOWN END DATE
    #
    # Example:
    #
    # April 2025
    #
    # Do NOT assume Present.
    # --------------------------------------------------------

    if not end_text:

        return None

    end_date = parse_experience_date(
        str(end_text)
    )

    if not end_date:
        return None

    # --------------------------------------------------------
    # Invalid date range
    # --------------------------------------------------------

    if end_date < start_date:
        return None

    return {
        "start": start_date,
        "end": end_date,
        "current": False
    }


# ============================================================
# CALCULATE TOTAL EXPERIENCE
# ============================================================

def calculate_total_experience(
    experiences: list
) -> Optional[float]:

    if not experiences:
        return None

    periods = []

    for experience in experiences:

        period = extract_experience_period(
            experience
        )

        if period:

            periods.append(
                period
            )

    if not periods:
        return None

    # --------------------------------------------------------
    # Sort by start date
    # --------------------------------------------------------

    periods.sort(
        key=lambda x: x["start"]
    )

    # --------------------------------------------------------
    # Merge overlapping periods
    # --------------------------------------------------------

    merged = []

    for period in periods:

        if not merged:

            merged.append(
                period
            )

            continue

        previous = merged[-1]

        if period["start"] <= previous["end"]:

            if period["end"] > previous["end"]:

                previous["end"] = period["end"]

        else:

            merged.append(
                period
            )

    # --------------------------------------------------------
    # Calculate total months
    # --------------------------------------------------------

    total_months = 0

    for period in merged:

        total_months += calculate_month_difference(
            period["start"],
            period["end"]
        )

    return months_to_years(
        total_months
    )


# ============================================================
# CALCULATE INDIVIDUAL EXPERIENCE DETAILS
# ============================================================

def calculate_experience_details(
    experiences: list
) -> list:
    """
    Calculate duration information for each individual
    experience entry.

    This reuses the same date parsing logic used by
    calculate_total_experience().

    Returns:
        A list containing individual experience details.
    """

    if not experiences:
        return []

    details = []

    for experience in experiences:

        if not isinstance(
            experience,
            dict
        ):
            continue

        # ----------------------------------------------------
        # Reuse the central experience period logic
        # ----------------------------------------------------

        period = extract_experience_period(
            experience
        )

        if not period:
            continue

        start_date = period["start"]
        end_date = period["end"]

        # ----------------------------------------------------
        # Calculate individual role duration
        # ----------------------------------------------------

        duration_months = calculate_month_difference(
            start_date,
            end_date
        )

        duration_years = months_to_years(
            duration_months
        )

        # ----------------------------------------------------
        # Build detail object
        # ----------------------------------------------------

        details.append(
            {
                "job_title": experience.get(
                    "job_title"
                ),

                "company": experience.get(
                    "company"
                ),

                "location": experience.get(
                    "location"
                ),

                "start": start_date.isoformat(),

                "end": (
                    "Present"
                    if period.get("current")
                    else end_date.isoformat()
                ),

                "current": period.get(
                    "current",
                    False
                ),

                "duration_months": duration_months,

                "duration_years": duration_years
            }
        )

    return details


# ============================================================
# MATCH EXPERIENCE
# ============================================================

def match_experience(
    resume: dict,
    required_experience: dict | None
) -> dict:

    # --------------------------------------------------------
    # No experience requirement
    # --------------------------------------------------------

    if not required_experience:

        return {
            "status": "not_required",
            "required_years": None,
            "candidate_years": None,
            "experience_details": []
        }

    required_years = required_experience.get(
        "minimum_years"
    )

    # --------------------------------------------------------
    # Requirement exists but years are unknown
    # --------------------------------------------------------

    if required_years is None:

        return {
            "status": "unknown",
            "required_years": None,
            "candidate_years": None,
            "experience_details": []
        }

    # --------------------------------------------------------
    # No resume
    # --------------------------------------------------------

    if not resume:

        return {
            "status": "unknown",
            "required_years": required_years,
            "candidate_years": None,
            "experience_details": []
        }

    # --------------------------------------------------------
    # Resume experience
    # --------------------------------------------------------

    experiences = resume.get(
        "experience",
        []
    )

    # --------------------------------------------------------
    # NEW:
    # Calculate individual experience details
    #
    # This is the important fix for:
    #
    # duration_years = None
    # relevant_years = 0.0
    #
    # RelevantExperienceAnalyzer can now consume this
    # centralized result.
    # --------------------------------------------------------

    experience_details = calculate_experience_details(
        experiences
    )

    # --------------------------------------------------------
    # Calculate total candidate experience
    # --------------------------------------------------------

    candidate_years = calculate_total_experience(
        experiences
    )

    # --------------------------------------------------------
    # Cannot determine experience
    # --------------------------------------------------------

    if candidate_years is None:

        return {
            "status": "unknown",
            "required_years": required_years,
            "candidate_years": None,
            "experience_details": experience_details
        }

    # --------------------------------------------------------
    # Compare candidate vs requirement
    # --------------------------------------------------------

    if candidate_years >= required_years:

        status = "matched"

    elif candidate_years > 0:

        status = "partial"

    else:

        status = "missing"

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    return {
        "status": status,
        "required_years": required_years,
        "candidate_years": candidate_years,
        "experience_details": experience_details
    }