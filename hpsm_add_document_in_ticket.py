#!/usr/bin/env python3

from action_hpsm import add_files
from BDoperations import execute_sql_query, auth
from urllib.request import urlopen
from loguru import logger


input_files = execute_sql_query("""UPDATE glpi_documents SET hpsm=true 
from glpi_tickets t
WHERE glpi_documents.hpsm=false and glpi_documents.glpi_ticket_id = t.glpi_id and t.hpsm_id is not null
returning t.hpsm_id, glpi_documents.filename, glpi_documents.filepath, glpi_documents.document_id;""", db=auth)

if input_files:
    for file in input_files:
        hpsm_id = file[0]
        file_name = file[1]
        file_path = urlopen(post_file_to_hpsm(file[2]))
        doc_id = file[3]
        new_file = add_files(hpsm_id, file_name, file_path)
        if new_file:
            logger.info(f'В обр {hpsm_id} успешно добавлен файл с id={doc_id}')
        else:
            execute_sql_query(f"UPDATE glpi_documents SET hpsm=false WHERE document_id={doc_id} returning 0;", db=auth)
