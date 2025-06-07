import os
import requests
from dotenv import load_dotenv

load_dotenv()

class DonutSMP:
    BASE_URL = "https://api.donutsmp.net/v1"
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("DONUTSMP_API")
        self.response_ah = None

    def _headers(self):
        return {
            "accept": "application/json",
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }

    def get_item(self, item, sort="lowest_price", index=0):
        url = f"{self.BASE_URL}/auction/list/1"
        payload = {"search": item, "sort": sort}
        try:
            res = requests.get(url, headers=self._headers(), json=payload)
            res.raise_for_status()
            self.response_ah = res.json()
        except Exception as e:
            self.response_ah = {"error": str(e)}
        return self  # For chaining

    def _get_entry(self, index=0):
        try:
            return self.response_ah.get("result", [])[index]
        except Exception as e:
            return {"error": str(e)}

    def get_seller(self, index):
        entry = self._get_entry(index)
        return entry.get("seller", {}).get("name", "Unknown") if isinstance(entry, dict) else entry

    def get_price(self, index):
        entry = self._get_entry(index)
        if not isinstance(entry, dict): return entry
        return self._format_number(entry.get("price", 0))

    def get_time_left(self, index):
        entry = self._get_entry(index)
        if not isinstance(entry, dict): return entry
        millis = entry.get("time_left", 0)
        seconds = millis // 1000
        h, m, s = seconds // 3600, (seconds % 3600) // 60, seconds % 60
        return f"{h}hr {m}min {s}sec"

    def get_item_name(self, index):
        entry = self._get_entry(index)
        if not isinstance(entry, dict): return entry
        item_id = entry.get("item", {}).get("id", "Unknown")
        return item_id.replace("minecraft:", "").replace("_", " ")

    def get_count(self, index):
        entry = self._get_entry(index)
        if not isinstance(entry, dict): return entry
        return entry.get("item", {}).get("count", "Unknown")

    def get_stats(self, player_name):
        url = f"{self.BASE_URL}/stats/{player_name}"
        try:
            res = requests.get(url, headers=self._headers())
            res.raise_for_status()
            self.response_stats = res.json()
        except Exception as e:
            return {"error": str(e)}

        return self
    
    def get_stat(self, key):
        result = self.response_stats.get("result", {})
        
        if key == "playtime":
            try:
                millis = int(result.get("playtime", 0))  # 🔁 convert to int!
            except ValueError:
                millis = 0

            seconds = millis // 1000
            d, h, m, s = seconds // (3600 * 24), (seconds // 3600) % 24, (seconds // 60) % 60, seconds % 60
            return f"{d}d {h}h {m}m"
        else:
            return self._format_number(result.get(key, 0))
            
        

    @staticmethod
    def _format_number(n):
        try:
            n = float(n)  # convert scientific notation to float if needed
        except:
            return str(n)

        for value, suffix in [(1_000_000_000_000, "T"), (1_000_000_000, "B"),
                            (1_000_000, "M"), (1_000, "K")]:
            if n >= value:
                return f"{n / value:.2f}".rstrip("0").rstrip(".") + suffix
        return f"{n:.2f}".rstrip("0").rstrip(".")