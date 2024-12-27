"""
Dummy mobile client for testing GET and POST requests.
"""
import json
from typing import Any
from kivy.app import App
from kivy.network.urlrequest import UrlRequest
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout


class UserInterface(BoxLayout):
    """User interface. """
    _user_data = ObjectProperty(None)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._get_user_data()

    def _get_user_data(self) -> None:
        UrlRequest(
            'http://localhost:8000/user/',
            on_success=self._render_user_data
        )

    def _render_user_data(
        self,
        req: UrlRequest,
        result: Any
    ) -> None:
        """Update user display with new user data.

        Args:
            req (UrlRequest): HTTP(S) request
            result (Any): request result
        """
        self._user_data.text = json.dumps(result)


class ClientApp(App):
    """Main application class. """
    def build(self) -> None:
        return UserInterface()


if __name__ == '__main__':
    ClientApp().run()
