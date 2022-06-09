#!/usr/bin/env python3

import json
import time
from loguru import logger


class HPSM:
    # url = "http://212.11.152.168:13084/SM/9/rest/ditMFSMAPI"  # "http://sm.mos.ru:8090/SM/9/rest/ditMFSMAPI"

    url = "http://sm.mos.ru:8090/SM/9/rest/ditMFSMAPI"

    def __init__(self, session, entity, entity_number=None):
        self.entity = entity
        self.session = session
        self.attach_token = None
        if entity_number:
            self.entity_number = entity_number

    def hpsm_post_request(self, payload: str):
        try:
            try_times = 0
            response_hpsm = {}
            while not response_hpsm.get("ditMFSMAPI") and try_times != 9:
                time.sleep(try_times)
                if try_times > 7:
                    logger.warning(f'response_hpsm - {response_hpsm}')
                    pass
                try_times += 1
                response_hpsm = self.session.post(self.url, data=payload).json()
            return response_hpsm

        except Exception as er:
            logger.warning(f'Error HPSM: {er}. Data_post was:\n{payload}')
            return False

    def get_attach_token(self):
        payload = {"ditMFSMAPI": {
            "Action": "getAttachToken",
            "Key": self.entity_number,
            "Filename": self.entity
        }
        }
        response_attach_token = self.hpsm_post_request(json.dumps(payload))
        return response_attach_token['ditMFSMAPI']['AttachToken']

    def add_comments(self, sd: str, comment: str):
        payload = {
            "ditMFSMAPI": {
                "Action": "addProtocol",
                "Key": sd,
                "Filename": self.entity,
                "ParamsNames": ["Тематика", "Сообщение", "Видно пользователю"],
                "ParamsValues": ["Дополнительная информация", f"{comment}", "false"]
            }
        }
        response = self.hpsm_post_request(json.dumps(payload))

        try:
            if response.get('ditMFSMAPI').get('Status') == 'SUCCESS':
                logger.info(f'В hpsm добавлен коммент {response}')
                return response
        except Exception as err:
            logger.warning(f'Error HPSM: {err}. Data_post was:\n{payload}')
            return False

    def attach_file(self, file_name, data):
        """
        Крепит к номеру сущности(например к номеру проблемы) self.entity_number файл
        с именем file_name и самого файла в виде байт - data.
        Полученный token указывает только на одну сущность в HPSM(например на PM00009303),
        куда по токену будут загружены файлы
        """
        headers = {
            'Content-Type': 'application/octet-stream',
            f'Content-Disposition': f'attachment; filename={file_name}',
        }

        if not self.attach_token:
            self.attach_token = self.get_attach_token()

        if self.attach_token:
            url_with_token = f"{self.url}/{self.attach_token}/attachments"
            try:
                try_times = 0
                response = {}
                while not response.get('attachment') and try_times != 7:
                    time.sleep(try_times)
                    try_times += 1
                    if try_times > 7:
                        pass
                    response = self.session.post(url_with_token, data=data, headers=headers).json()
                logger.info(f'В hpsm добавлен документ {file_name}\n {response} \nURL - {url_with_token}')
                return response
            except Exception as er:
                time.sleep(5)
                response = self.session.post(url_with_token, data=data, headers=headers).json()
                return response
        else:
            return False

    def accepted_sd(self, sd, solution):
        payload = {
                  "ditMFSMAPI": {
                     "Action": "execSMAction",
                     "Filename": self.entity,
                     "Key": sd,
                     "ParamsNames": ["SMAction", "Поле: Решение", "Поле: Код выполнения"],
                     "ParamsValues": ["Выполнить", f"{solution}", "выполнено"]
                  }
                }
        response = self.hpsm_post_request(json.dumps(payload))

        try:
            if response.get('ditMFSMAPI').get('Status') == 'SUCCESS':
                return response
        except Exception as err:
            logger.warning(f'Error HPSM: {err}. Data_post was:\n{payload}')
            return False

    def create_task_on_hpsm(self, body, head, glpi_id, hpsm_template):
        payload = {
              "ditMFSMAPI": {
                 "Action": "create",
                 "Filename": "Обращение",
                 "ParamsNames": ["Шаблон", "Поле: Контактное лицо","Поле: Email заявителя", "Поле: Инициатор", "Поле: Описание", "Поле: Краткое описание", "Поле: Внешняя система: Название", "Поле: Внешняя система: Код заявки"],
                 "ParamsValues": [hpsm_template, "Сервисная ИС ММЦ_2833503", "integration.mmc@it2g.ru", "Сервисная ИС ММЦ_2833503", f"{body}", f"{head}", "GLPI_GBU_MMC", f"{glpi_id}"]
              }
            }
        response = self.hpsm_post_request(json.dumps(payload))

        try:
            if response.get('ditMFSMAPI').get('Status') == 'SUCCESS':
                logger.info(f'В hpsm создано обращение {response} \nПо запросу {payload}')
                return response
        except Exception as err:
            logger.warning(f'Error HPSM: {err}. Data_post was:\n{payload}')
            return False
