# Copyright 2026 TechnoLibre - Mathieu Benoit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from odoo.tests.common import TransactionCase


class TestEventModel(TransactionCase):
    """Unit tests for the event.event model extension."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(cls.env.context, tracking_disable=True)
        )
        cls.event_vals = {
            "name": "Test Event",
            "date_begin": datetime.now() + timedelta(days=1),
            "date_end": datetime.now() + timedelta(days=2),
        }

    def test_field_exists(self):
        """The website_require_login field should exist on event.event."""
        field = self.env["event.event"]._fields.get("website_require_login")
        self.assertIsNotNone(field)
        self.assertEqual(field.type, "boolean")

    def test_default_value_is_false(self):
        """website_require_login should default to False."""
        event = self.env["event.event"].create(self.event_vals)
        self.assertFalse(event.website_require_login)

    def test_set_true(self):
        """Setting website_require_login to True should persist."""
        event = self.env["event.event"].create(self.event_vals)
        event.website_require_login = True
        self.assertTrue(event.website_require_login)

    def test_set_false_after_true(self):
        """Toggling website_require_login back to False should persist."""
        event = self.env["event.event"].create(
            dict(self.event_vals, website_require_login=True)
        )
        self.assertTrue(event.website_require_login)
        event.website_require_login = False
        self.assertFalse(event.website_require_login)

    def test_create_with_true(self):
        """Creating an event with website_require_login=True."""
        event = self.env["event.event"].create(
            dict(self.event_vals, website_require_login=True)
        )
        self.assertTrue(event.website_require_login)

    def test_write_preserves_other_fields(self):
        """Writing website_require_login should not affect other fields."""
        event = self.env["event.event"].create(self.event_vals)
        original_name = event.name
        event.write({"website_require_login": True})
        self.assertTrue(event.website_require_login)
        self.assertEqual(event.name, original_name)

    def test_copy_preserves_field(self):
        """Duplicating an event should preserve website_require_login."""
        event = self.env["event.event"].create(
            dict(self.event_vals, website_require_login=True)
        )
        copied = event.copy()
        self.assertTrue(copied.website_require_login)

    def test_copy_preserves_false(self):
        """Duplicating an event with False should keep False."""
        event = self.env["event.event"].create(self.event_vals)
        copied = event.copy()
        self.assertFalse(copied.website_require_login)

    def test_search_by_require_login(self):
        """Searching events by website_require_login should work."""
        event_login = self.env["event.event"].create(
            dict(
                self.event_vals,
                name="Event With Login",
                website_require_login=True,
            )
        )
        event_no_login = self.env["event.event"].create(
            dict(
                self.event_vals,
                name="Event Without Login",
                website_require_login=False,
            )
        )
        results = self.env["event.event"].search(
            [("website_require_login", "=", True)]
        )
        self.assertIn(event_login, results)
        self.assertNotIn(event_no_login, results)

    def test_multiple_events_independent(self):
        """Each event should have its own independent require_login value."""
        event1 = self.env["event.event"].create(
            dict(
                self.event_vals,
                name="Event 1",
                website_require_login=True,
            )
        )
        event2 = self.env["event.event"].create(
            dict(
                self.event_vals,
                name="Event 2",
                website_require_login=False,
            )
        )
        self.assertTrue(event1.website_require_login)
        self.assertFalse(event2.website_require_login)
        # Changing one should not affect the other
        event2.website_require_login = True
        self.assertTrue(event1.website_require_login)
        self.assertTrue(event2.website_require_login)
