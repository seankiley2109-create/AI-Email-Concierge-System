import streamlit as st
from google.cloud import storage
import json
import pandas as pd
import json
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, ColumnsAutoSizeMode, JsCode

BUCKET_NAME = 'hackathon-team2-bucket'
FILE_NAME = 'all_customer_support_analysis.json'

if 'df' not in st.session_state:
    st.session_state.df = None

st.set_page_config(page_title="Ottomatic Reply", layout="wide")
st.logo("otto-group-1536.png", size="large")

st.title('Welcome to Ottomatic Reply')
st.write('''#### Here’s where great service starts.
This internal support space is designed to help our team assist customers quickly, confidently, and in true Otto style.
We keep it efficient, empathetic, and always on-brand — just like the service our customers expect.
Let’s make support smarter, together.''')

if st.button('**Download data**', type='primary'):
    client = storage.Client(project= 'ogcs-av8t-ailaboratory')
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(FILE_NAME)
   
    data = blob.download_as_text()
    parsed_data = json.loads(data)

    # Step 2: Extract the list of email records
    # emails = parsed_data.get("emails", [])

    # Step 3: Convert to DataFrame
    df = pd.DataFrame(parsed_data)
    st.session_state.df = df


import streamlit as st

# Using "with" notation
with st.sidebar:
    team_select = st.selectbox(
    "Please select the Support Team",
    ("All","Shipping and Delivery Updates", "Returns and Exchanges Management",
        "Claims and Product Defects", "Payment and Billing Support", "Product Consultation", 
        "Order Support", "Technical Assistance", "Customer Account Support", 
        "Loyalty Programs and Discounts", "Customer Feedback and Complaints")
    )

#st.logo('Otto_Group_Logo_2022.svg.png')
    # Filter anwenden


