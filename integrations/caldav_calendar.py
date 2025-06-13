from caldav import DAVClient
from caldav.lib.error import DAVError
from datetime import datetime, timedelta

def handle_caldav_action(creds: dict, nlu_data: dict) -> str:
    """Handles CalDAV actions based on NLU intent and entities."""
    if not creds or not all(k in creds for k in ['url', 'user', 'password']):
        return "CalDAV credentials are not set or are incomplete. Please configure them in the settings (⚙️ icon)."

    url = creds['url']
    username = creds['user']
    password = creds['password']
    
    intent = nlu_data.get('intent')

    try:
        with DAVClient(url=url, username=username, password=password) as client:
            principal = client.principal()
            calendars = principal.calendars()
            
            if not calendars:
                return "No calendars were found for your account. Please check your CalDAV setup."
            
            # For simplicity, we'll use the first calendar found.
            # A more advanced version could let the user specify which calendar to use.
            calendar = calendars[0]

            if intent == 'get_calendar_events':
                # Default to today's events, but can be expanded with NLU entities for date ranges
                start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date + timedelta(days=1)
                
                return _get_events_for_range(calendar, start_date, end_date)

    except DAVError as e:
        print(f"CalDAV Error: Could not connect or authenticate with {url}. Details: {e}")
        # Check for common HTTP status codes if possible from the error
        # (This part is library-dependent and may need adjustment)
        if '401' in str(e):
             return f"Authentication failed for CalDAV server at {url}. Please check your username and password."
        if '404' in str(e):
            return f"Could not find a CalDAV service at the specified URL: {url}. Please check the server address."
        return f"Sorry, I encountered an error trying to connect to your calendar server at {url}."
    except Exception as e:
        print(f"An unexpected error occurred during CalDAV handling: {e}")
        return "An unexpected error occurred while accessing your calendar."

def _get_events_for_range(calendar, start_date, end_date) -> str:
    """Helper function to get and format events from a given calendar and date range."""
    try:
        events_found = calendar.date_search(start=start_date, end=end_date, expand=True)
        
        if not events_found:
            return f"No events found for {start_date.strftime('%A, %B %d, %Y')}."

        response_lines = [f"Here are your events for {start_date.strftime('%A, %B %d')}:"]
        
        # Sort events by start time
        sorted_events = sorted(events_found, key=lambda e: e.vobject_instance.vevent.dtstart.value)

        for event in sorted_events:
            vevent = event.vobject_instance.vevent
            summary = vevent.summary.value
            
            # Handle both datetime and date objects for start/end times
            dt_start = vevent.dtstart.value
            dt_end = vevent.dtend.value

            if isinstance(dt_start, datetime):
                # Format for events with specific times
                start_str = dt_start.strftime('%I:%M %p')
                end_str = dt_end.strftime('%I:%M %p')
                if dt_start.date() != dt_end.date():
                    # Handle multi-day events
                    response_lines.append(f"- {summary} (from {dt_start.strftime('%b %d, %I:%M %p')} to {dt_end.strftime('%b %d, %I:%M %p')})")
                else:
                    response_lines.append(f"- {summary} ({start_str} - {end_str})")
            else:
                # Format for all-day events
                response_lines.append(f"- {summary} (All day)")
        
        return "\n".join(response_lines)

    except Exception as e:
        print(f"Error searching for events in calendar '{calendar.name}': {e}")
        return f"Sorry, I had trouble searching for events in your '{calendar.name}' calendar." 