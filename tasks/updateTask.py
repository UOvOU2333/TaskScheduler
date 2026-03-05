import streamlit as st
from datetime import date

from services import task_services as taskDB

freq_display_list = [
    "一次性",
    "每天",
    "工作日",
    "每周",
    "每月",
    "每两天",
    "每三天",
    "每两周"
]

freq_map = {
    "一次性": "once",
    "每天": "daily",
    "每两天": "everyTwoDay",
    "每三天": "everyThreeDay",
    "每周": "weekly",
    "每两周": "everyTwoWeek",
    "每月": "monthly",
    "工作日": "weekday"
}

def updateTask():

    types = taskDB.get_task_types()

    edit_task_id = st.session_state.get("edit_task_id")
    task_data = None

    states = taskDB.get_task_states()

    type_dict = {t["type_name"]: t["id"] for t in types}
    state_dict = {s["state_name"]: s["id"] for s in states}

    col1, col2 = st.columns(2)

    with col1:
        col_name, col_id = st.columns(2)
        with col_id:
            task_id = st.number_input("任务编号", value=edit_task_id, step=1)

        # 根据当前输入的 task_id 查询任务
        if task_id:
            try:
                task_data = taskDB.get_task_by_id(int(task_id))
            except Exception:
                task_data = None

        # 检查任务是否存在
        task_exists = task_data is not None

        with col_name:
            task_name = st.text_input(
                "任务名称",
                value=task_data["task_name"] if task_data else ""
            )

        if not task_id:
            st.warning("请输入任务ID或在总列表中点击修改")
        else:
            if not task_exists:
                st.error("任务ID不存在")
            else:
                col_fre, col_mask = st.columns(2)
                with col_fre:
                    reverse_freq_map = {v: k for k, v in freq_map.items()}
                    default_freq_display = (
                        reverse_freq_map.get(task_data["frequency"]) if task_data else freq_display_list[0]
                    )
                    freq_display = st.selectbox(
                        "周期",
                        freq_display_list,
                        index=freq_display_list.index(default_freq_display)
                    )
                frequency = freq_map[freq_display]

                col_type, col_state = st.columns(2)

                type_keys = list(type_dict.keys())
                state_keys = list(state_dict.keys())

                default_type = None
                default_state = None
                if task_data:
                    for k, v in type_dict.items():
                        if v == task_data["type_id"]:
                            default_type = k
                    for k, v in state_dict.items():
                        if v == task_data["state_id"]:
                            default_state = k

                with col_type:
                    type_name = st.selectbox(
                        "任务类型",
                        type_keys,
                        index=type_keys.index(default_type) if default_type else 0
                    )
                with col_state:
                    state_name = st.selectbox(
                        "初始状态",
                        state_keys,
                        index=state_keys.index(default_state) if default_state else 0
                    )
                
                col_start, col_end = st.columns(2)
                with col_start:
                    start = st.date_input(
                        "开始日期",
                        value=date.fromisoformat(task_data["scheduled_start"]) if task_data and task_data["scheduled_start"] else date.today()
                    )
                with col_end:
                    end = st.date_input(
                        "结束日期（可选）",
                        value=date.fromisoformat(task_data["scheduled_end"]) if task_data and task_data["scheduled_end"] else None
                    )

                with col2:
                    priority = st.slider(
                        "优先级",
                        0,
                        10,
                        value=task_data["priority"] if task_data else 5
                    )

                    col_total, col_daily = st.columns(2)
                    with col_total:
                        total_amount = st.number_input(
                            "总目标次数",
                            min_value=1,
                            value=task_data["total_amount"] if task_data else 1
                        )
                    with col_daily:
                        daily_target = st.number_input(
                            "每日目标次数",
                            min_value=1,
                            value=task_data["daily_target"] if task_data else 1
                        )

                    all_weekdays = ["周日", "周一", "周二", "周三",
                                    "周四", "周五", "周六"]

                    week_map = {
                        "周日": 0, "周一": 1, "周二": 2,
                        "周三": 3, "周四": 4,
                        "周五": 5, "周六": 6
                    }

                    week_mask = 0
                    with col_mask:
                        if frequency == "weekly":
                            weekdays = st.multiselect("选择星期", all_weekdays)
                            for w in weekdays:
                                week_mask |= (1 << week_map[w])

                        elif frequency == "weekday":
                            # 自动选择周一到周五
                            weekdays = ["周一", "周二", "周三", "周四", "周五"]
                            for w in weekdays:
                                week_mask |= (1 << week_map[w])
                        
                        elif frequency == "daily":
                            # 自动选择全周
                            weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
                            for w in weekdays:
                                week_mask |= (1 << week_map[w])
    if task_id and  task_exists:
        if st.button("修改任务", key="updateTask", type="primary", use_container_width=True):
            if not task_name:
                st.warning("请输入任务名称")
                return

            taskDB.update_task(
                task_id,
                task_name,
                type_dict[type_name],
                state_dict[state_name],
                frequency,
                week_mask,
                start.isoformat(),
                end.isoformat() if end else None,
                total_amount,
                daily_target,
                priority
            )
            st.success("任务修改成功！")