if st.session_state.df is not None:
    # Make a copy of the DataFrame to avoid modifying the original session state object directly
    df = st.session_state.df.copy()

    if team_select != "All":
        df = df[df['support_team'] == team_select]
    
    df = df.drop(columns=['sentiment_score', 'sentiment_magnitude'])

    df['draft_reply'] = 'Subject' + df['draft_reply'].str.split('Subject', n=1).str[1]

    # Define a mapping for column renaming
    column_rename_map = {
        'timestamp': 'Timestamp',
        'email_address': 'Email Address',
        'subject': 'Subject',
        'original_email_text': 'Original Email',
        'redacted_email_text': 'Redacted Email',
        'support_team': 'Support Team',
        'sentiment_category': 'Sentiment',
        'urgency': 'Urgency',
        'draft_reply': 'Draft Reply',
        'answered': 'Answered',
    }
    df = df.rename(columns=column_rename_map)

    # --- AgGrid Configuration ---

    # Define the length at which text will be truncated in the table cells
    TRUNCATE_LEN = 100 # You can adjust this value

    # JavaScript function to truncate cell values for display
    # This function runs within the browser's JavaScript environment
    js_truncate_formatter = f"""
    function(params) {{
        if (params.value && params.value.length > {TRUNCATE_LEN}) {{
            return params.value.substring(0, {TRUNCATE_LEN}) + '...';
        }} else {{
            return params.value;
        }}
    }}
    """

    js_sentiment_cell_style = JsCode("""
    function(params) {
        var sentiment = params.value; // params.value already contains the cell value
        if (sentiment === 'Very unhappy') {
            return { 'color': 'darkred', 'backgroundColor': '#FFCCCC', 'fontWeight': 'bold' };
        } else if (sentiment === 'Unhappy') {
            return { 'color': '#CC6600', 'backgroundColor': '#FFD9CC', 'fontWeight': 'bold' };
        } else if (sentiment === 'Neutral') {
            return { 'color': 'darkgoldenrod', 'backgroundColor': '#FFFFCC', 'fontWeight': 'bold' };
        } else if (sentiment === 'Happy') {
            return { 'color': 'darkgreen', 'backgroundColor': '#CCFFCC', 'fontWeight': 'bold' };
        } else if (sentiment === 'Very Happy') {
            return { 'color': 'darkblue', 'backgroundColor': '#99FF99', 'fontWeight': 'bold' };
        }
        return null; // No specific style for other values
    }
    """)

    js_urgency_cell_style = JsCode("""
    function(params) {
        var urgency = params.value; // params.value already contains the cell value
        if (urgency === 1) {
            return { 'color': 'black', 'backgroundColor': 'white', 'fontWeight': 'bold' };
        } else if (urgency === 2) {
            return { 'color': 'black', 'backgroundColor': '#E5E5E5', 'fontWeight': 'bold' };
        } else if (urgency === 3) {
            return { 'color': 'darkgoldenrod', 'backgroundColor': '#FFFFCC', 'fontWeight': 'bold' };
        } else if (urgency === 4) {
            return { 'color': '#CC6600', 'backgroundColor': '#FFD9CC', 'fontWeight': 'bold' };
        } else if (urgency === 5) {
            return { 'color': 'darkred', 'backgroundColor': '#FFCCCC', 'fontWeight': 'bold' };
        }
        return null; // No specific style for other values
    }
    """)

    # Initialize GridOptionsBuilder with your DataFrame
    gb = GridOptionsBuilder.from_dataframe(df)

    # Configure the 'Original Email' column
    gb.configure_column(
        "Original Email",
        width=200, # Fixed width for the column in pixels (increased for better viewing)
        resizable=True,
        filter=True,
        tooltipField="Original Email", 
        )
    

    # Configure the 'Redacted Email' column similarly
    gb.configure_column(
        "Redacted Email",
        width=200, # Fixed width for the column (increased for better viewing)
        tooltipField="Redacted Email", # Shows the full text on hover
        resizable=True,
        filter=True
    )

    gb.configure_column(
        "Draft Reply",
        width=200, # Fixed width for the column (increased for better viewing)
        tooltipField="Draft Reply", # Shows the full text on hover
        resizable=True,
        filter=True
    )

    # Configure other columns for better display or specific needs
    gb.configure_column("Timestamp", type=["customDateTimeFormat"], custom_format_string='yyyy-MM-dd HH:mm:ss', filter="agDateColumnFilter")
    gb.configure_column("Email Address", width=100)
    gb.configure_column("Subject")
    gb.configure_column("Support Team", filter="agMultiColumnFilter")
    gb.configure_column("Sentiment", filter=True, cellStyle=js_sentiment_cell_style)
    gb.configure_column("Urgency", cellStyle=js_urgency_cell_style)
    gb.configure_column("Answered", width=30)
    gb.configure_column("trace_id", width=250)

    # Enable single row selection in the grid
    # When a row is selected, its data will be returned in grid_response['selected_rows']
    gb.configure_selection(
        'single',           # Allows only one row to be selected at a time
        use_checkbox=False, # Does not show a checkbox column for selection
        groupSelectsChildren=True # Selects child rows if grouped
    )

    # Build the grid options object
    gridOptions = gb.build()

    gridOptions['enableCellTextSelection'] = True
    gridOptions['ensureDomOrder'] = True

    gridOptions['rowHeight'] = 20

    # Display the AgGrid component
    grid_response = AgGrid(
        df,
        gridOptions=gridOptions,
        data_return_mode='FILTERED', # Return the data as it was input (useful for selection)
        update_mode=GridUpdateMode.MODEL_CHANGED, # Update when the model changes (e.g., selection)
        fit_columns_on_grid_load=False, # Important: Set to False to respect fixed column widths
        allow_unsafe_jscode=True, # Required for the custom JavaScript valueFormatter and cellStyle
        enable_enterprise_modules=False, # Set to True if you have an AG Grid Enterprise license
        width='100%', # Make the grid span the full width of its container
        reload_data=True, # Reloads grid data if the underlying DataFrame changes
        key="email_data_grid" # Unique key for the component to prevent re-rendering issues
    )
    with st.sidebar:
        st.metric(label='Number of unanswered Tickets (Team):', value=len(df), border=True)
else:
    st.info("Please click download data to retrieve the data from Google Cloud Storage.")

