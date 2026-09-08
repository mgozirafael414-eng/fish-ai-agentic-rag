# backend/app/agents/time_agent.py

from datetime import datetime
from zoneinfo import ZoneInfo
import re


# ============================================================
# TIMEZONE MAP
# ============================================================

TIMEZONE_MAP = {

    # ========================================================
    # TANZANIA
    # ========================================================

    "tanzania": ("Africa/Dar_es_Salaam", "Tanzania"),
    "tz": ("Africa/Dar_es_Salaam", "Tanzania"),
    "dar es salaam": ("Africa/Dar_es_Salaam", "Dar es Salaam"),
    "dar": ("Africa/Dar_es_Salaam", "Dar es Salaam"),
    "dodoma": ("Africa/Dar_es_Salaam", "Dodoma"),
    "mbeya": ("Africa/Dar_es_Salaam", "Mbeya"),
    "arusha": ("Africa/Dar_es_Salaam", "Arusha"),
    "mwanza": ("Africa/Dar_es_Salaam", "Mwanza"),
    "zanzibar": ("Africa/Dar_es_Salaam", "Zanzibar"),

    # ========================================================
    # EAST AFRICA
    # ========================================================

    "kenya": ("Africa/Nairobi", "Kenya"),
    "nairobi": ("Africa/Nairobi", "Nairobi"),

    "uganda": ("Africa/Kampala", "Uganda"),
    "kampala": ("Africa/Kampala", "Kampala"),

    "rwanda": ("Africa/Kigali", "Rwanda"),
    "kigali": ("Africa/Kigali", "Kigali"),

    "burundi": ("Africa/Bujumbura", "Burundi"),
    "bujumbura": ("Africa/Bujumbura", "Bujumbura"),

    "ethiopia": ("Africa/Addis_Ababa", "Ethiopia"),
    "addis ababa": ("Africa/Addis_Ababa", "Addis Ababa"),

    # ========================================================
    # OTHER AFRICA
    # ========================================================

    "south africa": (
        "Africa/Johannesburg",
        "South Africa"
    ),

    "johannesburg": (
        "Africa/Johannesburg",
        "Johannesburg"
    ),

    "nigeria": ("Africa/Lagos", "Nigeria"),
    "lagos": ("Africa/Lagos", "Lagos"),

    "ghana": ("Africa/Accra", "Ghana"),
    "accra": ("Africa/Accra", "Accra"),

    "egypt": ("Africa/Cairo", "Egypt"),
    "cairo": ("Africa/Cairo", "Cairo"),

    # ========================================================
    # EUROPE
    # ========================================================

    "london": ("Europe/London", "London"),
    "uk": ("Europe/London", "United Kingdom"),
    "england": ("Europe/London", "England"),

    "france": ("Europe/Paris", "France"),
    "paris": ("Europe/Paris", "Paris"),

    "germany": ("Europe/Berlin", "Germany"),
    "berlin": ("Europe/Berlin", "Berlin"),

    # ========================================================
    # NORTH AMERICA
    # ========================================================

    "new york": (
        "America/New_York",
        "New York"
    ),

    "usa": (
        "America/New_York",
        "USA"
    ),

    "america": (
        "America/New_York",
        "USA"
    ),

    "los angeles": (
        "America/Los_Angeles",
        "Los Angeles"
    ),

    # ========================================================
    # ASIA
    # ========================================================

    "india": ("Asia/Kolkata", "India"),
    "mumbai": ("Asia/Kolkata", "Mumbai"),
    "delhi": ("Asia/Kolkata", "Delhi"),

    "china": ("Asia/Shanghai", "China"),
    "shanghai": ("Asia/Shanghai", "Shanghai"),
    "beijing": ("Asia/Shanghai", "Beijing"),

    "japan": ("Asia/Tokyo", "Japan"),
    "tokyo": ("Asia/Tokyo", "Tokyo"),

    "dubai": ("Asia/Dubai", "Dubai"),
    "uae": ("Asia/Dubai", "UAE"),
}


