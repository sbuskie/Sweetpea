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
		return 'movement'
	else:
		return x



print('scraping form data')
df = main(spreadsheets)
print(df)
data = df
data['date_time'] = pd.to_datetime(data['date_time']) # this creates an odd time stamp in streamlit. Not required.
#OPTION TO WRITE TO CSV
#data.to_csv('sweetpea.csv', index = False)
st.title('Sweet Pea Movements')
st.image('./Sweet_Pea.jpg', caption='Feeling those wiggles')

st.subheader('Record wiggles here https://forms.gle/xW1HJuyCyQ4bywFU7')
st.subheader('View all wiggles')
st.write(data)
st.altair_chart(alt.Chart(data)
				.mark_rect()
				.encode(
	alt.X('hours(date_time):O', title='hour'),
	alt.Y('monthdate(date_time):O', title='day'),
	color='count(data):Q',
	tooltip=[
		alt.Tooltip('hours(date_time):O', title='hour'),
		alt.Tooltip('count(data):Q', title='Wiggle count')
	]
).properties(
	title='All the wiggles'
))

st.title("Wiggles by hour")
hour_selected = st.slider("Select hour of wiggles", 0, 23)

# FILTERING DATA BY HOUR SELECTED
data = data[data['date_time'].dt.hour == hour_selected]

# FILTERING DATA FOR THE HISTORGRAM

filtered = data[
    (data['date_time'].dt.hour >= hour_selected) & (data['date_time'].dt.hour < (hour_selected + 1))
    ]

hist = np.histogram(filtered['date_time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({"minute": range(60), "movement": hist})

#LAYING OUT THE HISTOGRAM SECTIONs

st.write("")
st.write("**Wiggles per minute between %i:00 and %i:00**" % (hour_selected, (hour_selected + 1) % 24))

st.altair_chart(alt.Chart(chart_data)
    .mark_area(
        interpolate='step-after',
    ).encode(
        x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
        y=alt.Y("movement:Q"),
        tooltip=['minute', 'movement']
    ).configure_mark(
        opacity=0.5,
        color='blue'
    ), use_container_width=True)


st.line_chart(data)
st.write(data)

