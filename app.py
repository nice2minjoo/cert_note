import streamlit as st
import requests
import json
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta # to add days or years

token = st.secrets["token"]
databasdID = st.secrets["databaseID"]
historyID = st.secrets["historyID"]

payload = {"page_size": 1000}
headers = {
    "Authorization": token,
    "accept": "application/json",
    "Notion-Version": "2022-06-28",
    "content-type": "application/json"
}

def parseData(data):
    mod_list = []
    vend_list = []
    chip_list = []
    tech_list = []
    carrier_list = []
    version_list = []
    status_list = []
    desc_list = []
    
    for result in data['results']:
        mod_output = result['properties']['Module']['select']['name']
        vend_output = result['properties']['Vendor']['select']['name']
        chip_output = result['properties']['Chipset']['rich_text'][0]['plain_text']
        tech_output = result['properties']['Technology']['select']['name']
        carrier_output = result['properties']['Carrier']['select']['name']
        version_output = result['properties']['Version']['rich_text'][0]['plain_text']
        if not result['properties']['Status']['status']:
            status_output = ''
        else:
            status_output = result['properties']['Status']['status']['name']
        if not result['properties']['Description']['rich_text']:
            desc_output = ''
        else:
            desc_output = result['properties']['Description']['rich_text'][0]['plain_text']
        mod_list.append(mod_output)
        vend_list.append(vend_output)
        chip_list.append(chip_output)
        tech_list.append(tech_output)
        carrier_list.append(carrier_output)
        version_list.append(version_output)
        status_list.append(status_output)
        desc_list.append(desc_output)
    
    df = pd.DataFrame({
        "Module" : mod_list,
        "Vendor" : vend_list,
        "Chipset" : chip_list,
        "Technology" : tech_list,
        "Carrier" : carrier_list,
        "Version" : version_list,
        "Status" : status_list,
        "Description" : desc_list
    })
      
    str_expr = f"Module.str.contains('{search_tab1}', case=False)"
    df = df.query(str_expr)
    st.dataframe(df, use_container_width=True)
    
def parseDataex(data):
    mod_listex = []
    carrier_listex = []
    date_listex = []
    desc_listex = []
    
    for result in data['results']:
        mod_outputex = result['properties']['Module']['select']['name']
        carrier_outputex = result['properties']['Carrier']['select']['name']
        date_outputex = result['properties']['Date']['date']['start']
        if not result['properties']['Description']['rich_text']:
            desc_outputex = ''
        else:
            desc_outputex = result['properties']['Description']['rich_text'][0]['plain_text']
        mod_listex.append(mod_outputex)
        carrier_listex.append(carrier_outputex)
        date_listex.append(date_outputex)
        desc_listex.append(desc_outputex)
    
    df = pd.DataFrame({
        "Module" : mod_listex,
        "Carrier" : carrier_listex,
        "Date" : date_listex,
        "Description" : desc_listex
    })
    
    filter_container = st.container()
    
    with filter_container:
        if search_tab2 == "Module":
            search_str = st.text_input("Input (e.g, BG96, bg96, bg)")
            str_expr = f"Module.str.contains('{search_str}', case=False)"
            df = df.query(str_expr)
        
        elif search_tab2 == "Date":
            min_date = dt.date(year=2010,month=1,day=1)
            max_date = dt.datetime.now().date()
            
            slider = st.slider('Date', min_value=min_date, max_value=max_date, value=(min_date, max_date))
            # st.write(f'{slider[0]} - {slider[1]}')
            # st.write(slider)
            # st.write(pd.to_datetime(df["Date"]))
            
            
    st.dataframe(df, use_container_width=True)

def readDatabase(url, tab):
    response = requests.post(url, json=payload, headers=headers)
    data_bytes = response.content
    data_str = data_bytes.decode('utf-8')
    data = json.loads(data_str)
    # st.write(data)
    
    if response :
    # if '\"status\":200' in response.text:
        if tab == 0:
            parseData(data)
        elif tab == 1:
            parseDataex(data)

    elif '\"status\":400' in response.text:
        err = f'[readDatabase] {response}'
        st.write(err)
        
    elif '\"status\":401' in response.text:
        err = f'[readDatabase] {response}'
        st.write(err)
        
    elif '\"status\":404' in response.text:
        err = f'[readDatabase] {response}'
        st.write(err)
    
# start from here
st.set_page_config(page_title = "Quectel Certification Status")
st.title("Quectel Certification Status")
st.write("This is a certification status of Quectel Korea for domestic carriers.")

tab1, tab2 = st.tabs(["Status","History"])
with tab1:
    with st.spinner("Waiting for loading data..."):
        tab = 0
        search_tab1 = st.text_input("Input module name (e.g, EC25-E, ec25, ec)")
        notion_api_link = f"https://api.notion.com/v1/databases/{databasdID}/query"
        readDatabase(notion_api_link, tab)

with tab2:
    with st.spinner("Waiting for loading data..."):
        tab = 1
        search_tab2 = st.selectbox("Search with", ("Module","Date"))
        # search_tab2 = st.text_input("Input module name (e.g, BG96, bg96, bg)")
        notion_api_link = f"https://api.notion.com/v1/databases/{historyID}/query"
        readDatabase(notion_api_link, tab)
