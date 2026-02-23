# Copyright 2026 TechnoLibre - Mathieu Benoit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from odoo.tests.common import HttpCase


class TestWebsiteEventRequireLoginBase(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # Create a test event with registration enabled
        cls.event = cls.env["event.event"].create(
            {
                "name": "Test Event Require Login",
                "date_begin": datetime.now() + timedelta(days=1),
                "date_end": datetime.now() + timedelta(days=2),
                "website_published": True,
                "website_require_login": True,
            }
        )
        # Create a ticket so registration is possible
        cls.ticket = cls.env["event.event.ticket"].create(
            {
                "name": "Free Registration",
                "event_id": cls.event.id,
                "seats_max": 100,
            }
        )
        # Create event without require login for comparison
        cls.event_no_login = cls.env["event.event"].create(
            {
                "name": "Test Event No Login Required",
                "date_begin": datetime.now() + timedelta(days=1),
                "date_end": datetime.now() + timedelta(days=2),
                "website_published": True,
                "website_require_login": False,
            }
        )
        cls.ticket_no_login = cls.env["event.event.ticket"].create(
            {
                "name": "Free Registration",
                "event_id": cls.event_no_login.id,
                "seats_max": 100,
            }
        )
        # Internal user for authenticated tests
        cls.user_internal = cls.env["res.users"].create(
            {
                "name": "Test Internal User",
                "login": "test_event_internal",
                "password": "test_event_internal",
                "groups_id": [
                    (4, cls.env.ref("base.group_user").id),
                ],
            }
        )
