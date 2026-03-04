import streamlit as st
from datetime import date

from services import sql_services as db

def createTask():

    types = db.get_task_types()
    states = db.get_task_states()

    type_dict = {t["type_name"]: t["id"] for t in types}
    state_dict = {s["state_name"]: s["id"] for s in states}

    col1, col2 = st.columns(2)

    with col1:
        type_name = st.selectbox("任务类型", list(type_dict.keys()))
        state_name = st.selectbox("初始状态", list(state_dict.keys()))
        frequency = st.selectbox(
            "周期",
            ["once", "daily", "everyTwoDay",
             "everyThreeDay", "weekly",
             "everyTwoWeek", "monthly", "weekday"]
        )

        start = st.date_input("开始日期", value=date.today())
        end = st.date_input("结束日期（可选）", value=None)

    with col2:
        priority = st.slider("优先级", 0, 10, 5)
        total_amount = st.number_input("目标次数", min_value=1, value=1)

        st.write("选择星期（用于 weekly / weekday）")

        weekdays = st.multiselect(
            "选择星期",
            ["周日", "周一", "周二", "周三",
             "周四", "周五", "周六"]
        )

        week_map = {
            "周日": 0, "周一": 1, "周二": 2,
            "周三": 3, "周四": 4,
            "周五": 5, "周六": 6
        }

        week_mask = 0
        for w in weekdays:
            week_mask |= (1 << week_map[w])
    
    if st.button("创建任务", key="createTask"):
        db.create_task(
            type_dict[type_name],
            state_dict[state_name],
            frequency,
            week_mask,
            start.isoformat(),
            end.isoformat() if end else None,
            total_amount,
            priority
        )
        st.success("任务创建成功！")