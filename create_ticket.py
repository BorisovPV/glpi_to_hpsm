#!/usr/bin/env python3

from BDoperations import execute_sql_query, auth
from action_hpsm import create_task
from glpi_action import hidden_comment
from loguru import logger


search_ticket_on_insert = execute_sql_query("""UPDATE glpi_tickets SET hpsm=true 
from ed_itilcategory 
WHERE glpi_tickets.hpsm=false and ed_itilcategory.itilcategories_id = glpi_tickets.itilcategories_id 
returning glpi_tickets.glpi_content_head, glpi_tickets.glpi_content_body, glpi_tickets.glpi_id, 
case when ed_itilcategory.template_hpsm_name is null then 'Шаблон для обращений по API ИС ММЦ' 
else ed_itilcategory.template_hpsm_name end as template_hpsm-- ed_itilcategory.template_hpsm_name;""", db=auth)


if search_ticket_on_insert:
    for task in search_ticket_on_insert:
        head = task[0]
        body = task[1]
        glpi_id = task[2]
        template = task[3]
        logger.info(f'По заявке {glpi_id} получены аргументы для создания обращения: {head}\n{body}\n{template}')
        sd_ticket = create_task(head=head, body=body, glpi_id=glpi_id, template_hpsm=template)
        if sd_ticket:
            SD = sd_ticket['ditMFSMAPI']['Key']
            execute_sql_query(f"select * from ticket_for_hpsm({glpi_id}, '{SD}')", db=auth)
            logger.info(f"По заявке {glpi_id} было создано обращение в HPSM под номером: {SD}")
            hidden_comment(glpi_id, f'Создано обращение в HPSM под номером: {SD}')
        else:
            logger.warning(f"{glpi_id}, не было создано обращение")
            execute_sql_query(f"""UPDATE glpi_tickets SET hpsm=false WHERE glpi_id = {glpi_id} returning 1;""", db=auth)
