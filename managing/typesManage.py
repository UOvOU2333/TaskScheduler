import streamlit as st
from services.type_services import *
from widgets.presetColor import preset_color_manager

def typeManage():
    types = get_all_types()

    col1, col2 = st.columns([1, 1])

    # =============================
    # 左侧：列表
    # =============================
    with col1:
        st.subheader("已有类型")

        for t in types:
            c1, c2, c3 = st.columns([4, 1, 1])
            with c1:
                st.markdown(
                    f"<span style='color:{t['type_color']};font-weight:bold'>{t['type_name']}</span>",
                    unsafe_allow_html=True
                )
            with c2:
                if st.button("编辑", key=f"edit_type_{t['id']}"):
                    st.session_state["editing_type"] = dict(t)
            with c3:
                if st.button("删除", key=f"del_type_{t['id']}"):
                    if type_used(t["id"]):
                        st.error("该类型已被任务使用，无法删除")
                    else:
                        delete_type(t["id"])
                        st.rerun()

    # =============================
    # 右侧：新增 / 编辑
    # =============================
    with col2:
        if "editing_type" in st.session_state:
            data = st.session_state["editing_type"]
            st.subheader("编辑类型")

            name = st.text_input("类型名称", value=data["type_name"])
            st.markdown("选择颜色")
            selected_color = preset_color_manager(return_selected=True)

            # 如果未选择则保持原颜色
            color = selected_color if selected_color else data["state_color"]

            if st.button("保存修改"):
                update_type(data["id"], name, color)
                del st.session_state["editing_type"]
                st.rerun()

            if st.button("取消"):
                del st.session_state["editing_type"]
                st.rerun()

        else:
            st.subheader("新增类型")

            name = st.text_input("类型名称", key="new_state_name")

            st.markdown("选择颜色")
            color = preset_color_manager(return_selected=True)

            if st.button("新增", key="add_state_btn"):
                if name.strip():
                    add_type(name, color)
                    st.rerun()
                else:
                    st.warning("请输入名称并选择颜色")