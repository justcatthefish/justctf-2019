### Cache Review

http://memes.web.jctf.pro

Goal: Leak admin's flag :)

Flag format: `justCTF{[a-z_]+}`


Hints
* $request_uri in our website looks like "/{sandbox_hash}/yourendpoint"
* Nginx is not caching POST request. Default value: `proxy_cache_methods GET HEAD;`
* Have you found a vuln in /api/v1/flag endpoint?


Author: *Cypis*