# ============================================================
# FIND TIMEZONE
# ============================================================

def detect_timezone(user_message: str):
    """
    Detect timezone and location from the user's message.

    Returns:
        (timezone_name, location)
    """

    message = user_message.lower().strip()

    for keyword in sorted(
        TIMEZONE_MAP,
        key=len,
        reverse=True
    ):
        if keyword in message:

            timezone_name, location = TIMEZONE_MAP[keyword]

            return timezone_name, location

    return (
        "Africa/Dar_es_Salaam",
        "Tanzania"
    )


# ============================================================
# FIND ALL LOCATIONS
# ============================================================

def detect_all_locations(user_message: str):
    """
    Detect all recognized locations mentioned
    in the user's message.

    Returns:
        list of dictionaries
    """

    message = user_message.lower().strip()

    detected = []

    for keyword in sorted(
        TIMEZONE_MAP,
        key=len,
        reverse=True
    ):

        if keyword in message:

            timezone_name, location = TIMEZONE_MAP[keyword]

            item = {
                "keyword": keyword,
                "timezone": timezone_name,
                "location": location,
            }

            # Prevent duplicate timezone/location entries
            if not any(
                existing["timezone"] == timezone_name
                and existing["location"] == location
                for existing in detected
            ):
                detected.append(item)

    return detected


# ============================================================
# DETECT TIME REQUEST TYPE
# ============================================================

def detect_time_request_type(user_message: str) -> str:
    """
    Detect:

        TIME_ONLY
        DATE_ONLY
        TIME_AND_DATE
        CONVERSION
        COMPARISON
    """

    message = user_message.lower().strip()

    # ========================================================
    # CONVERSION KEYWORDS
    # ========================================================

    conversion_keywords = [

        # English
        "convert",
        "conversion",
        "convert time",
        "change time",
        "from",
        "to",
        "in tanzania",
        "in kenya",
        "in london",
        "in new york",

        # Swahili
        "badilisha",
        "geuza",
        "kutoka",
        "kwenda",
    ]

    # ========================================================
    # COMPARISON KEYWORDS
    # ========================================================

    comparison_keywords = [

        # English
        "compare",
        "comparison",
        "difference between",
        "time difference",
        "what is the difference",
        "both times",
        "times in",

        # Swahili
        "linganisha",
        "tofauti ya muda",
        "tofauti kati ya",
        "saa zao",
    ]

    if any(
        keyword in message
        for keyword in comparison_keywords
    ):
        return "COMPARISON"

    if any(
        keyword in message
        for keyword in conversion_keywords
    ):

        # Only classify as conversion when
        # there are at least two locations.
        locations = detect_all_locations(message)

        if len(locations) >= 2:
            return "CONVERSION"

    # ========================================================
    # DATE KEYWORDS
    # ========================================================

    date_keywords = [

        "today's date",
        "todays date",
        "current date",
        "what date is it",
        "what is the date",
        "what is today's date",
        "what day is today",
        "which day is today",

        "time and date",
        "date and time",
        "current time and date",
        "current date and time",

        # Swahili
        "tarehe ya leo",
        "leo ni tarehe gani",
        "leo tarehe gani",
        "tarehe gani leo",
        "leo ni siku gani",
        "ni siku gani leo",
        "siku gani leo",
    ]

    # ========================================================
    # TIME KEYWORDS
    # ========================================================

    time_keywords = [

        "what time is it",
        "what's the time",
        "current time",
        "what is the current time",
        "what is the time",
        "what time is it now",
        "time now",
        "time right now",
        "tell me the time",
        "show me the time",
        "exact time",
        "local time",

        # Swahili
        "saa ngapi",
        "saa ngapi sasa",
        "ni saa ngapi",
        "ni saa ngapi sasa",
        "muda wa sasa",
        "muda gani sasa",
        "wakati gani sasa",
        "saa ya sasa",
    ]

    has_date = any(
        keyword in message
        for keyword in date_keywords
    )

    has_time = any(
        keyword in message
        for keyword in time_keywords
    )

    if has_time and has_date:
        return "TIME_AND_DATE"

    if has_date:
        return "DATE_ONLY"

    if has_time:
        return "TIME_ONLY"

    return "TIME_ONLY"


