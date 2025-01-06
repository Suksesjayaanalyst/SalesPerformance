import pandas as pd
import requests

import io
import streamlit as st
import plotly.express as px
from oauth2client.service_account import ServiceAccountCredentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
from google.oauth2 import service_account
import time
from st_aggrid import AgGrid, GridOptionsBuilder
import gspread




st.set_page_config("Sales Performance")

@st.cache_data
def get_data_from_google():
    with st.spinner("Getting data from Google Sheets..."):
        # Mengambil kredensial dari st.secrets
        google_creds = st.secrets["google"]

        # Scopes yang diperlukan untuk Google Drive API
        SCOPES = ['https://www.googleapis.com/auth/drive']

        # Autentikasi menggunakan service account dari st.secrets
        credentials = service_account.Credentials.from_service_account_info(
            {
                "type": google_creds["type"],
                "project_id": google_creds["project_id"],
                "private_key_id": google_creds["private_key_id"],
                "private_key": google_creds["private_key"],
                "client_email": google_creds["client_email"],
                "client_id": google_creds["client_id"],
                "auth_uri": google_creds["auth_uri"],
                "token_uri": google_creds["token_uri"],
                "auth_provider_x509_cert_url": google_creds["auth_provider_x509_cert_url"],
                "client_x509_cert_url": google_creds["client_x509_cert_url"]
            }, scopes=SCOPES)

        # Membangun layanan Google Drive API
        service = build('drive', 'v3', credentials=credentials)
        client = gspread.authorize(credentials)
        
        # Mengakses worksheet dan mengubah menjadi DataFrame
        sheet = client.open_by_key("1iK7Rv8lY5vbcy9ODj12-MbAvdqC7lwfH0UawHNPpVjs")
        worksheet = sheet.worksheet('BySales')
        BySales = worksheet.get_all_records()
        BySales = pd.DataFrame(BySales)

        worksheet = sheet.worksheet('RekapSales')
        RekapSales = worksheet.get_all_records()
        RekapSales = pd.DataFrame(RekapSales)
        
        # Mengembalikan data
        return BySales, RekapSales
    
if 'bysales' not in st.session_state:
    st.session_state.bysales = get_data_from_google()[0]
    st.session_state.rekapsales = get_data_from_google()[1]

BySales = st.session_state.bysales
RekapSales = st.session_state.rekapsales


st.title("Sales Performance")



selectedsales = st.selectbox("Sales", options=sorted(RekapSales['GroupSlp'].unique()), index=sorted(RekapSales['GroupSlp'].unique()).index("C1"))
name = RekapSales[RekapSales['GroupSlp'] == selectedsales]['slpname'].values[0]
st.markdown(
    f"""
    <div style="border: 2px solid #262730; padding: 10px; display: inline-block; border-radius: 10px ; margin: 0 0 10px 0">
        <b>Nama</b>: {name}
    </div>
    """, unsafe_allow_html=True
)


table1 = RekapSales.copy()
table1 = table1[table1['GroupSlp'] == selectedsales].reset_index(drop=True)

columns_except_groupslp = [col for col in table1.columns if col not in [
    "GroupSlp", "targetslp", "slpname", "TotalRevenue", "Total_Selisih", 
    "TotalBPAktifAll", "BPAktifSesuai", "BPAktifTidakSesuai", 
    "TotalBPMaster", "Selisih BP", "Reason"
]]

selectedcolumns = st.multiselect("Columns", options=columns_except_groupslp, default=columns_except_groupslp)   

# Menggabungkan kolom tetap dengan kolom yang dipilih
final_columns = ['slpname', 'GroupSlp', 'targetslp'] + selectedcolumns + ['TotalRevenue','Total_Selisih','TotalBPAktifAll','BPAktifSesuai','BPAktifTidakSesuai','TotalBPMaster','Selisih BP','Reason']

table1_final = table1[final_columns]

bulansaatini = table1_final['targetslp'][0] + table1_final['Total_Selisih'][0]

st.markdown(
    f"""
    <div style="display: flex; align-items: center; margin: 0 0 10px 0">
        <div style="border: 2px solid #262730; padding: 10px; display: inline-block; border-radius: 10px; margin-right: 20px;">
            <b>Target</b>: Rp {table1_final["targetslp"][0]:,.0f}
        </div>
        <div style="border: 2px solid #262730; padding: 10px; display: inline-block; border-radius: 10px; margin-right: 20px;"><b>Bulan Saat ini: Rp {bulansaatini:,.0f}</b></div>
    </div>
    """, unsafe_allow_html=True
)


st.dataframe(table1_final)


copytable = table1_final.copy()

table1_final.drop(columns=['GroupSlp', 'targetslp', 'TotalBPAktifAll', 'slpname'], inplace=True)

month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

selected_months = [month for month in month_order if month in table1_final.columns]

table1_final = table1_final[selected_months]



table1_final = table1_final.transpose()
# Plotting dengan Plotly
def format_currency(val):
    return f'Rp {val:,.0f}'  # Format sebagai Rp dengan pemisah ribuan

# Plotting dengan Plotly
fig = px.line(table1_final, 
              x=table1_final.index, 
              y=table1_final.columns, 
              labels={'x': 'Month', 'y': 'Values'},
              title='Sales Performance by Month', 
              markers=True)  # Menambahkan titik (dot) pada chart

# Menambahkan nilai pada titik dan mengubah format menjadi mata uang
fig.update_traces(mode='lines+markers+text', 
                  text=table1_final.values.flatten(),  # Nilai yang akan ditampilkan
                  texttemplate=[f'Rp {val:,.0f}' for val in table1_final.values.flatten()],  # Format Rp
                  textposition='top center',  # Posisi nilai di atas titik
                  showlegend=False)  # Menyembunyikan legenda (opsional)

# Menampilkan plot
st.plotly_chart(fig)


st.title("By Sales")


table2 = BySales[BySales['Sales_Employee_Name'].isin(copytable['slpname'])]

gb = GridOptionsBuilder.from_dataframe(table2)
gb.configure_columns(['Sales_Employee_Name', 'B'], pinned='left')  # Membekukan kolom A dan B
grid_options = gb.build()

AgGrid(table2, gridOptions=grid_options)