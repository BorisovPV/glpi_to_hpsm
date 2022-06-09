#!/usr/bin/env python3

from BDoperations import MMC_GLPI


glpi = MMC_GLPI()


def close_glpi_ticket(ticket):
    glpi.update('ticket', {"id": ticket, "status": 6})


def add_comment_to_ticket(ticket, comment):
    glpi.createFollowup('ticket',
                        {"itemtype": "Ticket", "items_id": int(ticket), "tickets_id": int(ticket),
                         "content": str(comment)})


def hidden_comment(ticket, comment):
    glpi.createFollowup('ticket',
                        {
                            "itemtype": "Ticket", "items_id": int(ticket), "tickets_id": int(ticket), "is_private": "1",
                            "content": str(comment)
                        }
                        )