import streamlit as st
import datetime

from services import task_services as taskDB
from widgets.capsule import render_capsule

def showAllTasks():

    st.divider()

    tasks = taskDB.get_all_tasks()

    # 按优先级排序（假设priority数值越小优先级越高，如相反可改为 reverse=True）
    tasks = sorted(tasks, key=lambda x: x["priority"])

    if not tasks:
        st.info("暂无任务")
        return

    for t in tasks:
        rate = taskDB.get_task_completion_rate(t["id"])

        type_color = t["type_color"] if "type_color" in t.keys() and t["type_color"] else "#999999"
        state_color = t["state_color"] if "state_color" in t.keys() and t["state_color"] else "#999999"

        col1, col2, col3, col_blank, col4 = st.columns([3, 2, 2, 1, 1])

        with col1:
            st.markdown(f"""
            <div style="font-size:18px;font-weight:600;margin-bottom:6px;">
                {t["task_name"]}
            </div>
            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                {render_capsule(t["type_name"], type_color)}{render_capsule(t["state_name"], state_color)}
            """, unsafe_allow_html=True)

        with col2:
            st.write(f"频率: {t['frequency']}")
            st.write(f"优先级: {t['priority']}")

        with col3:
            st.progress(min(max(rate, 0.0), 1.0))
            st.caption(f"完成率: {round(rate * 100, 2)}%")

        with col4:
            if st.button("修改", key=f"edit_{t['id']}", use_container_width=True):
                st.session_state["edit_task_id"] = t["id"]
                st.session_state["nav"] = "任务修改"
                st.rerun()

        with st.expander("查看详情", expanded=False):
            st.markdown(f"""
            **任务ID**: {t['id']}  
            **优先级**: {t['priority']}  
            **开始时间**: {t['scheduled_start']}  
            **结束时间**: {t['scheduled_end'] if t['scheduled_end'] else '无'}  
            **总次数**: {t['total_amount']}  
            **周掩码**: {t['week_mask']}  
            **创建时间**: {t['created_at']}  
            """)

        st.divider()

def todayTasks():

    st.divider()

    tasks = taskDB.get_day_tasks()

    if not tasks:
        st.info("今天没有任务 🎉")
        return

    for t in tasks:

        type_color = t["type_color"] if "type_color" in t.keys() and t["type_color"] else "#999999"
        state_color = t["state_color"] if "state_color" in t.keys() and t["state_color"] else "#999999"

        col1, col2 = st.columns([2, 1])

        # ===== 左侧：卡片标题 + 胶囊 =====
        with col1:
            st.markdown(f"""
            <div style="font-size:30px;font-weight:600;margin-bottom:6px;">
                {t['task_name']}
            </div>
            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                {render_capsule(t['type_name'], type_color)}{render_capsule(t['state_name'], state_color)}
            """, unsafe_allow_html=True)

        # ===== 中间：完成状态 =====
        with col2:
            status_label = "已完成" if t['finished_amount'] else "未完成"
            status_color = "#4CAF50" if t['finished_amount'] else "#F44336"

            st.markdown(render_capsule(status_label, status_color), unsafe_allow_html=True)

            if t["finished_amount"] == 0:
                if st.button("完成", key=f"finish_{t['task_id']}", use_container_width=True):
                    taskDB.finish_today_task(t["task_id"])
                    st.rerun()
            else:
                if st.button("撤销", key=f"undo_{t['task_id']}", use_container_width=True):
                    taskDB.undo_today_task(t["task_id"])
                    st.rerun()

        st.divider()

def overview():
    today = datetime.date.today()

    # 获取昨天、今天和未来3天
    days = [today - datetime.timedelta(days=1) + datetime.timedelta(days=i) for i in range(5)]

    def is_light_color(hex_color):
        # Remove '#' if present
        hex_color = hex_color.lstrip('#')
        # Convert to RGB integer tuple
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        # Calculate luminance
        luminance = (0.299 * r + 0.587 * g + 0.114 * b)
        return luminance > 186  # Threshold for light/dark

    # 显示5天（昨天、今天、未来3天）
    cols = st.columns(5)
    for i in range(5):
        day = days[i]
        with cols[i]:
            st.markdown(f"### {day.strftime('%m-%d %a')}")
            day_tasks = taskDB.get_day_tasks(day)

            if not day_tasks:
                st.write("无任务")
            else:
                for t in day_tasks:
                    type_color = t["type_color"] if "type_color" in t.keys() and t["type_color"] else "#999999"

                    # Determine text color based on type_color for contrast
                    text_color = "#000000" if is_light_color(type_color) else "#FFFFFF"

                    # Compose the two narrow vertical bars and task name HTML
                    bars_html = f'''
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <div style="width: 8px; height: 20px; background-color: {type_color}; border-radius: 4px;"></div>
                        <div style="color: {text_color}; font-weight: 100; white-space: nowrap;">{t['task_name']}</div>
                    </div>
                    '''
                    st.markdown(bars_html, unsafe_allow_html=True)