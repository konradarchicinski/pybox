#!/usr/bin/env python
from analyticspy.tools.task import TaskInit

import analyticspy.tools.database as atdb
import bs4
import requests
import pandas as pd
from datetime import date, datetime


def _save_log_settings(connection, conn_cursor, start_date, end_date):

    table_exists = atdb.check_if_table_exists(connection, "Settings")
    if not table_exists:
        conn_cursor.execute("""
        CREATE TABLE 'Settings'(
            id INTEGER PRIMARY KEY,
	        Setting TEXT NOT NULL,
	        SettingValue BLOB
        )
        """)
        conn_cursor.execute(f"""
        INSERT INTO 'Settings'(Setting, SettingValue)
        VALUES ('StartDate', date('{start_date.strftime('%Y-%m-%d')}')),
               ('EndDate', date('{end_date.strftime('%Y-%m-%d')}'))
        """)
    else:
        conn_cursor.execute(
            "SELECT SettingValue FROM Settings WHERE Setting = StartDate")
        last_start_date = datetime.strptime(
            conn_cursor.fetchall(), "%Y-%m-%d").date()
        if last_start_date > start_date:
            conn_cursor.execute(f"""
            REPLACE INTO Settings (Setting, SettingValue)
            VALUES('StartDate', date('{start_date.strftime('%Y-%m-%d')}'))
            """)
        conn_cursor.execute(
            "SELECT SettingValue FROM Settings WHERE Setting = EndDate")
        last_end_date = datetime.strptime(
            conn_cursor.fetchall(), "%Y-%m-%d").date()
        if last_end_date < end_date:
            conn_cursor.execute(f"""
            REPLACE INTO Settings (Setting, SettingValue)
            VALUES('EndDate', date('{end_date.strftime('%Y-%m-%d')}'))
            """)


def _insert_data_into_database(date, conn_cursor, serie):

    text_date = date.strftime("%Y-%m-%d")

    conn_cursor.execute(f"""
		INSERT INTO '{serie['EquityName']}'(
			Date,
			OpeningPrice,
			MaximumPrice,
			MinimumPrice,
			ClosingPrice,
			PriceChangePercentage,
			TradeVolume,
			Transactions,
			TurnoverValue
		)
		VALUES(
			date('{text_date}'),
			{serie['OpeningPrice']},
			{serie['MaximumPrice']},
			{serie['MinimumPrice']},
			{serie['ClosingPrice']},
			{serie['PriceChangePercentage']},
			{serie['TradeVolume']},
			{serie['Transactions']},
			{serie['TurnoverValue']}
		)
		""")


def _prepare_new_equity_in_database(connection, conn_cursor, serie):

    table_exists = atdb.check_if_table_exists(connection, serie['EquityName'])

    cur = connection.cursor()
    conn_cursor.execute("""
		CREATE TABLE IF NOT EXISTS 'EquitiesInfo'(
			EquityName TEXT PRIMARY KEY,
			ISIN TEXT,
			Currency TEXT
		)
		""")

    if not table_exists:
        conn_cursor.execute(f"""
			CREATE TABLE '{serie['EquityName']}'(
				Date TEXT PRIMARY KEY,
				OpeningPrice REAL,
				MaximumPrice REAL,
				MinimumPrice REAL,
				ClosingPrice REAL,
				PriceChangePercentage REAL,
				TradeVolume INTEGER,
				Transactions INTEGER,
				TurnoverValue INTEGER
			)
			""")
        conn_cursor.execute(f"""
			INSERT INTO 'EquitiesInfo'(
				EquityName,
				ISIN,
				Currency
			)
			VALUES(
				{serie['EquityName']},
				{serie['ISIN']},
				{serie['Currency']}
			)
			""")


def _read_achive_prices(page_address):
    """
    [summary]

    Args:
        page_address ([type]): [description]

    Returns:
        [type]: [description]
    """
    page = requests.get(page_address)
    soup = bs4.BeautifulSoup(page.text, "html.parser")

    data = []
    table = soup.find('table', {"class": "table footable"})

    if not table:
        return False

    table_columns = table.find("thead")
    columns = table_columns.find_all("th")
    column_names = [col.text.strip() for col in columns]

    rows = table.find_all('tr')
    for row in rows:
        row_values = [value.text.strip() for value in row.find_all('td')]
        if row_values:
            row_checked = [elem.replace(",", "") for elem in row_values]
            data.append(row_checked)

    tb = pd.DataFrame(data, columns=column_names)

    tb = tb.rename(columns={
        'Name': 'EquityName',
        'ISIN code': 'ISIN',
        'Currency': 'Currency',
        'Opening price': 'OpeningPrice',
        'Maximum price': 'MaximumPrice',
        'Minimum price': 'MinimumPrice',
        'Closing price': 'ClosingPrice',
        '% price change': 'PriceChangePercentage',
        'Trade volume (#)': 'TradeVolume',
        'Number of transactions': 'Transactions',
        'Turnover value (thou.)': 'TurnoverValue',
    })

    tb["TurnoverValue"] = tb["TurnoverValue"].apply(
        lambda value: float(value) * 1000)

    tb = tb.astype({
        'EquityName': str,
        'ISIN': str,
        'Currency': str,
        'OpeningPrice': float,
        'MaximumPrice': float,
        'MinimumPrice': float,
        'ClosingPrice': float,
        'PriceChangePercentage': float,
        'TradeVolume': int,
        'Transactions': int,
        'TurnoverValue': int,
    })
    return tb


def ingest_data(settings):
    """
    [summary]

    Args:
        settings ([type]): [description]
    """
    start_date = settings["StartDate"]
    end_date = settings["EndDate"]

    connection = atdb.create_connection("GPW")
    conn_cursor = connection.cursor()

    if start_date is None:
        conn_cursor.execute(
            "SELECT SettingValue FROM Settings WHERE Setting = StartDate")
        last_start_date = conn_cursor.fetchall()
        start_date = datetime.strptime(last_start_date, "%Y-%m-%d").date()
    if end_date is not date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

    date_delta = end_date - start_date
    dates_list = list()

    for i in range(date_delta.days + 1):
        day = start_date + datetime.timedelta(days=i)
        dates_list.append(day)

    for date in dates_list:
        gpw_page = "".join(["https://www.gpw.pl/",
                            "price-archive-full?type=10&instrument=&date=",
                            date.strftime("%d-%m-%Y")])
        tb = _read_achive_prices(gpw_page)

        if not isinstance(tb, bool):
            for _, row in tb.iterrows():
                _prepare_new_equity_in_database(connection, conn_cursor, row)
                _insert_data_into_database(date, conn_cursor, row)
            print(f"Handling {date} storage finished successfully.")
        else:
            print(
                f"Handling {date} storage finished unsuccessfully - No data.")

    _save_log_settings(connection, conn_cursor, start_date, end_date)

    connection.commit()
    connection.close()


task = TaskInit(
    task_name="DataIngest(GPW)",
    task_info="""
    The task is used to download and save in the database data on shares from
    the Warsaw Stock Exchange.
    """)
task.add_setting(
    name="EndDate",
    value=date.today(),
    info="""
    """)
task.add_setting(
    name="StartDate",
    value=None,
    info="""
    """)
task.run(main_function=ingest_data)
