#!/usr/bin/env python3

from action_hpsm import create_task
from BDoperations import execute_sql_query, auth
from glpi_action import hidden_comment
from loguru import logger


search_reopen_ticket = execute_sql_query("""select glpi_id, gt.glpi_content_head, gt.glpi_content_body, 
case when ei.template_hpsm_name is null then 'Шаблон для обращений по API ИС ММЦ' else ei.template_hpsm_name end as template_hpsm from glpi_tickets gt
left join ed_itilcategory ei on ei.itilcategories_id = gt.itilcategories_id 
where hpsm_close and glpi_solution is not null and hpsm and glpi_close_date_ts is null and glpi_ticket_status_id not in (5,6) and zni is null and pm is null limit 4""", db=auth)


if search_reopen_ticket:
    for ticket in search_reopen_ticket:
        glpi_id = ticket[0]
        body = ticket[2]
        head = ticket[1]
        template = ticket[3]
        reopen = create_task(body=body, head=head, glpi_id=glpi_id, template_hpsm=template)
        if reopen:
            SD = reopen['ditMFSMAPI']['Key']
            execute_sql_query(f"select * from reopen_ticket({glpi_id}, '{SD}')", db=auth)
            hidden_comment(glpi_id, f'Создано обращение в HPSM под номером: {SD}')
            logger.info(f'По заявке {glpi_id} было переоткрыто обращение {SD}')

