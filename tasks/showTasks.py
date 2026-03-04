import streamlit as st

from services import sql_services as db

def showAllTasks():

    tasks = db.get_all_tasks()

    for t in tasks:
        rate = db.get_task_completion_rate(t["id"])
        st.markdown(f"""
        ### {t["type_name"]} - {t["frequency"]}
        优先级: {t["priority"]}
        完成率: {round(rate * 100, 2)}%
        ---
        """)

def todayTasks():

    tasks = db.get_today_tasks()

    if not tasks:
        st.info("今天没有任务 🎉")

    for t in tasks:
        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(f"**{t['type_name']}**")

        with col2:
            if t["finished_amount"] == 0:
                if st.button("完成", key=f"finish_{t['task_id']}"):
                    db.finish_today_task(t["task_id"])
                    st.rerun()
            else:
                st.success("已完成")