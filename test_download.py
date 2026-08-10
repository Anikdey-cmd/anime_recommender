import requests

query = '''
query ($search: String) {
  Media(search: $search, type: ANIME) {
    coverImage { large }
  }
}
'''
r = requests.post("https://graphql.anilist.co", json={"query": query, "variables": {"search": "Cowboy Bebop"}}, timeout=10)
print(r.status_code)
print(r.text[:300])