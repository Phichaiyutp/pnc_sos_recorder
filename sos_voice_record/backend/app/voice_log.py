from datetime import datetime, timedelta
from pytz import timezone as tz
import json
import os
from attachment_handler import AttachmentHandler
import mysql.connector
from mysql.connector import Error


def VoiceLogging():
    payload = {}
    try:
        # Establish connection
        connection = mysql.connector.connect(
            host=os.getenv('CITY_DB_HOST'),
            database=os.getenv('CITY_DB_NAME'),
            user=os.getenv('CITY_DB_USER'),
            password=os.getenv('CITY_DB_PASSWORD')
        )

        # Check if the connection is established
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            attachment_handler = AttachmentHandler()
            attachment_info = attachment_handler.get_attachments()

            if not attachment_info['ok']:
                payload = {'ok': False, 'status': 'Attachment not found'}
            else:
                i = 0
                sosinfo = []

                while len(attachment_info['data']) != len(sosinfo) and i < len(attachment_info['data']):
                    recorded_number = attachment_info['data'][i]['recorded']
                    s_ts = attachment_info['data'][i]['timestamp']
                    e_ts = s_ts + timedelta(seconds=60)
                    s_ts_str = s_ts.strftime("%Y-%m-%d %H:%M:%S")
                    e_ts_str = e_ts.strftime("%Y-%m-%d %H:%M:%S")
                    i += 1
                    #หา id ของไฟล์แรกที่จะเริ่มต้นการ map เสียง
                    cursor.execute("""
                            SELECT id, lastupdate, call_data
                            FROM sos_sosinfo ss 
                            WHERE status_id = 5 
                            AND JSON_UNQUOTE(JSON_EXTRACT(call_data, '$.called_data.number')) = %s
                            AND lastupdate >= %s 
                            AND lastupdate < FROM_UNIXTIME(UNIX_TIMESTAMP(%s) + call_durations)  
                            ORDER BY id ASC
                            LIMIT 1;
                        """, (recorded_number,s_ts_str, e_ts_str))
                    
                    sosinfo_record = cursor.fetchone()
                    if sosinfo_record:
                        sosinfo.append(sosinfo_record)
                        last_sos_id = sosinfo_record['id']
                        #List ไฟล์โดยเริ่มตั้งแต่ id ของไฟล์แรกที่จะเริ่มต้นการ map เสียง 
                        cursor.execute("""
                                SELECT id, lastupdate, call_data,call_durations
                                FROM sos_sosinfo ss 
                                WHERE status_id = 5
                                AND JSON_UNQUOTE(JSON_EXTRACT(call_data, '$.called_data.number')) = %s
                                AND id >= %s
                                ORDER BY id ASC;
                            """, (recorded_number,last_sos_id))

                        sosinfo = cursor.fetchall()
                for record in sosinfo:
                    if 'call_data' in record:
                        record['call_data'] = json.loads(record['call_data'])

                if len(attachment_info['data']) == len(sosinfo):
                    for index, path_data in enumerate(attachment_info['data']):
                        if index <= len(sosinfo):
                            id = sosinfo[index]['id']
                            call_durations = int(
                                sosinfo[index]['call_durations'])
                            call_data = sosinfo[index]['call_data']
                            lastupdate = sosinfo[index]['lastupdate'].replace(
                                tzinfo=tz('UTC'))
                            timestamp = path_data['timestamp'].replace(
                                tzinfo=tz('UTC'))
                            time_diff = (
                                lastupdate - timestamp).total_seconds() - call_durations
                            if (int(path_data['caller']) == int(call_data['caller_data']['caller_number'])) and (int(path_data['recorded']) == int(call_data['called_data']['number'])) and abs(time_diff) < 90:
                                path_data['id'] = int(id)
                                path_data['lastupdate'] = lastupdate
                else:
                    for _, path in enumerate(attachment_info['data']):
                        path['id'] = 0
                        path['lastupdate'] = datetime.now()
                        for _, source in enumerate(sosinfo):
                            id = source['id']
                            call_durations = int(source['call_durations'])
                            call_data = source['call_data']
                            lastupdate = source['lastupdate'].replace(
                                tzinfo=tz('UTC'))
                            timestamp = path['timestamp'].replace(
                                tzinfo=tz('UTC'))
                            time_diff = (
                                lastupdate - timestamp).total_seconds() - call_durations
                            if (int(path['caller']) == int(call_data['caller_data']['caller_number'])) and (int(path['recorded']) == int(call_data['called_data']['number'])) and abs(time_diff) < 90:
                                path['id'] = int(id)
                                path['lastupdate'] = lastupdate
                                break

                sos_ids = []
                call_timestamps = []
                for item in attachment_info['data']:
                    if 'id' in item and 'lastupdate' in item:
                        sos_ids.append(item['id'])
                        call_timestamps.append(item['lastupdate'])

                """ payload = {
                    'source': sosinfo,
                    'path': attachment_info['data']
                } """
                # ในกรณีที่ ข้อมูลที่จะนำไป Map เข้ากับ Path ถูกต้อง
                if len(sos_ids) and len(sos_ids) == len(call_timestamps):
                    download_attachments = attachment_handler.download_attachments(
                        sos_ids=sos_ids, call_timestamps=call_timestamps)
                    payload = download_attachments
            cursor.close()

            # Return the records as a JSON response
            return payload

    except Error as e:
        # Handle errors

        return {'ok': False, 'error': str(e)}

    finally:
        # Ensure the connection is closed
        if 'connection' in locals() and connection.is_connected():
            connection.close()