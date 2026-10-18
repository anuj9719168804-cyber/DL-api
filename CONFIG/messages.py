# Messages Configuration - per-user language (English is the default and the fallback for any missing key)
import sys
import os
import logging

logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(__file__))

from CONFIG.LANGUAGES.messages_EN import Messages as EnglishMessages
from CONFIG.LANGUAGES.language_router import language_router


class Messages(object):
    def __init__(self, user_id=None, language_code=None):
        """Messages for one user. language_code wins; otherwise the user's saved lang.txt; otherwise English."""
        self.user_id = user_id
        if language_code is None and user_id is not None:
            try:
                language_code = language_router.get_user_language(user_id)
            except Exception:
                language_code = 'en'
        self.language_code = language_code or 'en'
        self._en_messages = EnglishMessages()
        self._lang = {}
        if self.language_code != 'en':
            try:
                self._lang = language_router.load_messages(self.language_code) or {}
            except Exception as e:
                logger.error(f"Could not load language {self.language_code}: {e}")
                self._lang = {}

    def __getattr__(self, name):
        """Translated text if this language has the key, otherwise the English text, otherwise a visible marker."""
        if name.startswith('_'):
            raise AttributeError(name)
        if name in ("user_id", "language_code"):
            return self.__dict__.get(name)
        value = self._lang.get(name) if self._lang else None
        if not isinstance(value, str):
            if hasattr(self._en_messages, name):
                value = getattr(self._en_messages, name)
            else:
                return f"[{name}]"
        if isinstance(value, str):
            return self._format_message(value)
        return value

    def _format_message(self, template: str) -> str:
        """Fill {required_channel}, {managed_by}, {credits_bots}, {cost} from Config. Unknown braces are left as-is."""
        try:
            from CONFIG.config import Config
            required_channel = getattr(Config, "REQUIRED_CHANNEL_MENTION", "") or "@Master_x_Bots"
            managed_by = getattr(Config, "CREDITS_MANAGED_BY", "") or "\n@Anujedits76"
            credits_bots = getattr(Config, "CREDITS_BOTS", "") or "@AKDownloaderProBot\n@Anujedits76"
            cost = str(getattr(Config, "NSFW_STAR_COST", 1))
            return template.format(required_channel=required_channel, managed_by=managed_by,
                                   credits_bots=credits_bots, cost=cost)
        except Exception:
            return template


def get_messages_instance(user_id=None, language_code=None):
    return Messages(user_id, language_code)


def safe_get_messages(user_id=None, language_code=None):
    """Never fails: returns the user's language (English if none set)."""
    try:
        return get_messages_instance(user_id, language_code)
    except Exception:
        return Messages(None, 'en')


def safe_messages(user_id=None):
    return safe_get_messages(user_id)


def set_user_language(user_id, language_code):
    """Save the user's language choice (lang.txt). Returns True when saved."""
    return language_router.set_user_language(user_id, language_code)


messages = Messages(None, 'en')
