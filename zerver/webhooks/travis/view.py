# Webhooks for external integrations.
from typing import Dict

from django.http import HttpRequest, HttpResponse

from zerver.decorator import webhook_view
from zerver.lib.request import REQ, has_request_variables
from zerver.lib.response import json_success
from zerver.lib.validator import check_bool, check_dict, check_string
from zerver.lib.webhooks.common import check_send_webhook_message
from zerver.models import UserProfile

GOOD_STATUSES = ["Passed", "Fixed"]
BAD_STATUSES = ["Failed", "Broken", "Still Failing", "Errored", "Canceled"]
PENDING_STATUSES = ["Pending"]
ALL_EVENT_TYPES = [
    "push",
    "pull_request",
]

MESSAGE_TEMPLATE = """\
Author: {}
Build status: {} {}
Details: [changes]({}), [build log]({})"""


@webhook_view("Travis", all_event_types=ALL_EVENT_TYPES)
@has_request_variables
def api_travis_webhook(
    request: HttpRequest,
    user_profile: UserProfile,
    ignore_pull_requests: bool = REQ(json_validator=check_bool, default=True),
    message: Dict[str, object] = REQ(
        "payload",
        json_validator=check_dict(
            [
                ("author_name", check_string),
                ("status_message", check_string),
                ("compare_url", check_string),
            ]
        ),
    ),
) -> HttpResponse:
    event = str(message["type"])
    message_status = message["status_message"]
    if ignore_pull_requests and message["type"] == "pull_request":
        return json_success(request)

    if message_status in GOOD_STATUSES:
        emoji = ":thumbs_up:"
    elif message_status in BAD_STATUSES:
        emoji = ":thumbs_down:"
    elif message_status in PENDING_STATUSES:
        emoji = ":counterclockwise:"
    else:
        emoji = f"(No emoji specified for status '{message_status}'.)"

    body = MESSAGE_TEMPLATE.format(
        message["author_name"],
        message_status,
        emoji,
        message["compare_url"],
        message["build_url"],
    )
    topic = "builds"

    check_send_webhook_message(request, user_profile, topic, body, event)
    return json_success(request)
