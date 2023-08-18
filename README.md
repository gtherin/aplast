### 🤿 The aim of this app is help divers to optimize their gear.
Athletes should fill their diving performances 📉, their gliding characteristics 🐬 and body characteristics👽.

**It will finally generate gear recommendations.** ⚓ 

[![CC-by-nc-sa license](https://badgen.net/badge/icon/CC%20by-nc-sa?label=Licence)](https://creativecommons.org/licenses/by-nc-sa/4.0)

### Quick Installation guide

```bash
# 📋 Clone the code from github
git clone https://github.com/guydegnol/aplast
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

# options-2-trees

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/guydegnol/aplast/main/app.py) 

https://github.com/guydegnol/aplast/edit/master/README.md

A graphical visualisation of the Cox-Ross-Rubinstein options pricing model made interactive with Streamlit. Feel free to play around with the parameters or the source code!

https://user-images.githubusercontent.com/79203609/120888876-93f50d00-c5f2-11eb-91a0-bef1c410602d.mp4



