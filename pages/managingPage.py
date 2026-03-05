import streamlit as st
import streamlit_antd_components as sac

from tasks.createTask import createTask
from tasks.updateTask import updateTask
from tasks.showTasks import showAllTasks
from widgets.navbar import navbar
from managing.statesManage import stateManage
from managing.typesManage import typeManage

st.set_page_config(page_title="Task Scheduler", layout="wide")

PAGENAME = "task"

with st.sidebar:
    navbar(PAGENAME)
    st.title("任务管理")
    menu = sac.menu(
        items=[
            sac.MenuItem('创建任务', icon='plus-circle'),
            sac.MenuItem('修改任务', icon='recycle'),
            sac.MenuItem('全部任务', icon='database'),
            sac.MenuItem('类型管理', icon='tag'),
            sac.MenuItem('状态管理', icon='toggle-on'),
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

elif menu == "修改任务":
    with col_mainT:
        st.title("修改任务")
    updateTask()

# ==================================
# 全部任务页面
# ==================================
elif menu == "全部任务":
    with col_mainT:
        st.title("全部任务")
    showAllTasks()

elif menu == "类型管理":
    with col_mainT:
        st.title("任务类型管理")
    typeManage()

elif menu == "状态管理":
    with col_mainT:
        st.title("任务状态管理")
    stateManage()