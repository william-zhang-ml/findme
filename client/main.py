"""
Dummy mobile client for testing GET and POST requests.
"""
import json
from typing import Any
from kivy.app import App
from kivy.graphics.texture import Texture
from kivy.network.urlrequest import UrlRequest
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout


class UserInterface(BoxLayout):
    """User interface. """
    _score = ObjectProperty(None)
    _quest = ObjectProperty(None)
    _image = ObjectProperty(None)
    _quest_but = ObjectProperty(None)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._get_user_data()

    def _get_user_data(self) -> None:
        req = UrlRequest(
            'http://localhost:8000/user/',
            on_success=self._unpack_user_data
        )
        req.wait(0)

    def _unpack_user_data(
        self,
        req: UrlRequest,
        result: Any
    ) -> None:
        """Update user display with new user data.

        Args:
            req (UrlRequest): HTTP(S) request
            result (Any): request result
        """
        self._score.text = f'Score: {result["total_score"]}'
        self._quest.text = f'Quest: {result["quest_cat"]}'
        self._quest_but.disabled = result['has_quest']

    def _get_new_quest(self) -> None:
        req = UrlRequest(
            'http://localhost:8000/newquest/',
            on_success=self._unpack_user_data
        )
        req.wait(0)

    def _submit(self) -> None:
        if self._image.texture is None:
            self._image.texture = Texture.create(
                size=(128, 256),
                colorfmt='rgb'
            )
        self._image.texture.flip_vertical()
        req = UrlRequest(
            'http://localhost:8000/score/',
            req_headers={'Content-Type': 'application/json'},
            req_body=json.dumps({
                'mode': 'RGB',
                'size': (128, 256),
                'data': self._image.texture.pixels.hex()
            }),
            on_success=lambda req, res: print(res)
        )
        req.wait(0)


class ClientApp(App):
    """Main application class. """
    def build(self) -> None:
        return UserInterface()


if __name__ == '__main__':
    ClientApp().run()
