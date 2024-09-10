import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from st_aggrid import AgGrid, GridOptionsBuilder

# Function to load data from Google Sheets
@st.cache_data
def load_data(sheet_url):
    # Convert Google Sheets link to CSV format
    csv_url = sheet_url.replace('/edit?usp=sharing&ouid=111152179320358185815&rtpof=true&sd=true', '/export?format=csv')
    data = pd.read_csv(csv_url)
    return data

# Load the data
sheet_url = "https://docs.google.com/spreadsheets/d/1c7_Cb3u34t_pwKyQ0RWHtCfso4ELJpFV/edit?usp=sharing&ouid=111152179320358185815&rtpof=true&sd=true"
df = load_data(sheet_url)

# Ensure all data in the 'Department' and 'Publisher' columns are strings
df['Department'] = df['Department'].astype(str)
df['Publisher'] = df['Publisher'].astype(str)

# Initialize session state variables only if they do not exist
if 'title_search' not in st.session_state:
    st.session_state.title_search = ""
if 'author_search' not in st.session_state:
    st.session_state.author_search = ""
if 'department_search' not in st.session_state:
    st.session_state.department_search = ""
if 'publisher_search' not in st.session_state:
    st.session_state.publisher_search = ""

# Calculate Total Title Collection and Total Books Collection
total_titles = len(df)
total_books = df['Available Nos'].sum()

# Title of the Streamlit app
st.title("Library Book Search App for DSAC")
st.subheader("version 1.0")

# Display total collections information
st.markdown(f"**Total Title Collection:** {total_titles}")
st.markdown(f"**Total Books Collection:** {total_books}")

# Search inputs in the main panel
st.header("Search Filters")

# Check if the "Clear Filters" button was pressed
if st.button("Clear Filters"):
    st.session_state.title_search = ""
    st.session_state.author_search = ""
    st.session_state.department_search = ""
    st.session_state.publisher_search = ""

# Function to get unique values for suggestions
def get_unique_suggestions(column, search_term):
    suggestions = df[column].dropna().unique().tolist()
    if search_term:
        suggestions = [item for item in suggestions if search_term.lower() in item.lower()]
    return suggestions

# Dynamic search inputs with auto-suggestions and bold titles
title_search = st.selectbox("**Search by Title**", options=[""] + get_unique_suggestions("TITLE", st.session_state.title_search), key="title_search")
author_search = st.selectbox("**Search by Author**", options=[""] + get_unique_suggestions("Authors", st.session_state.author_search), key="author_search")
department_search = st.selectbox("**Search by Department**", options=[""] + get_unique_suggestions("Department", st.session_state.department_search), key="department_search")
publisher_search = st.selectbox("**Search by Publisher**", options=[""] + get_unique_suggestions("Publisher", st.session_state.publisher_search), key="publisher_search")

# Function to filter data based on user input
def filter_data(df, title, author, department, publisher):
    if title:
        df = df[df['TITLE'].str.contains(title, case=False, na=False)]
    if author:
        df = df[df['Authors'].str.contains(author, case=False, na=False)]
    if department:
        df = df[df['Department'].str.contains(department, case=False, na=False)]
    if publisher:
        df = df[df['Publisher'].str.contains(publisher, case=False, na=False)]
    return df

# Filter the data based on user input
filtered_df = filter_data(df, st.session_state.title_search, st.session_state.author_search, st.session_state.department_search, st.session_state.publisher_search)

# Place "Clear Filters" button below the search boxes
st.write("")
st.write("")
if st.button("Clear Filters", key="clear_filters_bottom"):
    st.session_state.title_search = ""
    st.session_state.author_search = ""
    st.session_state.department_search = ""
    st.session_state.publisher_search = ""

# Plot the bar graph for the "Department" column
st.header("Books Available by Department")

# Group the data by 'Department' and sum the 'Available Nos'
dept_counts = df.groupby('Department')['Available Nos'].sum().sort_values()

# Plotting the bar chart with increased size
fig, ax = plt.subplots(figsize=(10, 15))  # Adjust the figure size for better clarity
bars = ax.barh(dept_counts.index, dept_counts.values, color=plt.cm.Paired(range(len(dept_counts))), height=0.5) # 5mm is approximately 0.5 when scaled

# Set the labels and title to bold
ax.set_xlabel('Number of Books', fontsize=12, fontweight='bold')
ax.set_ylabel('Department', fontsize=12, fontweight='bold')
ax.set_title('Number of Books Available by Department', fontsize=14, fontweight='bold')

# Adding value labels on each bar
for bar in bars:
    ax.text(bar.get_width(), bar.get_y() + bar.get_height()/2, f'{int(bar.get_width())}', va='center', fontsize=10, fontweight='bold')

# Show the plot in Streamlit
st.pyplot(fig)

# Display the number of search results below the plot
st.write(f"**Total books found:** {len(filtered_df)}")

# Display the filtered data using AgGrid for better interaction
gb = GridOptionsBuilder.from_dataframe(filtered_df)
gb.configure_pagination(paginationAutoPageSize=True) # Add pagination
gb.configure_side_bar() # Add a sidebar
gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children")
gridOptions = gb.build()

AgGrid(filtered_df, gridOptions=gridOptions)
