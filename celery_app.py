from celery import Celery

from app import app as flask_app


celery_app = Celery(
    "klasscred",
    broker=flask_app.config["CELERY_BROKER_URL"],
    include=["tasks"],
)
celery_app.conf.update(
    task_ignore_result=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
)


class FlaskContextTask(celery_app.Task):
    def __call__(self, *args, **kwargs):
        with flask_app.app_context():
            return self.run(*args, **kwargs)


celery_app.Task = FlaskContextTask
