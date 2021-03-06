# Webhooks for external integrations.
from typing import Any, Mapping, Optional, Tuple

import orjson
from django.http import HttpRequest, HttpResponse

from zerver.decorator import return_success_on_head_request, webhook_view
from zerver.lib.exceptions import UnsupportedWebhookEventType
from zerver.lib.request import REQ, has_request_variables
from zerver.lib.response import json_success
from zerver.lib.webhooks.common import check_send_webhook_message
from zerver.models import UserProfile

from .board_actions import SUPPORTED_BOARD_ACTIONS, process_board_action
from .card_actions import IGNORED_CARD_ACTIONS, SUPPORTED_CARD_ACTIONS, process_card_action


@webhook_view("Trello")
@return_success_on_head_request
@has_request_variables
def api_trello_webhook(
    request: HttpRequest,
    user_profile: UserProfile,
    payload: Mapping[str, Any] = REQ(argument_type="body"),
) -> HttpResponse:
    payload = orjson.loads(request.body)
    action_type = payload["action"].get("type")
    message = get_subject_and_body(payload, action_type)
    if message is None:
        return json_success(request)
    else:
        subject, body = message

    check_send_webhook_message(request, user_profile, subject, body)
    return json_success(request)


def get_subject_and_body(payload: Mapping[str, Any], action_type: str) -> Optional[Tuple[str, str]]:
    if action_type in SUPPORTED_CARD_ACTIONS:
        return process_card_action(payload, action_type)
    if action_type in IGNORED_CARD_ACTIONS:
        return None
    if action_type in SUPPORTED_BOARD_ACTIONS:
        return process_board_action(payload, action_type)

    raise UnsupportedWebhookEventType(action_type)
