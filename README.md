# adFreeSearch

A private, security oriented search engine

### Features

- [x] Self Hostable, you can build this on docker with the provided Docker files or just run it through the main.py file.
- [x] Google link based tracker stripping
- [x] Ranking of results based on multiple sources
- [x] A proxy (masks the client's IP as the server is making the request, stripping then forwarding it on) &larr; needs more work but exists in an alpha state. Currently strips script elements if it is detected to reference external JS files. Common web building frameworks will need to be added in the future.
- [x] Minimalist design, free of ads or any images (speeds up render times)
- [x] No JS
- [x] Doesn't store IPs, queries (except when it may print on the console (usually an accident of mine for forgetting to remove or comment out print statements used in testing))
- [x] All interactions are made through POST requests
- [x] A widget sidebar (shows up based on the queries featuring information from a variety of sources)
- [x] Image search (only deviantart right now)

### To-Dos

- [ ] Add support for commonly used JS frameworks so sites don't simply break.
- [ ] Add support for proxying pages past the initial page (dealing with link elements and possibly converting them into POST requests to be proxied and forwarded)
- [ ] Dark Mode
- [ ] Add more image sources
- [ ] Add adjustable settings
- [ ] Add video search
- [ ] Possibly a maps function (likely through OSM - Open Street Maps)
- [ ] Other sources other than just Google (Might end up like SearX but I don't want to make the search engine bloated and slow)

## How to run (Basic)
*Prerequisite: Have Docker installed to your system*

1. Run this command in the terminal:

    This will only install the adfreesearch search engine to docker, allowing you to open the webpage without any encryption. **Only doing this much may be insecure as well as posing as a privacy risk if you intend on port forwarding the server to the internet.**
    
    > docker run -d -p EXTERNAL_PORT:5000 ghcr.io/isaac-to/adfreesearch:master
    
    * replace EXTERNAL_PORT with the port of your choosing.

### HTTPS/TLS encryption (Optional but highly reccomended)

This can be done a couple different ways, but I reccomend using caddy which poses as a reverse proxy. Caddy will automatically generate a Let's Encrypt Certificate to apply TLS encryption to all outgoing traffic.

2. Install Caddy on the host computer **OR** run Caddy on a docker network that can access the other image

3. Run this command in the terminal:
    
    This will create a reverse proxy from your designated port in step 1 to port **443** the default SSL port.

    > caddy reverse-proxy --to 127.0.0.1:ADFREESEARCHPORT
    * replace ADFREESEARCHPORT with the port that you assigned to the adfreesearch container when you initialized it

4. You should now be able to access the site from port **443** with HTTPS/TLS encryption enabled. You may notice that it is using a self signed certificate if you're accessing the site through an IP. Don't worry, once there is a domain name pointing to the server and you're accessing the site through that domain name, Caddy will **automatically** generate a Let's Encrypt Certificate and apply it.