import streamlit as st
from services.preset_color_services import (
    get_all_preset_colors,
    add_preset_color,
    delete_preset_color
)

def preset_color_manager(return_selected: bool = False):

    col_cho, col_add = st.columns(2)
    
    colors = get_all_preset_colors()

    with col_add:
        if colors:
            st.space()
            with st.expander("已有颜色"):
                        # ================= 展示已有颜色列表 =================
                for c in colors:
                    col1, col2, col3 = st.columns([1, 2, 2])

                    with col1:
                        st.markdown(
                            f"""
                            <div style="
                                width:40px;
                                height:40px;
                                background:{c['color_value']};
                                border-radius:8px;
                                border:1px solid #ccc;
                            "></div>
                            """,
                            unsafe_allow_html=True
                        )

                    with col2:
                        st.markdown(
                            f"""
                            <div style="line-height:1.2; margin:0;">
                                <div style="font-weight:600; margin:4px;">{c['color_name']}</div>
                                <div style="font-size:12px; color:gray; margin:2px;">{c['color_value']}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    with col3:
                        if st.button("删除", key=f"del_{c['id']}"):
                            delete_preset_color(c["id"])
                            st.rerun()

        # ================= 新增颜色 =================
        with st.expander("新增颜色"):

            col1, col2 = st.columns([2,1])

            with col1:
                color_name = st.text_input("颜色名称", key="pc_name")

            with col2:
                color_value = st.color_picker("选择颜色", "#409EFF", key="pc_picker")

            if st.button("保存颜色", key="pc_save"):
                name = color_name.strip()

                if not name:
                    st.warning("请输入颜色名称")
                else:
                    # 检查是否重名（忽略大小写）
                    existing_names = [c["color_name"].lower() for c in colors]

                    if name.lower() in existing_names:
                        st.error("该名称已被占用")
                    else:
                        add_preset_color(name, color_value)
                        st.success("保存成功")
                        st.rerun()

    with col_cho:
        if not colors:
            st.info("暂无预设颜色")
            return None if return_selected else None

        # 选择功能
        color_map = {c["color_name"]: c["color_value"] for c in colors}
        selected_color_value = None

        if return_selected:
            selected_name = st.selectbox(
                "预设颜色",
                list(color_map.keys()),
                key="pc_select"
            )
            selected_color_value = color_map[selected_name]

            # 预览
            st.markdown(
                f"""
                <div style="
                    width:100%;
                    height:40px;
                    background:{selected_color_value};
                    border-radius:6px;
                    margin-bottom:10px;
                "></div>
                """,
                unsafe_allow_html=True
            )

    return selected_color_value if return_selected else None