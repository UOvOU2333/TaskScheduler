import streamlit as st
import streamlit_antd_components as sac

from services import sql_services as db
from tasks.createTask import createTask
from tasks.showTasks import showAllTasks
from widgets.navbar import navbar

st.set_page_config(page_title="Task Scheduler", layout="wide")

PAGENAME = "task"

with st.sidebar:
    navbar(PAGENAME)
    st.title("任务管理")
    menu = sac.menu(
        items=[
            sac.MenuItem('创建任务', icon='upload'),
            sac.MenuItem('全部任务', icon='database'),
        ],
        open_all=True
    )

col_mainT, col_subT = st.columns([1,2])

with col_subT:
    st.title("Task Scheduler",text_alignment="right")

# ==================================
# 创建任务页面
# ==================================
if menu == "创建任务":
    with col_mainT:
        st.title("创建任务")
    createTask()

# ==================================
# 全部任务页面
# ==================================
elif menu == "全部任务":
    with col_mainT:
        st.title("全部任务")
    showAllTasks()