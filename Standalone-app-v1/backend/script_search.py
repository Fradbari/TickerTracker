import re

with open('src/market_data/services/yahoo_provider.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_func = re.search(r'    async def search_symbol\(self, query: str\) -> list\[dict\]:.*?return \[\]\n        except Exception:\n            return \[\]', text, re.DOTALL)

if old_func:
    new_func = '''    async def search_symbol(self, query: str) -> list[dict]:
        """
        Search for symbols using Yahoo Finance.
        Uses public undocumented API for actual search.
        
        Args:
            query: Search query
            
        Returns:
            List of matching symbols
        """
        try:
            url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10.0)
                if response.status_code != 200:
                    return []
                
                data = response.json()
                quotes = data.get("quotes", [])
                results = []
                for q in quotes:
                    if "symbol" in q:
                        results.append({
                            "symbol": q["symbol"],
                            "name": q.get("longname") or q.get("shortname", ""),
                            "exchange": q.get("exchange", "")
                        })
                return results
                
        except Exception:
            return []'''
            
    new_text = text.replace(old_func.group(0), new_func)
    
    with open('src/market_data/services/yahoo_provider.py', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("Done")
else:
    print("Not found")

