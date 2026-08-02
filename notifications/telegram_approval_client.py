from __future__ import annotations

from collections.abc import Callable


class TelegramApprovalClient:
    def __init__(
        self,
        *,
        send_message: Callable[[str], None],
        receive_reply: Callable[[], str],
    ) -> None:
        self._send_message = send_message
        self._receive_reply = receive_reply
        self._last_processed_update_id: int | None = None

    def receive_authorized_reply(
        self,
        *,
        fetch_update: Callable[[], dict],
        authorized_chat_id: int,
        minimum_update_id: int | None = None,
        max_attempts: int | None = None,
    ) -> str:
        attempts = 0

        while (
            max_attempts is None
            or attempts < max_attempts
        ):
            update = fetch_update()
            attempts += 1

            update_id = update.get(
                "update_id"
            )

            has_update_id = isinstance(
                update_id,
                int,
            )

            if has_update_id:
                if (
                    minimum_update_id is not None
                    and update_id < minimum_update_id
                ):
                    continue

                if (
                    self._last_processed_update_id
                    is not None
                    and update_id
                    <= self._last_processed_update_id
                ):
                    continue

            elif minimum_update_id is not None:
                # Cannot safely compare old-style
                # updates without an update_id.
                continue

            if (
                update.get("chat_id")
                != authorized_chat_id
            ):
                continue

            response = str(
                update.get("text", "")
            ).strip().upper()

            if not response:
                continue

            command = response.split()[0]

            if command not in {
                "APPROVE",
                "REJECT",
            }:
                continue

            if has_update_id:
                self._last_processed_update_id = (
                    update_id
                )

            return response

        return "REJECT"

    def request_response(
        self,
        message: str,
        *,
        fetch_update: Callable[[], dict] | None = None,
        authorized_chat_id: int | None = None,
        minimum_update_id: int | None = None,
        max_attempts: int | None = None,
    ) -> str:
        self._send_message(
            message
        )

        polling_requested = (
            fetch_update is not None
            or authorized_chat_id is not None
        )

        if polling_requested:
            if (
                fetch_update is None
                or authorized_chat_id is None
            ):
                return "REJECT"

            return self.receive_authorized_reply(
                fetch_update=fetch_update,
                authorized_chat_id=authorized_chat_id,
                minimum_update_id=minimum_update_id,
                max_attempts=max_attempts,
            )

        return self._receive_reply()