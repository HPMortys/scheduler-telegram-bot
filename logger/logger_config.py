import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filemode='w', filename='app.log')

handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