# ============================================================
# DETECT TIME FORMAT
# ============================================================

def detect_time_format(user_message: str) -> str:
    """
    Detect:

        12H
        24H
    """

    message = user_message.lower().strip()

    twelve_hour_keywords = [

        "12 hour",
        "12-hour",
        "12 hours",
        "am pm",
        "am/pm",
        "a.m.",
        "p.m.",
        "12h",

        # Swahili
        "mfumo wa saa 12",
        "saa 12",
        "masaa 12",
    ]

    twenty_four_hour_keywords = [

        "24 hour",
        "24-hour",
        "24 hours",
        "24h",
        "military time",

        # Swahili
        "mfumo wa saa 24",
        "saa 24",
        "masaa 24",
    ]

    if any(
        keyword in message
        for keyword in twelve_hour_keywords
    ):
        return "12H"

    if any(
        keyword in message
        for keyword in twenty_four_hour_keywords
    ):
        return "24H"

    return "24H"


# ============================================================
# EXTRACT TIME FROM USER MESSAGE
# ============================================================

def extract_time_from_message(user_message: str):
    """
    Extract a time such as:

        10:00
        10:30
        10:30 AM
        8 PM
        08:15:00
    """

    message = user_message.lower().strip()

    # --------------------------------------------------------
    # HH:MM:SS AM/PM
    # --------------------------------------------------------

    pattern_1 = re.search(
        r"\b(\d{1,2}):(\d{2}):(\d{2})\s*(am|pm)\b",
        message
    )

    if pattern_1:

        hour = int(pattern_1.group(1))
        minute = int(pattern_1.group(2))
        second = int(pattern_1.group(3))
        period = pattern_1.group(4).upper()

        return hour, minute, second, period

    # --------------------------------------------------------
    # HH:MM AM/PM
    # --------------------------------------------------------

    pattern_2 = re.search(
        r"\b(\d{1,2}):(\d{2})\s*(am|pm)\b",
        message
    )

    if pattern_2:

        hour = int(pattern_2.group(1))
        minute = int(pattern_2.group(2))
        period = pattern_2.group(3).upper()

        return hour, minute, 0, period

    # --------------------------------------------------------
    # HH AM/PM
    # --------------------------------------------------------

    pattern_3 = re.search(
        r"\b(\d{1,2})\s*(am|pm)\b",
        message
    )

    if pattern_3:

        hour = int(pattern_3.group(1))
        period = pattern_3.group(2).upper()

        return hour, 0, 0, period

    # --------------------------------------------------------
    # 24-hour HH:MM
    # --------------------------------------------------------

    pattern_4 = re.search(
        r"\b(\d{1,2}):(\d{2})\b",
        message
    )

    if pattern_4:

        hour = int(pattern_4.group(1))
        minute = int(pattern_4.group(2))

        return hour, minute, 0, None

    return None


# ============================================================
# NORMALIZE TIME
# ============================================================

def normalize_time(
    hour: int,
    minute: int,
    second: int = 0,
    period=None,
):
    """
    Convert extracted time into a valid datetime time.

    Returns:
        hour, minute, second
    """

    if period:

        if period == "PM" and hour != 12:
            hour += 12

        elif period == "AM" and hour == 12:
            hour = 0

    if not (
        0 <= hour <= 23
        and 0 <= minute <= 59
        and 0 <= second <= 59
    ):
        return None

    return hour, minute, second


# ============================================================
# CONVERT TIME BETWEEN TIMEZONES
# ============================================================

