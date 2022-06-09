#!/usr/bin/python3

import threading
import transliterate
from BDoperations import execute_sql_query, logger, auth, MMC_GLPI
import re


findCriteria_all_tickets_on_mod = {"criteria": [{"link": None, "searchtype": "equals", "field": "Group_Group.completename", "value": "42"},
                                                {"link": "AND", "searchtype": "morethan", "field": "date_mod", "value": "-1HOUR"}]}
glpi = MMC_GLPI()


def check_user(user_id):
    user = execute_sql_query(f"""select * from glpi_users gu where user_id = {user_id}""", db=auth)
    if not user:
        user_info = glpi.api_rest.request(method='get', url=r'User/' + str(user_id)).json()
        fio_user = user_info.get('realname') + ' ' + str(user_info.get('firstname'))
        execute_sql_query(f"select * from add_users({user_id}, '{fio_user}', False)", db=auth)
    return user_id


def get_executors(ticket, one_solve):
    solution_executor = glpi.api_rest.request(method='get', url=r'Ticket/' + str(ticket) + '/ITILSolution').json()
    if solution_executor:
        for solve in solution_executor:
            user_id, solution_text = check_user(solve['users_id']), solve['content']
    else:
        user_id, solution_text = 'None', one_solve
    return user_id, solution_text


def additional_ticket(glpi_id, ticket_status, solution, head, body, created_ts, solution_ts, mod_ts, executor, close_ts, requesttypes_id, itilcategories_id):
    execute_sql_query(f"select * from added_ticket({glpi_id},'None', 'None', '{solution}', '{executor}', {ticket_status}, '{head}', '{body}', '{solution_ts}', '{created_ts}', '{mod_ts}', '{close_ts}', '{requesttypes_id}', '{itilcategories_id}')", db=auth)


def translit_name_doc(name):
    try:
        new_val = re.sub("№|—", "", name)
        name_translit = transliterate.translit(new_val, reversed=True)
        return name_translit
    except transliterate.exceptions.LanguageDetectionError:
        extension = name.split('.')[-1]
        new_val = 'any_document.' + str(extension)
        return new_val


def get_documet_glpi(links, glpi_id):
    for link in links:
        if link['rel'] == 'Document_Item':
            items = glpi.get_doc(link['href'])
            for item in items:
                for link in item.get("links"):
                    if link.get("rel") == 'Document':
                        add_documnets(glpi.get_doc(link.get("href")), glpi_id)


def add_documnets(documents, glpi_id):
    doc_id = documents['id']
    filename = translit_name_doc(documents['filename'])
    user_id = check_user(documents['users_id'])
    date = documents['date_creation']
    path = 'http://URL/glpi/files/'
    path += documents.get('filepath')
    mime = documents['mime']
    new_file = execute_sql_query(f"select * from add_document({glpi_id}, {doc_id}, '{filename}', {user_id}, '{date}', '{path}', '{mime}')", db=auth)
    if new_file[0][0]:
        logger.info(f"{doc_id} новый документ добавлен в бд")


def comments(gli_id):
    comments_glpi_ticket = glpi.api_rest.request(method='get', url=r'Ticket/' + str(gli_id) + '/ITILFollowup').json()
    for comment in comments_glpi_ticket:
        COM_ID = comment['id']
        COM_DATE = comment['date']
        COM_PRIVATE = True if comment['is_private'] == 1 else False
        COM_CONTENT = str(comment['content'])
        USER_ID = check_user(comment['users_id'])
        new_comment = execute_sql_query(f"select * from added_comment('{COM_ID}', '{gli_id}', '{COM_CONTENT}', '{COM_DATE}', '{USER_ID}', {COM_PRIVATE})", db=auth)
        if new_comment:
            logger.info(f"Комментарий с id={COM_ID} был добавлен в бд")


try:
    response = glpi.search_engine('ticket', findCriteria_all_tickets_on_mod)['data']
except KeyError:
    pass
except Exception as err:
    logger.error(err)

for count, info_ticket in enumerate(response):
    info = glpi.get('Ticket', info_ticket['2'])
    glpi_id = info['id']
    executor, solution = get_executors(ticket=glpi_id, one_solve=info_ticket['24'])
    head, body, ticket_status = info['name'], info['content'], info['status']
    created_ts, solution_ts, mod_ts, close_ts = info['date_creation'], info['begin_waiting_date'], info['date_mod'], info['closedate']
    requesttypes_id, itilcategories_id = info['requesttypes_id'], info['itilcategories_id']
    ThreadDocuments = threading.Thread(target=get_documet_glpi, args=[info['links'], glpi_id])
    ThreadDocuments.start()
    ThreadTicket = threading.Thread(target=additional_ticket, args=[glpi_id, ticket_status, solution, head, body, created_ts, solution_ts, mod_ts, executor, close_ts, requesttypes_id, itilcategories_id])
    ThreadTicket.start()
    ThreadComment = threading.Thread(target=comments, args=[glpi_id])
    ThreadComment.start()
    if count % 5 == 0:
        ThreadDocuments.join()
        ThreadTicket.join()
        ThreadComment.join()
