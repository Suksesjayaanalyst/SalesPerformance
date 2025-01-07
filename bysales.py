import streamlit as st
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
import pandas as pd




st.set_page_config("Sales Performance || SPV")

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
st.write("by Location")

location = st.selectbox("Choose:", options=["TENGSEK", "PIK"])

pik = ["Abdul Wahid", "Ahmad Rizal", "Dina", "Femi Permatasari", "Indah Mellani", "Ine", "Junia Rachma", "Leppi Dianti", "Rachel Valencia", "Rizki", "Rosida Juniaz Santi", "Sadarmawati", "Saepudin", "Shifa Anggraeni"
]

tengsek = ["Ariyani Febiyanti", "Bella Ariesta", "Dinda Audia Fajri", "Dita Putri Endah", "Fera Ramadhani", "Fitria Ningsih", "Hestuti", "Ika Oktaviani", "Maharani Permatasari", "Mahdiyah", "Maimanah", "Muslihah", "Nadia Syahdania", "Putri Khaeru Shifa", "Siti Aisyah", "Siti Nur Afifah", "Tika Juliasih", "Wulandari", "Yani", "Zalsabila Dwi Qirunnisa"
]

if location == "PIK":
    RekapSales = RekapSales[RekapSales['slpname'].isin(pik)]
    BySales = BySales[BySales['Sales_Employee_Name'].isin(pik)]

if location == "TENGSEK":
    RekapSales = RekapSales[RekapSales['slpname'].isin(tengsek)]
    BySales = BySales[BySales['Sales_Employee_Name'].isin(tengsek)]


# st.dataframe(BySales)

excluded_columns = [
    "TotalBPAktifAll","Selisih BP","TotalBPMaster", "BPAktifSesuai", "BPAktifTidakSesuai", "TotalBPMasterSelisih"
]

# Mengubah semua kolom numeric kecuali kolom yang dikecualikan menjadi format Rupiah
forTable = RekapSales.apply(
    lambda col: col.apply(
        lambda x: f"Rp {x:,.0f}".replace(",", ".") if isinstance(x, (int, float)) and col.name not in excluded_columns else x
    )
)

# Membuat GridOptionsBuilder
gb = GridOptionsBuilder.from_dataframe(forTable)

# Membekukan kolom slpname dan targetslp di sebelah kiri
gb.configure_columns(['slpname', 'targetslp'], pinned='left')

# Membangun opsi grid
grid_options = gb.build()

# Menampilkan DataFrame di AgGrid
AgGrid(forTable, gridOptions=grid_options)


if location == "PIK":
    st.header("SPV")
    selectspv = st.selectbox("Choose:", options=["Linda", "Ari", "Regen"])
    if selectspv == "Linda":
        spvsales = ["Ahmad Rizal", "Rizki", "Rachel Valencia", "Rosida Juniaz Santi"]
    elif selectspv == "Ari":
        spvsales = ["Ine", "Sadarmawati", "Femi Permatasari", "Leppi Dianti"]
    elif selectspv == "Regen":
        spvsales = ["Dina", "Shifa Anggraeni", "Abdul Wahid", "Indah Mellani"]

    sales = st.multiselect("Choose:", options=pik, default=spvsales)
    spvlinda = forTable[forTable['slpname'].isin(sales) ]
    gb = GridOptionsBuilder.from_dataframe(spvlinda)
    gb.configure_columns(['slpname', 'targetslp'], pinned='left')
    grid_options = gb.build()
    AgGrid(spvlinda, gridOptions=grid_options, height=175)