def convert_time_between_timezones(
    source_datetime: datetime,
    source_timezone: str,
    target_timezone: str,
) -> datetime:
    """
    Convert datetime from source timezone
    to target timezone.
    """

    source_zone = ZoneInfo(source_timezone)

    localized_datetime = source_datetime.replace(
        tzinfo=source_zone
    )

    target_zone = ZoneInfo(target_timezone)

    converted_datetime = localized_datetime.astimezone(
        target_zone
    )

    return converted_datetime


# ============================================================
# GET UTC OFFSET
# ============================================================

def get_utc_offset(now: datetime) -> str:
    """
    Convert:

        +0300 -> UTC+03:00
        +0100 -> UTC+01:00
        -0400 -> UTC-04:00
    """

    utc_offset = now.strftime("%z")

    if len(utc_offset) == 5:

        utc_offset = (
            utc_offset[:3]
            + ":"
            + utc_offset[3:]
        )

    return f"UTC{utc_offset}"


# ============================================================
# CHECK DAYLIGHT SAVING TIME
# ============================================================

def is_dst_active(now: datetime) -> bool:
    """
    Check whether DST is active.
    """

    dst = now.dst()

    if dst is None:
        return False

    return dst.total_seconds() != 0


# ============================================================
# FORMAT TIME
# ============================================================

def format_time(
    value: datetime,
    request_format: str
) -> str:

    if request_format == "12H":

        return value.strftime(
            "%I:%M:%S %p"
        )

    return value.strftime(
        "%H:%M:%S"
    )


# ============================================================
# DETECT LANGUAGE
# ============================================================

def detect_language(user_message: str) -> str:
    """
    Returns:

        sw
        en
    """

    swahili_words = [

        "saa",
        "muda",
        "wakati",
        "leo",
        "tarehe",
        "siku",

        "tanzania",
        "kenya",
        "uganda",
        "rwanda",
        "burundi",

        "badilisha",
        "geuza",
        "kutoka",
        "kwenda",
        "linganisha",
        "tofauti",
    ]

    message_lower = user_message.lower()

    if any(
        word in message_lower
        for word in swahili_words
    ):
        return "sw"

    return "en"


# ============================================================
# CONVERSION RESPONSE
# ============================================================

def build_conversion_response(
    user_message: str,
    source_datetime: datetime,
    source_timezone: str,
    source_location: str,
    target_timezone: str,
    target_location: str,
) -> str:

    language = detect_language(user_message)

    request_format = detect_time_format(
        user_message
    )

    converted_datetime = convert_time_between_timezones(
        source_datetime,
        source_timezone,
        target_timezone,
    )

    source_time = format_time(
        source_datetime,
        request_format
    )

    target_time = format_time(
        converted_datetime,
        request_format
    )

    source_offset = get_utc_offset(
        source_datetime.replace(
            tzinfo=ZoneInfo(source_timezone)
        )
    )

    target_offset = get_utc_offset(
        converted_datetime
    )

    if language == "sw":

        return (
            f"🕐 **Time Conversion**\n\n"
            f"📍 Kutoka: **{source_location}**\n"
            f"🕐 Muda: **{source_time}**\n"
            f"🌍 UTC Offset: **{source_offset}**\n\n"
            f"➡️ Kwenda: **{target_location}**\n"
            f"🕐 Muda: **{target_time}**\n"
            f"🌍 UTC Offset: **{target_offset}**\n\n"
            f"🌍 Timezone: **{target_timezone}**\n"
            f"🕐 Format: **{request_format}**"
        )

    return (
        f"🕐 **Time Conversion**\n\n"
        f"📍 From: **{source_location}**\n"
        f"🕐 Time: **{source_time}**\n"
        f"🌍 UTC Offset: **{source_offset}**\n\n"
        f"➡️ To: **{target_location}**\n"
        f"🕐 Time: **{target_time}**\n"
        f"🌍 UTC Offset: **{target_offset}**\n\n"
        f"🌍 Timezone: **{target_timezone}**\n"
        f"🕐 Format: **{request_format}**"
    )


# ============================================================
# TIME COMPARISON
# ============================================================

