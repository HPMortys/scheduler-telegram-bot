task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Europe/Kyiv'
enable_utc = True

task_routes = {
                  'celery_tasks.scheduler_task': {'queue': 'scheduler'},
              }

beat_schedule = {
    'test_scheduler': {
        'task': 'celery_tasks.scheduler_task',
        'schedule': 29.0
    }
}
