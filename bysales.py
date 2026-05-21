import streamlit as st
import gspread
import pandas as pd

from google.oauth2 import service_account
from st_aggrid import AgGrid, GridOptionsBuilder
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_data
def get_data_from_google():

    with st.spinner("Getting data from Google Sheets..."):

        google_creds = dict(st.secrets["google"])

        credentials = service_account.Credentials.from_service_account_info(
            google_creds,
            scopes=SCOPES
        )

        client = gspread.authorize(credentials)

        sheet = client.open_by_key(
            "1iK7Rv8lY5vbcy9ODj12-MbAvdqC7lwfH0UawHNPpVjs"
        )

        worksheet = sheet.worksheet("BySales")
        bysales = pd.DataFrame(worksheet.get_all_records())

        worksheet = sheet.worksheet("RekapSales")
        rekapsales = pd.DataFrame(worksheet.get_all_records())

        return bysales, rekapsales

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