def build_comparison_response(
    user_message: str,
    locations: list,
) -> str:
    """
    Compare current times for multiple locations.
    """

    request_format = detect_time_format(
        user_message
    )

    language = detect_language(
        user_message
    )

    results = []

    for item in locations:

        timezone_name = item["timezone"]
        location = item["location"]

        now = datetime.now(
            ZoneInfo(timezone_name)
        )

        current_time = format_time(
            now,
            request_format
        )

        utc_offset = get_utc_offset(now)

        results.append({
            "location": location,
            "timezone": timezone_name,
            "time": current_time,
            "offset": utc_offset,
        })

    if language == "sw":

        response = (
            "🌍 **Ulinganisho wa muda**\n\n"
        )

        for result in results:

            response += (
                f"📍 **{result['location']}**\n"
                f"🕐 Muda: **{result['time']}**\n"
                f"🌍 UTC Offset: **{result['offset']}**\n"
                f"Timezone: **{result['timezone']}**\n\n"
            )

        return response

    response = (
        "🌍 **Time Comparison**\n\n"
    )

    for result in results:

        response += (
            f"📍 **{result['location']}**\n"
            f"🕐 Time: **{result['time']}**\n"
            f"🌍 UTC Offset: **{result['offset']}**\n"
            f"Timezone: **{result['timezone']}**\n\n"
        )

    return response


# ============================================================
# TIME AGENT
# ============================================================

