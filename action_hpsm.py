#!/usr/bin/env python3

import requests
from hpsm import HPSM
from BDoperations import auth_hpsm


def add_comments(sd, comment):
    with requests.Session() as session:
        session.auth = auth_hpsm
        create = HPSM(session=session, entity='Обращение')
        hpsm_response = create.add_comments(sd=sd, comment=comment)
        return hpsm_response


def accept_ticket(sd, solution):
    with requests.Session() as session:
        session.auth = auth_hpsm
        accept = HPSM(session=session, entity='Обращение', entity_number=sd)
        hpsm_response = accept.accepted_sd(sd=sd, solution=solution)

    return hpsm_response


def create_task(body, head, glpi_id, template_hpsm):
    with requests.Session() as session:
        session.auth = auth_hpsm
        create = HPSM(session=session, entity='Обращение')
        hpsm_response = create.create_task_on_hpsm(body=body, head=head, glpi_id=glpi_id, hpsm_template=template_hpsm)

    return hpsm_response