import streamlit as st
from services.state_services import *
from widgets.presetColor import preset_color_manager


def stateManage():

    states = get_all_states()

    col1, col2 = st.columns([1, 1])

    # =============================
    # 左侧：列表
    # =============================
    with col1:
        st.subheader("已有状态")

        for s in states:
            c1, c2, c3 = st.columns([4, 1, 1])
            with c1:
                st.markdown(
                    f"<span style='color:{s['state_color']};font-weight:bold'>{s['state_name']}</span>",
                    unsafe_allow_html=True
                )
            with c2:
                if st.button("编辑", key=f"edit_state_{s['id']}"):
                    st.session_state["editing_state"] = dict(s)
            with c3:
                if st.button("删除", key=f"del_state_{s['id']}"):
                    if state_used(s["id"]):
                        st.error("该状态已被任务使用，无法删除")
                    else:
                        delete_state(s["id"])
                        st.rerun()

    # =============================
    # 右侧：新增 / 编辑
    # =============================
    with col2:
        if "editing_state" in st.session_state:
            data = st.session_state["editing_state"]
            st.subheader("编辑状态")

            name = st.text_input("状态名称", value=data["state_name"], key="edit_state_name")

            st.markdown("选择颜色")
            selected_color = preset_color_manager(return_selected=True)

            # 如果未选择则保持原颜色
            color = selected_color if selected_color else data["state_color"]

            if st.button("保存修改", key="save_state_edit"):
                update_state(data["id"], name, color)
                del st.session_state["editing_state"]
                st.rerun()

            if st.button("取消", key="cancel_state_edit"):
                del st.session_state["editing_state"]
                st.rerun()

        else:
            st.subheader("新增状态")

            name = st.text_input("状态名称", key="new_state_name")

            st.markdown("选择颜色")
            color = preset_color_manager(return_selected=True)

            if st.button("新增", key="add_state_btn"):
                if name.strip() and color:
                    add_state(name, color)
                    st.rerun()
                else:
                    st.warning("请输入名称并选择颜色")