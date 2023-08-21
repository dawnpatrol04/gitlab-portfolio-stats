from fastapi import APIRouter, HTTPException
from src.value.calculate_value import get_value_over_time_for_ui

router = APIRouter()

# Savings Calculations Route ####################################################
@router.get("/value-detail/", tags=["value"])
def savings_calculations(start_date: str = '2023-01-01', end_date: str = None):
    """
    Get the savings calculations in a format suitable for CoreUI data tables.

    Args:
    - start_date (str, optional): The start date for which the savings calculations are needed. Defaults to '2023-01-01'.
    - end_date (str, optional): The end date for which the savings calculations are needed.

    Returns:
    - dict: Reformatted savings data.
    """
    try:
        reformatted_data = get_value_over_time_for_ui(start_date, end_date)
        return reformatted_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
