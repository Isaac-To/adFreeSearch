# adFreeSearch

A private, security oriented search engine

## Features
- [x] Self Hostable, you can build this on docker with the provided Docker files or just run it through the main.py file.
- [x] Google link based tracker stripping
- [x] A proxy (masks the client's IP as the server is making the request, stripping then forwarding it on) &larr; needs more work but exists in an alpha state. Currently strips script elements if it is detected to reference external JS files. Common web building frameworks will need to be added in the future.
- [x] Minimalist design, free of ads or any images (speeds up render times)
- [x] No JS
- [x] Doesn't store IPs, queries (except when it may print on the console (usually an accident of mine for forgetting to remove or comment out print statements used in testing))
- [x] All interactions are made through POST requests
- [x] A widget sidebar (shows up based on the queries featuring information from a variety of sources)

## To-Dos
- [ ] Add support for commonly used JS frameworks so sites don't simply break.
- [ ] Add support for proxying pages past the initial page (dealing with link elements and possibly converting them into POST requests to be proxied and forwarded)
- [ ] Dark Mode
- [ ] Add image search
- [ ] Add video search
- [ ] Possibly a maps function (likely through OSM - Open Street Maps)
- [ ] Other sources other than just Google (Might end up like SearX but I don't want to make the search engine bloated and slow)
