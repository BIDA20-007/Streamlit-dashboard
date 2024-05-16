import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64
import pydeck as pdk
import time 
import requests
import warnings
warnings.filterwarnings('ignore')

# Function to fetch data from the API
def fetch_api_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()  # Convert response to JSON format
            return data
        else:
            st.error(f"Failed to fetch data from API. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error occurred while fetching data from API: {e}")
        return None
 
# API URL
api_url = "http://127.0.0.1:5000/api/data"
st.set_page_config(page_title="Fun Olympics Broadcasting Performance Dashboard",
                   page_icon =":bar_chart:",
                   layout="wide"
)


# Rest of your Streamlit app code...
 
# After defining your Streamlit app components, decide where you want to call the function to fetch API data.
# You can add a button or a checkbox to trigger the API data fetch, or fetch data automatically when the app starts.
# For example, you can place the function call within the 'if uploaded_file is not None:' block:
 
# Define the rest of your Streamlit app components...

#https://www.webfx.com/tools/emoji-cheat-sheet/
# Set wide layout for the page

# Add a title to the dashboard
st.title(":bar_chart: Broadcasting Performance Dashboard")

# Load streaming_data from CSV
streaming_data = pd.read_csv("streaming_data.csv")

# Convert 'Date' column to datetime objects
streaming_data["Date"] = pd.to_datetime(streaming_data["Date"])

# Define custom CSS styles
kpi_card_style = """
      background-color: #032545;
      padding: 20px;
      border-radius: 10px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      width: 250px;
      height: 150px;
      margin-bottom: 20px;
"""
# Add logo or picture to the sidebar at the top
st.sidebar.image("Analytics.png", use_column_width=True)


# Apply custom styling to the sidebar
st.sidebar.header("Filters")

# Sidebar filter for countries
all_countries = ["All"] + list(streaming_data["Country"].unique())
selected_country = st.sidebar.selectbox("Country", all_countries, index=0, format_func=lambda x: "Select Country" if x == "All" else x)

# Sidebar filter for events
all_events = ["All"] + list(streaming_data["Event"].unique())
selected_event = st.sidebar.selectbox("Event", all_events, index=0, format_func=lambda x: "Select Event" if x == "All" else x)

# Date filter
start_date = st.sidebar.date_input("Select Start Date", streaming_data["Date"].min().date())
end_date = st.sidebar.date_input("Select End Date", streaming_data["Date"].max().date())

# Convert start_date and end_date to datetime objects
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filter data
filtered_data = streaming_data.copy()
if selected_country != "All":
    filtered_data = filtered_data[filtered_data["Country"] == selected_country]
if selected_event != "All":
    filtered_data = filtered_data[filtered_data["Event"] == selected_event]

# Convert start_date and end_date to datetime objects
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filter data by date range
filtered_data = filtered_data[(filtered_data["Date"] >= start_date) & (filtered_data["Date"] <= end_date)]

# Add file uploader to the sidebar
#uploaded_file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx", "xls", "csv"])

#if uploaded_file is not None:
    # Read the uploaded Excel file
   # uploaded_data = pd.read_excel(uploaded_file)
    #st.sidebar.write("Uploaded file preview:")
    #st.sidebar.write(uploaded_data)
#else:
  #  st.sidebar.write("No file uploaded. Using default streaming data:")
   # st.sidebar.write(streaming_data)

# Create KPI cards
col1, col2, col3, col0 = st.columns(4)

