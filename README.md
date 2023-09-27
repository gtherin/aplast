### 🤿 The aim of this app is help divers to optimize their gear.
Athletes should fill their diving performances 📉, their gliding characteristics 🐬 and body characteristics👽.

**It will finally generate gear recommendations.** ⚓ 

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://aplast.streamlit.app/) 
[![CC-by-nc-sa license](https://badgen.net/badge/icon/CC%20by-nc-sa?label=Licence)](https://creativecommons.org/licenses/by-nc-sa/4.0)


https://github.com/gtherin/aplast/assets/82407580/3116c847-bbb2-4f0f-b525-f932c4a091e4


### Quick local Installation guide

```bash
# 📋 Clone the code from github
git clone https://github.com/gtherin/aplast
# 🐋 Build the app with docker
docker build . -t aplast-image
# 🤿 Launch the web app on the local server (opened on port 8503)
docker run -p 8503:8503 --name aplast-container aplast-image
```

>**Other command tips:**
```bash
# To restart the local container
docker restart aplast-container

# Kill all containers
docker stop $(docker ps -a -q) && docker rm $(docker ps -a -q)
```



