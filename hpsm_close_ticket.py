#!/usr/bin/env python3

from action_hpsm import accept_ticket
from BDoperations import execute_sql_query, auth
from loguru import logger


search_ticket_to_close = execute_sql_query("""select glpi_id, hpsm_id, glpi_solution from glpi_tickets gt
where glpi_ticket_status_id in (5,6) and hpsm_id is not null and hpsm_close is False""", db=auth)


if search_ticket_to_close:
    for ticket in search_ticket_to_close:
        glpi_id = ticket[0]
        SD = ticket[1]
        solution = ticket[2]
        if solution is None:
            solution = 'Выполнено'
        close = accept_ticket(sd=SD, solution=solution)
        if close:
            execute_sql_query(f"UPDATE glpi_tickets SET hpsm_close=true WHERE glpi_id={glpi_id} returning 0;", db=auth)
            logger.info(f'В hpsm закрыто {SD}, по заявке {glpi_id}')

