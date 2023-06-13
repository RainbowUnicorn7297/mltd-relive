from datetime import timedelta, timezone

# 'zh' for Traditional Chinese, 'ko' for Korean
server_language = 'zh'
server_timezone = timezone(timedelta(
    hours=8 if server_language == 'zh' else 9))

