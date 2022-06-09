#!/usr/bin/env python3

import psycopg2.extras
from loguru import logger
from glpi import GLPI
import os


os.chdir(r'/opt/sql/GLPI_Intagration') if os.name == 'posix' else os.chdir(r'C:\Users\Павел\GLPI_Intagration')
logger.add("logs/integrate.log", format="{time} {level} {message}", level="DEBUG", rotation="06:30", compression="zip")
auth = {'dbname': 'integration', 'user': 'postgres', 'password': 'postgres', 'host': '127.0.0.1'}
auth_hpsm = ('LOGIN', 'PASSWORD')


def execute_sql_query(*args, db):
    with psycopg2.connect(**db) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
            for i in args:
                cur.execute(i)
            rows = cur.fetchall()
    return rows


def MMC_GLPI():
    glpi = GLPI('http://URL/glpi/apirest.php',
                'APP_TOKEN', ('LOGIN', 'P@ssw0rd'))

    if not glpi.api_has_session():
        glpi.init_api()
    return glpi
