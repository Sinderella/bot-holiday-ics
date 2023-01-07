import sys
from datetime import datetime
from pprint import pprint

import requests as requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event


# func to fetch calendar data from https://www.bot.or.th/English/FinancialInstitutions/FIholiday/Pages/HolidayCalendar.aspx?y=2023
def get_calendar(year_no: int):
    url = (
        "https://www.bot.or.th/English/FinancialInstitutions/FIholiday/Pages/HolidayCalendar.aspx?y="
        + str(year_no)
    )
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    tables = soup.find_all("table")
    output = {}
    for table in tables:
        output = {**output, **_get_month(table)}
    return output


# get month from table
def _get_month(table):
    month_name = table.parent.parent.find("span", class_="cal_month_text").text
    output = {month_name: []}
    rows = table.find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        holiday_day_no = [
            {ele.text.strip(): ele["title"]} for ele in cols if "title" in ele.attrs
        ]
        if not holiday_day_no:
            continue
        output[month_name] += holiday_day_no
    return output


if __name__ == "__main__":
    try:
        year = int(sys.argv[1])
    except (IndexError, ValueError):
        year = datetime.now().year

    # get calendar data
    data = get_calendar(year)

    # create calendar
    cal = Calendar()
    cal.add("prodid", "-//Thai Bank Holiday//NONSGML v1.0//EN")
    cal.add("version", "2.0")

    # add holidays to calendar
    for month, holidays in data.items():
        for holiday in holidays:
            for day_no, summary in holiday.items():
                date = datetime.strptime(f"{day_no} {month} {year}", "%d %B %Y").date()

                event = Event()
                event.add("summary", summary)
                event.add("dtstart", date)
                event.add("dtend", date)
                cal.add_component(event)

    # write calendar to file
    with open("thai bank holidays.ics", "wb") as f:
        f.write(cal.to_ical())
