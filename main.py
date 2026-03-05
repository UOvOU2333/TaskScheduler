import streamlit as st
import streamlit_antd_components as sac

from tasks.showTasks import todayTasks, overview
from widgets.navbar import navbar
from services.snapshots_services import ensure_all_snapshots

ensure_all_snapshots()

st.set_page_config(page_title="Task Scheduler", layout="wide")

PAGENAME = "main"

with st.sidebar:
    navbar(PAGENAME)
    st.title("首页")
    menu = sac.menu(
        items=[
            sac.MenuItem('总览看板', icon='house-door'),
        ],
        open_all=True
    )

# ==================================
# 页面内容区
# ==================================

col_mainT, col_subT = st.columns([1,2])

with col_subT:
    st.title("Task Scheduler",text_alignment="right")

if menu == "总览看板":
    with col_mainT:
        st.title("总览看板")
    col_today, col_blank, col_overview = st.columns([10,1,20])
    with col_today:
        todayTasks()
    with col_overview:
        overview()





