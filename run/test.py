import os

import requests

print(requests.get("https://iw233.cn/api.php?sort=random").json())