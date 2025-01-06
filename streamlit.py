import streamlit as st
import pandas as pd

report = st.Page(
    page="Report.py",
    title="Sales Performance",
    icon="📊",
    default=True
)

bysales = st.Page(
    page="bysales.py",
    title="by Location",
    icon="📊",
)

pg = st.navigation({
    "Report": [report, bysales]
})



pg.run()