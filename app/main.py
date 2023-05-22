import sys
from datetime import datetime

import requests as requests
from icalendar import Calendar, Event


# func to fetch calendar data from https://www.bot.or.th/content/bot/en/financial-institutions-holiday/jcr:content/root/container/holidaycalendar.model.2023.json
def get_calendar(year_no: int) -> dict[datetime, str]:
    url = f"https://www.bot.or.th/content/bot/en/financial-institutions-holiday/jcr:content/root/container/holidaycalendar.model.{year_no}.json"

    page = requests.get(url)
    content = page.json()["holidayCalendarLists"]

    output = {}

    for item in content:
        description = item["holidayDescription"].strip()
        date_no = item["date"].split(" ")[-1].strip()
        month = item["month"].strip()
        year = item["year"].strip()

        if year != str(year_no):
            raise RuntimeError("Year no does not match")

        parsed_date = datetime.strptime(f"{date_no} {month} {year}", "%d %B %Y").date()
        output[parsed_date] = description

    return output


def generate_uid(date: datetime) -> str:
    return f"BOT-{date.strftime('%Y%m%d')}"


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
    for date, summary in data.items():
        event = Event()
        event.add("summary", summary)
        event.add("dtstart", date)
        event.add("dtend", date)
        event.add("dtstamp", datetime.now())
        event.add("uid", generate_uid(date))
        cal.add_component(event)

    # write calendar to file
    with open("thai bank holidays.ics", "wb") as f:
        f.write(cal.to_ical())
