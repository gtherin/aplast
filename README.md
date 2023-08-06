
The aim of this package is help divers to optimize their gear.


### Quick Installation guide

```bash
# 📋 Clone the code from github
git clone https://github.com/guydegnol/aplast
# 🐋 Build the app with docker
docker build . -t aplast-image
# 🤿 Launch the web app on the local server (opened on port 8503)
docker run -p 8503:8503 --name aplast-container aplast-image

# To restart the local container
docker restart aplast-container

# Kill all containers
docker stop $(docker ps -a -q) && docker rm $(docker ps -a -q)
```

