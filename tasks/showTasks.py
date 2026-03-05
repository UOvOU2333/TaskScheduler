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

        col1, col2, col3, col_blank, col4 = st.columns([6, 6, 4, 3, 3])

        with col1:
            st.markdown(f"""
            <div style="font-size:25px;font-weight:600;margin:2px;margin-top:0">
                {t["task_name"]}
            </div>
            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                {render_capsule(t["type_name"], type_color)}{render_capsule(t["state_name"], state_color)}
            """, unsafe_allow_html=True)

        with col2:
            # ===== 优先级：5星制（支持半星） =====
            raw_priority = t["priority"] if t["priority"] is not None else 0
            raw_priority = max(0, min(int(raw_priority), 10))  # 仍然按0-10存储

            # 映射到5星（每2为1星）
            full_stars = raw_priority // 2
            has_half = (raw_priority % 2) == 1
            empty_stars = 5 - full_stars - (1 if has_half else 0)

            stars_html = ""

            # 满星
            for _ in range(full_stars):
                stars_html += "<span style='color:#FFD700;font-size:20px;'>★</span>"

            # 半星（使用渐变裁剪实现）
            if has_half:
                stars_html += """
                <span style='
                    font-size:20px;
                    background: linear-gradient(90deg, #FFD700 50%, #DDDDDD 50%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                '>★</span>
                """

            # 空星
            for _ in range(empty_stars):
                stars_html += "<span style='color:#DDDDDD;font-size:20px;'>★</span>"

            st.markdown(
                f"<div style='margin-bottom:6px;'>{stars_html}</div>",
                unsafe_allow_html=True
            )

            # ===== 频率展示优化 =====
            freq_map = {
                "daily": "每天",
                "weekly": "每周",
                "weekday": "工作日",
                "once": "单次",
                "everyTwoDay": "每两天",
                "everyThreeDay": "每三天",
                "everyTwoWeek": "每两周",
                "monthly": "每月"
            }

            frequency = t["frequency"]
            week_mask = t["week_mask"] if "week_mask" in t.keys() and t["week_mask"] is not None else 0

            if frequency in ("daily", "weekly", "weekday"):
                days_label = ["M", "T", "W", "T", "F", "S", "S"]
                circles = ""

                for i in range(7):
                    active = False

                    if frequency == "daily":
                        active = True
                    elif frequency == "weekday":
                        active = i < 5
                    else:  # weekly 使用掩码
                        active = (week_mask >> i) & 1 == 1

                    bg = "#4CAF50" if active else "#E0E0E0"
                    color = "#FFFFFF" if active else "#666666"

                    circles += f"""
                    <div style='width:26px;height:26px;border-radius:50%;
                                display:flex;align-items:center;justify-content:center;
                                background:{bg};color:{color};font-size:12px;'>
                        {days_label[i]}
                    </div>
                    """

                st.markdown(
                    f"""
                    <div style='display:flex;gap:6px;margin-top:4px;'>
                        {circles}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.caption(f"频率: {freq_map.get(frequency, frequency)}")

        with col3:
            if t["scheduled_end"]:
                st.write( t["scheduled_start"]+" ~ "+ t["scheduled_end"])
            else:
                st.write( t["scheduled_start"]+" ~ ")

            if rate:
                col_bar, col_word = st.columns([1,1])
                with col_bar:
                    st.progress(min(max(rate[2], 0.0), 1.0))
                with col_word:
                    st.caption(f"{round(rate[2] * 100, 2)}% ({rate[0]}/{rate[1]})")

        with col4:
            if st.button("修改", key=f"edit_{t['id']}", use_container_width=True):
                st.session_state["edit_task_id"] = t["id"]
                with col_blank:
                    st.success("已保存")

        with st.expander("任务详情", expanded=False):
            col_id, col_total, col_create = st.columns(3)
            with col_id:
                st.write("ID：" + str(t['id']))
            with col_total:
                st.write("总次数：" + str(t['total_amount']))
            with col_create:
                created_at = t['created_at']
                if hasattr(created_at, 'strftime'):
                    created_at = created_at.strftime('%Y-%m-%d %H:%M:%S')
                st.write("创建时间：" + str(created_at))

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

        col1, col2, col3 = st.columns([2, 2, 1])

        # ===== 左侧：卡片标题 + 胶囊 =====
        with col1:
            st.markdown(f"""
            <div style="font-size:25px;font-weight:600;margin-bottom:6px;">
                {t['task_name']}
            </div>
            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                {render_capsule(t['type_name'], type_color)}{render_capsule(t['state_name'], state_color)}
            """, unsafe_allow_html=True)

        # ===== 中间：完成状态 =====
        with col2:
            finished = t["finished_amount"]
            daily_target = t["daily_target"] if "daily_target" in t.keys() and t["daily_target"] is not None else 1

            # 进度条

            # 状态判断
            is_done = finished >= daily_target
            status_label = "已达标" if is_done else "进行中"
            status_color = "#4CAF50" if is_done else "#FF9800"

            progress_ratio = finished / daily_target if daily_target > 0 else 0.0
            progress_ratio = min(max(progress_ratio, 0.0), 1.0)

            st.markdown(
                render_capsule(f"{status_label}", status_color),
                unsafe_allow_html=True
            )

            st.progress(progress_ratio)
            st.caption(f"{finished} / {daily_target}")

        with col3:
            # ===== 操作按钮 =====

            if st.button("＋", key=f"finish_{t['task_id']}", use_container_width=True):
                taskDB.finish_today_task(t["task_id"])
                st.rerun()

            if finished > 0:
                if st.button("－", key=f"undo_{t['task_id']}", use_container_width=True):
                    taskDB.undo_today_task(t["task_id"])
                    st.rerun()

        st.divider()

def overview():
    today = datetime.date.today()

    # 获取昨天、今天和未来3天
    days = [today - datetime.timedelta(days=1) + datetime.timedelta(days=i) for i in range(5)]

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

                    bars_html = f'''
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <div style="width: 8px; height: 20px; background-color: {type_color}; border-radius: 4px;"></div>
                        <div style="font-weight: 500; white-space: nowrap;">{t['task_name']}</div>
                    </div>
                    '''
                    st.markdown(bars_html, unsafe_allow_html=True)