import pydeck as pdk
import datetime
import bar_chart_race as bcr
import math
import altair as alt
from altair import Chart, X, Y, Axis, SortField, OpacityValue
import plotly.figure_factory as ff
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
import time
import streamlit as st

#TODO must add secrets.toml entire text into streamlit secrets during deployment
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']


import json
key_dict = json.loads(st.secrets["textkey"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
client = gspread.authorize(creds)

#Change to your Google Sheets Name
#can add more spreadsheets as in example - spreadsheets = ['dummy_10k_response','dummy_data_pcr_test']
spreadsheets = ['Sweet Pea Movements']


def main(spreadsheets):
	df = pd.DataFrame()

	for spreadsheet in spreadsheets:
		# Open the Spreadsheet
		sh = client.open(spreadsheet)

		# Get all values in the first worksheet
		worksheet = sh.get_worksheet(0)
		data = worksheet.get_all_values()

		# Save the data inside the temporary pandas dataframe
		df_temp = pd.DataFrame(columns=[i for i in range(len(data[0]))])
		for i in range(1, len(data)):
			df_temp.loc[len(df_temp)] = data[i]

		#Convert column names
		column_names = data[0]
		df_temp.columns = [convert_column_names(x) for x in column_names]

		# Data Cleaning
		#df_temp['Response'] = df_temp['Response'].replace({'': 'Yes'})


		# Concat Dataframe
		df = pd.concat([df, df_temp])
		return df # added this line. Delete when writing to csv. Testing for combined file, trying to return function to df.

		# API Limit Handling
		time.sleep(5)

#this line below does nothing after the return df was added above. Output file outside of function
	#df.to_csv('10k_survey_google_output.csv', index=False)

def convert_column_names(x):
	if x == 'Timestamp':
		return 'date_time'
	elif x == 'Yes, I felt movements':
		return 'Movement'
	else:
		return x



print('scraping form data')
df = main(spreadsheets)
print(df)
raw_data = df
df['date_time'] = pd.to_datetime(df['date_time'])

st.title('Sweet Pea Movements')
st.image('./Sweet_Pea.jpg', caption='Feeling those wiggles')

st.subheader('Record wiggles here https://forms.gle/xW1HJuyCyQ4bywFU7')

st.write(df)

