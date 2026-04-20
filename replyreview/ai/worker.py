from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from replyreview.ai.client import AIAuthError, AIClient
from replyreview.models import ReviewData


class WorkerSignals(QObject):
    """ReplyWorker가 발행하는 시그널 컨테이너."""

    finished = Signal(str)
    # API 키 인증 실패 시 발행. 파라미터 없음.
    auth_error = Signal()
    # 네트워크 오류 등 일반 예외 발생 시 발행.
    error = Signal(str)


class ReplyWorker(QRunnable):
    """백그라운드 스레드에서 AIClient.generate_reply를 호출하는 워커."""

    def __init__(self, client: AIClient, review: ReviewData) -> None:
        super().__init__()
        self._client = client
        self._review = review
        self.signals = WorkerSignals()

    @Slot()
    def run(self) -> None:
        try:
            reply = self._client.generate_reply(self._review)
            self.signals.finished.emit(reply)
        except AIAuthError:
            self.signals.auth_error.emit()
        except Exception as e:
            self.signals.error.emit(str(e))
