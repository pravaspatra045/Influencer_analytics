from dataclasses import dataclass, field


@dataclass
class NotificationRequest:
    """
    Notification request object.
    """

    user: object

    title: str

    message: str

    category: str

    notification_type: str

    template: str | None = None

    subject: str | None = None

    context: dict = field(default_factory=dict)

    payload: dict = field(default_factory=dict)

    cc: list = field(default_factory=list)

    bcc: list = field(default_factory=list)
