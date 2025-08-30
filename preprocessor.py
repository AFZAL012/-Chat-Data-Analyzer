import re
import pandas as pd

def preprocess(data):
    # Covers both 12h (AM/PM) and 24h time formats
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?:\s[APap][Mm])?\s-\s'

    messages = re.split(pattern, data)[1:]   # split messages
    dates = re.findall(pattern, data)        # extract dates

    if not messages or not dates:
        return pd.DataFrame()   # return empty df if parsing fails

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Try multiple datetime formats
    date_formats = [
        "%d/%m/%y, %H:%M - ",
        "%d/%m/%Y, %H:%M - ",
        "%m/%d/%y, %H:%M - ",
        "%m/%d/%Y, %H:%M - ",
        "%d/%m/%y, %I:%M %p - ",
        "%d/%m/%Y, %I:%M %p - ",
        "%m/%d/%y, %I:%M %p - ",
        "%m/%d/%Y, %I:%M %p - ",
    ]

    for fmt in date_formats:
        try:
            df['message_date'] = pd.to_datetime(df['message_date'], format=fmt)
            break
        except:
            continue
    else:
        df['message_date'] = pd.to_datetime(df['message_date'], errors='coerce')

    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Split user & message
    users, messages = [], []
    for msg in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', msg, maxsplit=1)
        if len(entry) > 1:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Extra columns for analysis
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['month_num'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['only_date'] = df['date'].dt.date
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    return df