# Total Visits card
with col1:
    total_visits_without_filter = len(streaming_data)
    total_visits_with_filter = len(filtered_data)
    threshold = 200
    delta_value = total_visits_with_filter - total_visits_without_filter
    arrow_symbol = "↑" if delta_value > 0 else "↓"
    arrow_color = 'red' if delta_value < threshold else 'green'
    
    st.markdown(
        f"""
        <div style="{kpi_card_style}">
            <p>Total Visits: <strong>{total_visits_with_filter}</strong></p>
            <p>Delta: <strong style="color: {arrow_color}">{delta_value} {arrow_symbol}</strong></p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Average Session Duration card
with col2:
    average_session_duration = filtered_data['Session Duration'].mean()
    reference_value = 100
    delta_value = average_session_duration - reference_value
    delta_color = 'inverse' if delta_value < 0 else 'normal'
    arrow_icon = "&#8595;" if delta_value < 0 else "&#8593;"
    
    st.markdown(
        f"""
        <div style="{kpi_card_style}">
            <p>Average Session Duration: <strong>{average_session_duration:.2f} seconds</strong></p>
            <p>Delta: <strong style="color: {'red' if delta_value < 50 else 'green'}">{delta_value:.2f} {arrow_icon}</strong></p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Event Views card
with col3:
    max_value = 1000
    num_views = filtered_data.shape[0]
    percentage = (num_views / max_value) * 100
    color = "#032545" if percentage >= 80 else "orange" if percentage >= 50 else "red"
    
    st.markdown(
        f"""
        <div style="{kpi_card_style}; background-color: {color}; color: white; text-align: center;">
            <p>Views by {selected_event} in {selected_country}</p>
            <h2>{num_views}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

with col0:
# Calculate the country with the highest number of visits
 top_country = filtered_data['Country'].value_counts().idxmax()
 num_visits_top_country = filtered_data['Country'].value_counts().max()

# Display the KPI card
 st.markdown(
    f"""
    <div style="{kpi_card_style}">
        <p>Top country: <strong>{top_country}</strong></p>
        <p>Number of Visits: <strong>{num_visits_top_country}</strong></p>
    </div>
    """,
    unsafe_allow_html=True
 )

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
if uploaded_file is not None:
    # Read uploaded file
    new_df = pd.read_csv(uploaded_file)
    # Display uploaded data
    st.write("Uploaded Data:")
    st.write(new_df)
    # Fetch data from the API
    api_data = fetch_api_data(api_url)
 
    # Check if data is fetched successfully
    if api_data:
        # Display fetched data
        st.write("Data Fetched from API:")
        st.write(pd.DataFrame(api_data))
 
# Or, you can add a separate button to trigger API data fetching:
if st.button("Fetch Data from API"):
    # Fetch data from the API
    api_data = fetch_api_data(api_url)
 
    # Check if data is fetched successfully
    if api_data:
        # Display fetched data
        st.write("Data Fetched from API:")
        st.write(pd.DataFrame(api_data))
 
# Define the rest of your Streamlit app components...


col4, col5 = st.columns(2)


#-------------------USER AGENT----------------------------------/
with col4:
# Calculate the frequency of each user agent
 user_agent_counts = filtered_data['User Agent'].value_counts()

# Define colors for the user agents
 colors = ['red', 'orange', 'green', 'blue', 'purple', 'yellow']  # Add more colors if needed

# Create pie chart for user agents
 fig_user_agents = go.Figure(go.Pie(
    labels=user_agent_counts.index,
    values=user_agent_counts.values,
    marker=dict(colors=colors[:len(user_agent_counts)]),  # Assign colors to pie slices
      ))

# Update layout to adjust the size and add title
 fig_user_agents.update_layout(
    width=500,  # Adjust width
    height=400,  # Adjust height
    title={'text': "User Agents", 'font': {'size': 16}, 'x': 0.5, 'y': 0.95, 'xanchor': 'center', 'yanchor': 'top', 'xref': 'paper'}
  )

# Display the pie chart
#st.plotly_chart(fig_user_agents)
#st.write("Page with most engagements: ", most_engaged_page)
 st.plotly_chart(fig_user_agents)

#--------------Device Usage Breakdown------------------------/
with col5:
 device_visits = filtered_data.groupby('Device')['UserID'].sum().reset_index()

# Plot the pie chart
 fig_device = px.pie(device_visits, 
                    names='Device', 
                    values='UserID', 
                    title='Device Usage Breakdown')
 # Resize the pie chart
 fig_device.update_layout(width=500, height=400)  # Adjust width and height as needed


# Display the pie chart in Streamlit
 st.plotly_chart(fig_device)

col6, col7 = st.columns(2)
 #---------------Visit details--------------------/
 # Visits Details
with col6:
 st.header("Visits Details")
 st.write(filtered_data[["IP Address", "Date", "Time", "Session Duration"]])
 # Add a button to download the information/records
 if st.button("Download"):
    # Code to download the records goes here
    # For example, you can use pandas to_csv() function to export the data to a CSV file
    csv = filtered_data.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="visits_details.csv">Download CSV File</a>'
    st.markdown(href, unsafe_allow_html=True)


#----------------Unique visitor trends over time-----------------/
with col7:
# Convert 'Time' column to datetime type
 filtered_data['Time'] = pd.to_datetime(filtered_data['Time'])

# Grouping by time intervals and counting unique IP addresses
 grouped_df = filtered_data.groupby(pd.Grouper(key='Time', freq='1H'))['IP Address'].nunique().reset_index(name='Unique_Visitors')

# Line chart
 fig = px.line(grouped_df, x='Time', y='Unique_Visitors', title='Unique Visitor Trends Over Time')
 st.plotly_chart(fig)

col8, col9 = st.columns(2)

#-----------------Top 10 COUNTRIES---------------/
with col8:
# Group data by country and calculate total visits
 country_visits = streaming_data.groupby('Country')['UserID'].sum()

# Sort countries by total visits in descending order and select top 10
 top_countries = country_visits.sort_values(ascending=False).head(10)

# Plot horizontal bar graph using Plotly Express
 fig = px.bar(top_countries, x=top_countries.values, y=top_countries.index, orientation='h',
             labels={'x':'Visits', 'y':'Country'}, title='Top 10 Countries by Visits')
 st.plotly_chart(fig)

#------------------Views by EVENTS----------------/
with col9:
# Main interest (viewed sports/events)
 st.header("Views by events")
 event_counts = filtered_data["Event"].value_counts()
 st.bar_chart(event_counts)

col10, col11 = st.columns(2)
#--------------------BUFFERING RATE OVERTIME--------------------------
with col10:
# Assuming 'Time' column is already in datetime format
 filtered_data['Time'] = pd.to_datetime(filtered_data['Time'])

# Grouping by time intervals and counting unique IP addresses
 grouped_df = filtered_data.groupby(pd.Grouper(key='Time', freq='1H'))['Buffering Rate'].mean().reset_index()

# Plot the line graph
 fig = px.line(grouped_df, x='Time', y='Buffering Rate', title='Buffering Rate Over Time')

# Customize x-axis tick labels
 fig.update_xaxes(
    tickmode='array',  # Set tick mode to array
    tickvals=grouped_df['Time'],  # Specify tick values from the grouped DataFrame
    ticktext=grouped_df['Time'].dt.strftime('%H:%M')  # Specify tick text as formatted time strings
 )

# Display the Plotly chart in Streamlit
 st.plotly_chart(fig)

#-------------------------RESOLUTION CHANGES OVERTIME----------------------------/
with col11:
   # Convert 'Time' column to datetime type
 streaming_data['Time'] = pd.to_datetime(streaming_data['Time'])

# Extract hour from 'Time' column
 streaming_data['Hour'] = streaming_data['Time'].dt.hour

# Aggregate data by hour and count occurrences of each resolution within each hour
 resolution_counts_hourly = streaming_data.groupby(['Hour', 'Resolution']).size().reset_index(name='Count')

# Create a stacked bar chart
 fig_stacked_bar_hourly = px.bar(resolution_counts_hourly, 
                                x='Hour', 
                                y='Count', 
                                color='Resolution', 
                                title='Resolution Changes Over Time (1-Hour Intervals)',
                                labels={'Hour': 'Hour of the Day', 'Count': 'Count'})

# Display the stacked bar chart in Streamlit
 st.plotly_chart(fig_stacked_bar_hourly)

#--------------------NOTIFICATION--------------------------------------/
# Notification for high buffering rate
# Define the threshold for high buffering rate (adjust as needed)
threshold = 2

# Filter data for high buffering rate
high_buffering_data = streaming_data[streaming_data['Buffering Rate'] > threshold]

if not high_buffering_data.empty:
    # Display warning message
    st.warning("High buffering rate detected in the following records:")
    
    # Display the table
    st.write(high_buffering_data[['Time', 'Buffering Rate', 'IP Address', 'Country']])

    # Download button for high buffering rate data
    csv_buffering = high_buffering_data.to_csv(index=False)
    st.download_button(label="Download High Buffering Rate Data", data=csv_buffering, file_name='high_buffering_rate_data.csv')

    

   