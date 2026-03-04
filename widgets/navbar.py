import streamlit as st

# ==============================
# 页面间跳转（顶端导航栏）
# ==============================

def navbar(pageName):

    # 初始化状态
    if "show_navbar" not in st.session_state:
        st.session_state["show_navbar"] = False

    if st.button("导航栏", use_container_width=True, type="primary"):
        st.session_state["show_navbar"] = not st.session_state["show_navbar"]
                

    if st.session_state["show_navbar"]:
        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            if st.button("首页", key=f"btn_home_{pageName}", use_container_width=True):
                st.switch_page("main.py")
        with col_nav2:
            if st.button("任务管理", key=f"btn_task_{pageName}", use_container_width=True):
                st.switch_page("pages/taskManage.py")
