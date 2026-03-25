import os
import requests
from bs4 import BeautifulSoup
import json
import hashlib

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

data_path = os.getenv('DATA_PATH', "/data")
url = 'https://ntcbadm1.ntub.edu.tw/StdAff/STDWeb/ABS_SearchSACP.aspx'

with open(os.path.join(data_path, 'watchlist.json'), encoding='utf-8') as fwatch_list:
    watch_list = json.load(fwatch_list)

for user, user_data in watch_list.items():
    session_id = user_data.get('sessionId')
    webhook_url = user_data.get('webhookUrl')
    try:
        web = requests.get(url, cookies={'ASP.NET_SessionId': session_id})
        soup = BeautifulSoup(web.text, features="html.parser")

        all_absences = soup.find('table', attrs={'id':'ctl00_ContentPlaceHolder1_GRD'})
        all_absences = all_absences.find_all('tr')

        checkfile_dir_path = os.path.join(data_path, '../usr')
        checkfile_path = os.path.join(checkfile_dir_path, user)
        if not os.path.exists(checkfile_dir_path):
            os.makedirs(checkfile_dir_path)
        if not os.path.exists(checkfile_path):
            open(checkfile_path, 'w').close()

        for absences in all_absences:
            try:
                if absences.td.get_text() == '曠課':
                    date = absences.find('span', attrs={'id':'ctl00_ContentPlaceHolder1_GRD_ctl02_lb_recdate'}).get_text()
                    class_num = absences.find('span', attrs={'id':'ctl00_ContentPlaceHolder1_GRD_ctl02_lb_totalsection'}).get_text()
                    class_count = len(class_num.split(','))

                    absences_id = hashlib.sha256((date + class_num).encode('utf-8')).hexdigest()

                    with open(checkfile_path, 'r') as checkfile:
                        checkfile_id = checkfile.read().splitlines()
                    if absences_id not in checkfile_id:
                        with open(checkfile_path, 'a') as checkfile:
                            checkfile.write(absences_id + '\n')
                            requests.post(webhook_url, json={
                                "embeds": [{
                                        "title": f"你有{class_count}節曠課",
                                        "description": f"**{date}**\n節數: {class_num}",
                                    }]
                            })
            except Exception as e:
                pass # The first row is used for header, so it doesn't have td tag, just skip it
    except Exception as e:
        print(e)
        requests.post(webhook_url, json={
            "content": f"Something went wrong! Usually session expire\n{e}"
        })