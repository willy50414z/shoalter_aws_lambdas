from util import google_sheet_util, datetime_util


def get_updated_row_idx(channel, msg_ts):
    print(f"[get_updated_row_idx]start, channel[{channel.value}]msg_ts[{msg_ts}]")
    sheet_json = google_sheet_util.find_all(channel.sheet_id, channel.channel_name)
    print(sheet_json)
    rows = sheet_json["values"]
    for i in range(1, len(rows)):
        if len(rows[i][1]) == 0:
            print("update date")
            RANGE = f"{channel.channel_name}!B{i + 1}"
            res = google_sheet_util.update(channel.sheet_id, RANGE, {"values": [[f"=K{i + 1}+8/24"]]})
            print(res.json())

            ts = datetime_util.datetime_str_to_ts(rows[i][10])
            datetime_str = datetime_util.ts_to_datetime_str(ts + 60 * 60 * 8)
            rows[i][1] = datetime_str

        if rows[i][0] == channel.channel_name and int(datetime_util.datetime_str_to_ts(rows[i][1])) == msg_ts:
            print(f"[get_updated_row_idx] find row index [{i}]")
            return i, len(rows)
    print(f"[get_updated_row_idx] cant find row index")
    return None, len(rows)

# def resolve(channel_name, msg_ts, event_time):
#     print(f"[resolve] start resolve,channel_name[{channel_name}]msg_ts[{msg_ts}]event_time[{event_time}]")
#     sheet_json = google_sheet_util.findAll(channel_name.sheet_id)
#     rows = sheet_json["values"]
#     for i in range(1, len(rows)):
#         # update datetime first if empty
#         if len(rows[i][1]) == 0:
#             print("update date")
#             RANGE = f"{channel_name.channel_name}!B{i + 1}"
#             res = google_sheet_util.update(channel_name.sheet_id, RANGE, {"values": [[f"=K{i + 1}+8/24"]]})
#             print(res.json())
#
#             ts = datetime_util.datetime_str_to_ts(rows[i][10])
#             datetime_str = datetime_util.ts_to_datetime_str(ts + 60 * 60 * 8)
#             rows[i][1] = datetime_str
#
#         # update target row to finish
#         # print(f"rows[i][{rows[i]}]channel_name[{channel_name}]ts[{msg_ts}]int(datetime_util.datetime_str_to_ts(rows[i][1]))[{int(datetime_util.datetime_str_to_ts(rows[i][1]))}]rows[i][0] == channel_name[{rows[i][0] == channel_name}]rows[i][1] == msg_time[{rows[i][1] == msg_ts}]")
#         if rows[i][0] == channel_name and int(datetime_util.datetime_str_to_ts(rows[i][1])) == msg_ts:
#             print("update to done")
#             RANGE = f"{channel_name.channel_name}!G{i + 1}:J{i + 1}"
#             res = google_sheet_util.update(channel_name.sheet_id, RANGE,
#                                            {"values": [["QA", "Y", event_time, "Wait QA test"]]})
#             print(res.json())
#             break