async def time_agent(
    user_message: str,
    conversation=None,
) -> str:
    """
    FishAI Time Agent.

    Supports:

    1. Current time
    2. Current date
    3. Time + date
    4. Timezone detection
    5. UTC offset
    6. DST detection
    7. 12H / 24H format
    8. Time conversion
    9. Multiple timezone comparison
    10. English / Swahili
    """

    # ========================================================
    # DETECT LANGUAGE
    # ========================================================

    language = detect_language(
        user_message
    )

    # ========================================================
    # DETECT REQUEST TYPE
    # ========================================================

    request_type = detect_time_request_type(
        user_message
    )

    # ========================================================
    # DETECT LOCATIONS
    # ========================================================

    locations = detect_all_locations(
        user_message
    )

    # ========================================================
    # COMPARISON
    # ========================================================

    if request_type == "COMPARISON":

        if len(locations) >= 2:

            return build_comparison_response(
                user_message,
                locations,
            )

    # ========================================================
    # CONVERSION
    # ========================================================

    if request_type == "CONVERSION":

        if len(locations) >= 2:

            source_location_data = locations[0]
            target_location_data = locations[1]

            source_timezone = (
                source_location_data["timezone"]
            )

            source_location = (
                source_location_data["location"]
            )

            target_timezone = (
                target_location_data["timezone"]
            )

            target_location = (
                target_location_data["location"]
            )

            extracted_time = extract_time_from_message(
                user_message
            )

            if extracted_time:

                hour, minute, second, period = (
                    extracted_time
                )

                normalized = normalize_time(
                    hour,
                    minute,
                    second,
                    period,
                )

                if normalized:

                    hour, minute, second = normalized

                    source_datetime = datetime(
                        2026,
                        1,
                        1,
                        hour,
                        minute,
                        second,
                    )

                    return build_conversion_response(
                        user_message,
                        source_datetime,
                        source_timezone,
                        source_location,
                        target_timezone,
                        target_location,
                    )

            # ------------------------------------------------
            # No explicit time supplied
            # Use current source time.
            # ------------------------------------------------

            source_now = datetime.now(
                ZoneInfo(source_timezone)
            )

            return build_conversion_response(
                user_message,
                source_now.replace(tzinfo=None),
                source_timezone,
                source_location,
                target_timezone,
                target_location,
            )

    # ========================================================
    # CURRENT TIME / DATE
    # ========================================================

    timezone_name, location = detect_timezone(
        user_message
    )

    # ========================================================
    # CURRENT TIME
    # ========================================================

    now = datetime.now(
        ZoneInfo(timezone_name)
    )

    # ========================================================
    # UTC OFFSET
    # ========================================================

    utc_offset_display = get_utc_offset(
        now
    )

    # ========================================================
    # DST
    # ========================================================

    dst_active = is_dst_active(
        now
    )

    if dst_active:

        dst_status = "Active"

    else:

        dst_status = "Not active"

    # ========================================================
    # TIME FORMAT
    # ========================================================

    request_format = detect_time_format(
        user_message
    )

    # ========================================================
    # FORMAT TIME
    # ========================================================

    current_time = format_time(
        now,
        request_format
    )

    # ========================================================
    # FORMAT DATE
    # ========================================================

    current_date = now.strftime(
        "%A, %d %B %Y"
    )

    # ========================================================
    # SWAHILI RESPONSE
    # ========================================================

    if language == "sw":

        # ----------------------------------------------------
        # DATE ONLY
        # ----------------------------------------------------

        if request_type == "DATE_ONLY":

            return (
                f"📅 **Tarehe ya leo {location}**\n\n"
                f"Leo ni **{current_date}**.\n\n"
                f"🌍 Timezone: **{timezone_name}**\n"
                f"🕐 UTC Offset: **{utc_offset_display}**\n"
                f"☀️ DST: **{dst_status}**"
            )

        # ----------------------------------------------------
        # TIME + DATE
        # ----------------------------------------------------

        if request_type == "TIME_AND_DATE":

            return (
                f"🕐 **Muda na tarehe ya sasa {location}**\n\n"
                f"Kwa sasa ni **{current_time}**.\n\n"
                f"📅 Tarehe: **{current_date}**\n"
                f"🌍 Timezone: **{timezone_name}**\n"
                f"🕐 UTC Offset: **{utc_offset_display}**\n"
                f"☀️ DST: **{dst_status}**\n"
                f"🕐 Format: **{request_format}**"
            )

        # ----------------------------------------------------
        # TIME ONLY
        # ----------------------------------------------------

        return (
            f"🕐 **Muda wa sasa {location}**\n\n"
            f"Kwa sasa ni **{current_time}**.\n\n"
            f"🌍 Timezone: **{timezone_name}**\n"
            f"🕐 UTC Offset: **{utc_offset_display}**\n"
            f"☀️ DST: **{dst_status}**\n"
            f"🕐 Format: **{request_format}**"
        )

    # ========================================================
    # ENGLISH RESPONSE
    # ========================================================

    # --------------------------------------------------------
    # DATE ONLY
    # --------------------------------------------------------

    if request_type == "DATE_ONLY":

        return (
            f"📅 **Today's date in {location}**\n\n"
            f"Today is **{current_date}**.\n\n"
            f"🌍 Timezone: **{timezone_name}**\n"
            f"🕐 UTC Offset: **{utc_offset_display}**\n"
            f"☀️ DST: **{dst_status}**"
        )

    # --------------------------------------------------------
    # TIME + DATE
    # --------------------------------------------------------

    if request_type == "TIME_AND_DATE":

        return (
            f"🕐 **Current time and date in {location}**\n\n"
            f"The current time is **{current_time}**.\n\n"
            f"📅 Date: **{current_date}**\n"
            f"🌍 Timezone: **{timezone_name}**\n"
            f"🕐 UTC Offset: **{utc_offset_display}**\n"
            f"☀️ DST: **{dst_status}**\n"
            f"🕐 Format: **{request_format}**"
        )

    # --------------------------------------------------------
    # TIME ONLY
    # --------------------------------------------------------

    return (
        f"🕐 **Current time in {location}**\n\n"
        f"The current time is **{current_time}**.\n\n"
        f"🌍 Timezone: **{timezone_name}**\n"
        f"🕐 UTC Offset: **{utc_offset_display}**\n"
        f"☀️ DST: **{dst_status}**\n"
        f"🕐 Format: **{request_format}**"
    )