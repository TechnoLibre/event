# Copyright 2026 TechnoLibre - Mathieu Benoit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from odoo.tests import tagged

from .common import TestWebsiteEventRequireLoginBase


@tagged("post_install", "-at_install")
class TestWebsiteEventRequireLogin(TestWebsiteEventRequireLoginBase):
    def _build_registration_post_data(self, ticket):
        """Build minimal POST data to trigger the registration_new controller.

        The parent controller _process_tickets_form expects keys like
        ``nb_register-{ticket_id}`` with an integer count.
        """
        return {
            f"nb_register-{ticket.id}": 1,
        }

    def _registration_url(self, event):
        return f"/event/{event.id}/registration/new"

    def _json_rpc_post(self, url, params):
        """Send a JSON-RPC POST request as the website_event
        registration_new endpoint uses type='json'."""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "id": 1,
            "params": params,
        }
        return self.url_open(
            url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )

    def _get_json_result(self, response):
        """Extract JSON-RPC result as a string.

        The result can be a string (HTML), False/None (no tickets),
        or other types depending on the flow.
        """
        result = response.json().get("result", "")
        if not result:
            return ""
        return str(result)

    # ------------------------------------------------------------------
    # Case 1: Public user + require_login enabled -> modal returned
    # ------------------------------------------------------------------
    def test_public_user_require_login_returns_modal(self):
        """When a non-authenticated user tries to register on an event
        that requires login, the controller must return the login-required
        modal instead of the normal registration flow."""
        self.authenticate(None, None)  # public / anonymous session
        url = self._registration_url(self.event)
        post_data = self._build_registration_post_data(self.ticket)
        response = self._json_rpc_post(url, post_data)
        self.assertEqual(response.status_code, 200)
        result = self._get_json_result(response)
        # The modal template id must be present in the returned HTML
        self.assertIn(
            "modal_attendees_registration_login_required",
            result,
            "The login-required modal should be rendered for public users "
            "when website_require_login is enabled.",
        )
        # The modal should contain a login link redirecting to the event
        self.assertIn(
            "/web/login?redirect=",
            result,
            "The modal should contain a login redirect link.",
        )

    # ------------------------------------------------------------------
    # Case 2: Authenticated user + require_login enabled -> normal flow
    # ------------------------------------------------------------------
    def test_authenticated_user_require_login_no_modal(self):
        """When an authenticated user registers on an event that requires
        login, the controller must proceed with the normal registration
        flow (no modal)."""
        self.authenticate(
            self.user_internal.login,
            self.user_internal.login,
        )
        url = self._registration_url(self.event)
        post_data = self._build_registration_post_data(self.ticket)
        response = self._json_rpc_post(url, post_data)
        self.assertEqual(response.status_code, 200)
        result = self._get_json_result(response)
        self.assertNotIn(
            "modal_attendees_registration_login_required",
            result,
            "The login-required modal must NOT appear for authenticated users.",
        )

    # ------------------------------------------------------------------
    # Case 3: Public user + require_login disabled -> normal flow
    # ------------------------------------------------------------------
    def test_public_user_no_require_login_no_modal(self):
        """When website_require_login is disabled, even a public user
        should go through the standard registration flow without the
        login modal."""
        self.authenticate(None, None)
        url = self._registration_url(self.event_no_login)
        post_data = self._build_registration_post_data(self.ticket_no_login)
        response = self._json_rpc_post(url, post_data)
        self.assertEqual(response.status_code, 200)
        result = self._get_json_result(response)
        self.assertNotIn(
            "modal_attendees_registration_login_required",
            result,
            "The login-required modal must NOT appear when the feature "
            "is disabled, even for public users.",
        )

    # ------------------------------------------------------------------
    # Case 4: Authenticated user + require_login disabled -> normal flow
    # ------------------------------------------------------------------
    def test_authenticated_user_no_require_login_no_modal(self):
        """An authenticated user on an event without require_login
        should go through normal registration without modal."""
        self.authenticate(
            self.user_internal.login,
            self.user_internal.login,
        )
        url = self._registration_url(self.event_no_login)
        post_data = self._build_registration_post_data(self.ticket_no_login)
        response = self._json_rpc_post(url, post_data)
        self.assertEqual(response.status_code, 200)
        result = self._get_json_result(response)
        self.assertNotIn(
            "modal_attendees_registration_login_required",
            result,
            "The login-required modal must NOT appear for authenticated "
            "users when the feature is disabled.",
        )

    # ------------------------------------------------------------------
    # Case 5: Modal contains correct event URL
    # ------------------------------------------------------------------
    def test_modal_login_redirect_contains_event_url(self):
        """The login redirect in the modal should point to the event."""
        self.authenticate(None, None)
        url = self._registration_url(self.event)
        post_data = self._build_registration_post_data(self.ticket)
        response = self._json_rpc_post(url, post_data)
        result = self._get_json_result(response)
        # The event URL should be embedded in the redirect link
        self.assertIn(
            self.event.website_url,
            result,
            "The modal login redirect should contain the event URL.",
        )

    # ------------------------------------------------------------------
    # Case 6: Modal content structure
    # ------------------------------------------------------------------
    def test_modal_contains_login_link(self):
        """The modal should contain a link to /web/login."""
        self.authenticate(None, None)
        url = self._registration_url(self.event)
        post_data = self._build_registration_post_data(self.ticket)
        response = self._json_rpc_post(url, post_data)
        result = self._get_json_result(response)
        self.assertIn(
            "btn btn-primary",
            result,
            "The modal should contain a primary button (login link).",
        )

    def test_modal_contains_dismiss_button(self):
        """The modal should contain a dismiss/close button."""
        self.authenticate(None, None)
        url = self._registration_url(self.event)
        post_data = self._build_registration_post_data(self.ticket)
        response = self._json_rpc_post(url, post_data)
        result = self._get_json_result(response)
        self.assertIn(
            "js_goto_event",
            result,
            "The modal should contain a dismiss button with "
            "js_goto_event class.",
        )

    def test_modal_has_proper_structure(self):
        """The modal should have header, body and footer."""
        self.authenticate(None, None)
        url = self._registration_url(self.event)
        post_data = self._build_registration_post_data(self.ticket)
        response = self._json_rpc_post(url, post_data)
        result = self._get_json_result(response)
        self.assertIn("modal-header", result)
        self.assertIn("modal-body", result)
        self.assertIn("modal-footer", result)

    # ------------------------------------------------------------------
    # Case 7: Validate the field on event model
    # ------------------------------------------------------------------
    def test_website_require_login_field_default(self):
        """The website_require_login field should default to False."""
        event = self.env["event.event"].create(
            {
                "name": "Event Default Field Test",
                "date_begin": self.event.date_begin,
                "date_end": self.event.date_end,
            }
        )
        self.assertFalse(
            event.website_require_login,
            "website_require_login should default to False.",
        )

    def test_website_require_login_field_toggle(self):
        """Toggling website_require_login should persist correctly."""
        self.event.website_require_login = False
        self.assertFalse(self.event.website_require_login)
        self.event.website_require_login = True
        self.assertTrue(self.event.website_require_login)

    # ------------------------------------------------------------------
    # Case 8: Event page renders with data-require-login attribute
    # ------------------------------------------------------------------
    def test_event_page_has_require_login_attribute(self):
        """The event registration page should include the
        data-require-login attribute when enabled."""
        self.authenticate(None, None)
        url = f"/event/{self.event.id}/register"
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "data-require-login",
            response.text,
            "The registration form should contain data-require-login "
            "attribute when website_require_login is True.",
        )

    def test_event_page_require_login_value_one(self):
        """data-require-login should be '1' for public user on an
        event that requires login."""
        self.authenticate(None, None)
        url = f"/event/{self.event.id}/register"
        response = self.url_open(url)
        self.assertIn(
            'data-require-login="1"',
            response.text,
            "data-require-login should be '1' for public user.",
        )

    def test_event_page_no_require_login_attribute_absent(self):
        """When require_login is disabled, QWeb renders a falsy value
        (0) for data-require-login, which means the attribute is not
        rendered at all in the HTML."""
        self.authenticate(None, None)
        url = f"/event/{self.event_no_login.id}/register"
        response = self.url_open(url)
        self.assertNotIn(
            'data-require-login="1"',
            response.text,
            "data-require-login='1' must NOT appear when feature is "
            "disabled.",
        )

    def test_event_page_authenticated_no_require_login_attribute(self):
        """For authenticated users, data-require-login should not be
        '1' even when the event requires login."""
        self.authenticate(
            self.user_internal.login,
            self.user_internal.login,
        )
        url = f"/event/{self.event.id}/register"
        response = self.url_open(url)
        self.assertNotIn(
            'data-require-login="1"',
            response.text,
            "data-require-login='1' must NOT appear for authenticated "
            "users.",
        )

    # ------------------------------------------------------------------
    # Case 9: Toggling require_login changes behavior dynamically
    # ------------------------------------------------------------------
    def test_disable_require_login_allows_public_registration(self):
        """After disabling require_login, public users should be able
        to register without the modal."""
        self.event.website_require_login = False
        self.authenticate(None, None)
        url = self._registration_url(self.event)
        post_data = self._build_registration_post_data(self.ticket)
        response = self._json_rpc_post(url, post_data)
        self.assertEqual(response.status_code, 200)
        result = self._get_json_result(response)
        self.assertNotIn(
            "modal_attendees_registration_login_required",
            result,
            "After disabling require_login, no modal should appear.",
        )

    def test_enable_require_login_blocks_public_registration(self):
        """After enabling require_login on an event that did not have it,
        public users should see the modal."""
        self.event_no_login.website_require_login = True
        self.authenticate(None, None)
        url = self._registration_url(self.event_no_login)
        post_data = self._build_registration_post_data(self.ticket_no_login)
        response = self._json_rpc_post(url, post_data)
        self.assertEqual(response.status_code, 200)
        result = self._get_json_result(response)
        self.assertIn(
            "modal_attendees_registration_login_required",
            result,
            "After enabling require_login, the modal should appear.",
        )
