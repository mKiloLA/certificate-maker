import pandas as pd
from typing import Any
import openpyxl

from certificate_maker.src.data.on_demand.report_entry import ReportEntry
from certificate_maker.src.data.ref import us_state_to_abbrev
from certificate_maker.src.exception_types import MissingSubmissionData, MissingEvaluationData, MalformedCROString, MalformedEvaluationQuestionResponse, ReferenceFileMissingSheet, RefereneFileMissingCourse


def _abbreviate_rating(rating: Any) -> str:
    """
    Convert a rating string to abbreviated form using first letter of each word.
    Example: "Exceeded Expectation" -> "EE", "Met Expectation" -> "ME"
    """
    if pd.isna(rating) or not rating:
        return ""
    
    try:
        rating_str = str(rating).strip()
        words = rating_str.split()
        abbreviated = "".join(word[0].upper() for word in words if word)
        return abbreviated
    except Exception:
        raise MalformedEvaluationQuestionResponse(rating)


def _parse_evaluation_info(row: pd.Series, rating_columns: list[str]) -> str | None:
    """
    Extract course evaluation from row by abbreviating all "Please rate..." responses.
    Abbreviates each response by taking the first letter of each word.
    Example: "Exceeded Expectation" -> "EE", "Met Expectation" -> "ME"
    Returns comma-separated abbreviations, or None if no data.
    """
    try:
        abbreviations: list[str] = [
            _abbreviate_rating(row.get(col)) for col in rating_columns
        ]
        # Filter out empty strings and join with ", "
        result = ", ".join(abbr for abbr in abbreviations if abbr)
        return result if result else None
    except Exception as e:
        raise MalformedEvaluationQuestionResponse(e)

def _parse_cro_info(cro_string: Any) -> list[tuple[str, str]]:
    """
    Extract all state and bar number pairs from CRO string.
    Format: "State: BarNumber - Hours" or multiple entries separated by ", "
    Example: "Georgia: 289725 - 2 hours" -> [("GA", "289725")]
    Example: "Tennessee: 017801 - 1 hours, Tennessee: 017801 - 2 hours" -> [("TN", "017801")]
    Returns list of tuples, deduped by state.
    """
    if pd.isna(cro_string) or not cro_string:
        return []
    
    try:
        cro_str = str(cro_string).strip()
        entries: list[tuple[str, str]] = []
        seen_states: set[str] = set()
        
        # Split by comma and space to get individual entries
        for entry_text in cro_str.split(", "):
            entry_text = entry_text.strip()
            if not entry_text:
                continue
            
            # Split by colon to get state name and rest
            parts = entry_text.split(":")
            if len(parts) < 2:
                continue
            
            state_name = parts[0].strip()
            # Find the state abbreviation
            state_abbrev = us_state_to_abbrev.get(state_name)
            
            # Skip if we've already seen this state
            if state_abbrev in seen_states:
                continue
            
            # Extract bar number from the second part
            bar_part = parts[1].split("-")[0].strip()
            
            if state_abbrev and bar_part:
                entries.append((state_abbrev, bar_part))
                seen_states.add(state_abbrev)
        
        return entries
    except Exception:
        raise MalformedCROString(cro_string)


def create_on_demand_report(
    attendance_file: str, evaluation_file: str, reference_file: str
) -> None:
    """Creates a list of ReportEntry objects from the on-demand report."""
    # Read attendance file
    attendance_df: pd.DataFrame = pd.read_csv(attendance_file)
    
    report_entries: list[ReportEntry] = []
    
    for _, row in attendance_df.iterrows():
        # Extract state and bar number from CRO string
        cro_entries: list[tuple[str, str]] = _parse_cro_info(row.get("Submitted CRO (Member Number) and Hours"))

        # Split course title on last colon and take everything before it
        course_title: Any = row.get("Chapter Title")
        if course_title and ':' in course_title:
            course_title = course_title.rsplit(':', 1)[0]
        
        # Iterate through each state and bar number pair to create a ReportEntry for each
        for state, bar_number in cro_entries:
            entry: ReportEntry = ReportEntry(
                first_name=row.get("First Name"),
                last_name=row.get("Last Name"),
                email=row.get("Email"),
                state=state,
                bar_number=bar_number,
                course_title=course_title,
                course_completed_date=row.get("Date Submitted")
            )
            report_entries.append(entry)
    
    del attendance_df  # Free memory

    # Read evaluation file
    evaluation_df: pd.DataFrame = pd.read_csv(evaluation_file)
    
    # Get all columns that start with "Please rate" plus the recommendation column
    rating_columns: list[str] = [col for col in evaluation_df.columns if col.startswith("Please rate")]
    if "Would you recommend Comedian of Law to others?" in evaluation_df.columns:
        rating_columns.append("Would you recommend Comedian of Law to others?")

    # Compare email and course title to find the evaluation for each report entry
    # There may be multiple entries with the same email and course title and we want to update all of them that match
    for _, row in evaluation_df.iterrows():
        email = row.get("Email")
        course_title = row.get("Course Title")
        course_evaluation = _parse_evaluation_info(row, rating_columns)

        # Track if we found a match
        found_match = False
        for entry in report_entries:
            if entry.email == email and entry.course_title == course_title:
                entry.course_evaluation = course_evaluation
                found_match = True
        
        # Raise error if no matching entry was found
        if not found_match:
            raise MissingSubmissionData(email, course_title)
        
    del evaluation_df  # Free memory

    # Now we need to compare the report entries to the reference file to find the course ID and hours for each ent
    for entry in report_entries:
        # Check that we have evaluation data for the entry, if not raise error
        if entry.course_evaluation is None:
            raise MissingEvaluationData(entry.email, entry.course_title)
        
        # Iterate through each sheet in the reference file to find a matching course title and evaluation
        found_match = False
        sheet_name = f"{entry.state} - Yes"  # Sheet name format is "State - Yes"

        if sheet_name in pd.ExcelFile(reference_file).sheet_names:
            sheet_df = pd.read_excel(reference_file, sheet_name=sheet_name)

            # Find the last row where column C (index 2) matches the course title
            matches = sheet_df[sheet_df.iloc[:, 2].astype(str).str.strip() == entry.course_title.strip()]

            if not matches.empty:
                last_match = matches.iloc[-1]
                entry.course_id = last_match.iloc[5]
                entry.course_hours = last_match.iloc[6]
            else:
                raise RefereneFileMissingCourse((sheet_name, entry.course_title))
        else:
            raise ReferenceFileMissingSheet(entry.state)
        
    print(f"Report generation complete! Generated {len(report_entries)} entries.")
