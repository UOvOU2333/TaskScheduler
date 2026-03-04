import streamlit as st
import streamlit_antd_components as sac

from tasks.showTasks import todayTasks
from widgets.navbar import navbar

st.set_page_config(page_title="Task Scheduler", layout="wide")

PAGENAME = "main"

with st.sidebar:
    navbar(PAGENAME)
    st.title("首页")
    menu = sac.menu(
        items=[
            sac.MenuItem('总览看板', icon='calendar'),
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
    st.header("今日任务")
    todayTasks()





