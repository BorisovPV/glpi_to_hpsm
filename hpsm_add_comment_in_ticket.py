#!/usr/bin/env python3

from action_hpsm import add_comments
from BDoperations import execute_sql_query, auth
from loguru import logger


search_comment = execute_sql_query("""select distinct gt.hpsm_id, concat_ws(' - ',gc.glpi_comment_date, gu.description, gc.glpi_comment_content), gc.comment_id, gc.glpi_comment_date  from glpi_comments gc 
join glpi_tickets gt on gc.glpi_ticket_id = gt.glpi_id 
join glpi_users gu on gc.glpi_commnet_user_id = gu.user_id 
join hpsm_ticket ht on ht.glpi_id = gc.glpi_ticket_id 
where 1=1
and gc.hpsm is false 
and gt.hpsm and gc.glpi_commnet_user_id != 4050
and ht.reopen_ts::date >= current_date - '2 day'::interval 
order by gc.glpi_comment_date limit 4""", db=auth)

if search_comment:
    for comment in search_comment:
        hpsm_sd = comment[0]
        content = comment[1]
        com_id = comment[2]
        com_in_sd = add_comments(hpsm_sd, content)
        if com_in_sd:
            execute_sql_query(f"UPDATE glpi_comments SET hpsm=true WHERE comment_id={com_id} returning 0;", db=auth)
            logger.info(f'В обр {hpsm_sd} добавлен комментарий в протокол с id={com_id}')
