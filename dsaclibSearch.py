import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Function to load data from Google Sheets
@st.cache_data
def load_data(sheet_url):
    csv_url = sheet_url.replace('/edit?usp=sharing&ouid=111152179320358185815&rtpof=true&sd=true', '/export?format=csv')
    data = pd.read_csv(csv_url)
    return data

# Load the data
sheet_url = "https://docs.google.com/spreadsheets/d/1c7_Cb3u34t_pwKyQ0RWHtCfso4ELJpFV/edit?usp=sharing&ouid=111152179320358185815&rtpof=true&sd=true"
df = load_data(sheet_url)

# Ensure all data in the 'Department' and 'Publisher' columns are strings
df['Department'] = df['Department'].astype(str)
df['Publisher'] = df['Publisher'].astype(str)

# Calculate totals
total_titles = len(df['TITLE'].unique())
total_books = df['Available Nos'].sum()
avg_books_per_title = round(total_books / total_titles, 2)

# Initialize session state variables
if "reset_filters" not in st.session_state:
    st.session_state.reset_filters = False
if "title_input" not in st.session_state:
    st.session_state.title_input = ""
if "title_select" not in st.session_state:
    st.session_state.title_select = ""
if "author_input" not in st.session_state:
    st.session_state.author_input = ""
if "author_select" not in st.session_state:
    st.session_state.author_select = ""
if "department_input" not in st.session_state:
    st.session_state.department_input = ""
if "department_select" not in st.session_state:
    st.session_state.department_select = ""
if "publisher_input" not in st.session_state:
    st.session_state.publisher_input = ""
if "publisher_select" not in st.session_state:
    st.session_state.publisher_select = ""

# Function to get dynamic suggestions
def get_dynamic_suggestions(column, user_input):
    """Return dynamic suggestions for a given column based on user input."""
    if not user_input:
        return []  # No suggestions when input is empty
    suggestions = df[column].dropna().unique().tolist()
    filtered_suggestions = [item for item in suggestions if user_input.lower() in item.lower()]
    return filtered_suggestions[:10]  # Limit to top 10 suggestions

# Title and Summary
st.title("DSAC Library Book Search App")
st.markdown(
    f"""
    **Total Titles**: {total_titles}  
    **Total Books**: {total_books}  
    **Average Books per Title**: {avg_books_per_title}  
    """
)

# Filters Section
st.header("Search Filters")

# Title Search
title_input = st.text_input(
    "Search by Title",
    value=st.session_state.title_input,
    placeholder="Type to search titles...",
    key="title_input"
)
title_suggestions = get_dynamic_suggestions("TITLE", title_input)
title_select = st.selectbox(
    "Suggestions for Title", 
    options=[""] + title_suggestions if title_suggestions else [""],
    key="title_select"
)

# Author Search
author_input = st.text_input(
    "Search by Author",
    value=st.session_state.author_input,
    placeholder="Type to search authors...",
    key="author_input"
)
author_suggestions = get_dynamic_suggestions("Authors", author_input)
author_select = st.selectbox(
    "Suggestions for Author", 
    options=[""] + author_suggestions if author_suggestions else [""],
    key="author_select"
)

# Department Search
department_input = st.text_input(
    "Search by Department",
    value=st.session_state.department_input,
    placeholder="Type to search departments...",
    key="department_input"
)
department_suggestions = get_dynamic_suggestions("Department", department_input)
department_select = st.selectbox(
    "Suggestions for Department", 
    options=[""] + department_suggestions if department_suggestions else [""],
    key="department_select"
)

# Publisher Search
publisher_input = st.text_input(
    "Search by Publisher",
    value=st.session_state.publisher_input,
    placeholder="Type to search publishers...",
    key="publisher_input"
)
publisher_suggestions = get_dynamic_suggestions("Publisher", publisher_input)
publisher_select = st.selectbox(
    "Suggestions for Publisher", 
    options=[""] + publisher_suggestions if publisher_suggestions else [""],
    key="publisher_select"
)

# Clear Filters Button
if st.button("Clear Filters"):
    st.session_state.title_input = ""
    st.session_state.title_select = ""
    st.session_state.author_input = ""
    st.session_state.author_select = ""
    st.session_state.department_input = ""
    st.session_state.department_select = ""
    st.session_state.publisher_input = ""
    st.session_state.publisher_select = ""

# Function to filter data based on user input and suggestion dropdown
def filter_data(df, title_input, title_select, author_input, author_select, department_input, department_select, publisher_input, publisher_select):
    if title_select:
        df = df[df['TITLE'].str.contains(title_select, case=False, na=False)]
    elif title_input:
        df = df[df['TITLE'].str.contains(title_input, case=False, na=False)]
    
    if author_select:
        df = df[df['Authors'].str.contains(author_select, case=False, na=False)]
    elif author_input:
        df = df[df['Authors'].str.contains(author_input, case=False, na=False)]
    
    if department_select:
        df = df[df['Department'].str.contains(department_select, case=False, na=False)]
    elif department_input:
        df = df[df['Department'].str.contains(department_input, case=False, na=False)]
    
    if publisher_select:
        df = df[df['Publisher'].str.contains(publisher_select, case=False, na=False)]
    elif publisher_input:
        df = df[df['Publisher'].str.contains(publisher_input, case=False, na=False)]
    
    return df

# Filter the data based on inputs and suggestions
filtered_df = filter_data(
    df,
    st.session_state.title_input,
    st.session_state.title_select,
    st.session_state.author_input,
    st.session_state.author_select,
    st.session_state.department_input,
    st.session_state.department_select,
    st.session_state.publisher_input,
    st.session_state.publisher_select,
)

# Display filtered results count
st.markdown(f"**Total books found:** {len(filtered_df)}")

# Interactive Pie Chart for Book Distribution
st.header("Books Distribution by Department")
dept_counts = df.groupby('Department')['Available Nos'].sum().sort_values()
pie_chart = px.pie(
    dept_counts.reset_index(),
    names='Department',
    values='Available Nos',
    title='Book Distribution by Department',
    hole=0.3,
    color_discrete_sequence=px.colors.sequential.RdBu
)
st.plotly_chart(pie_chart, use_container_width=True)

# Word Cloud for Departments
st.header("Popular Departments")
wordcloud = WordCloud(width=800, height=400).generate(" ".join(df['Department']))
fig, ax = plt.subplots()
ax.imshow(wordcloud, interpolation='bilinear')
ax.axis('off')
st.pyplot(fig)

# Display filtered data using AgGrid
st.header("Search Results")
gb = GridOptionsBuilder.from_dataframe(filtered_df)
gb.configure_pagination(paginationAutoPageSize=True)  # Add pagination
gb.configure_side_bar()  # Add a sidebar
gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children")
gridOptions = gb.build()

AgGrid(filtered_df, gridOptions=gridOptions)

# Add a download button for filtered data
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Filtered Data as CSV",
    data=csv,
    file_name='filtered_books.csv',
    mime='text/csv',
)
