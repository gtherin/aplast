
The aim of this package is help divers to optimize their gear.


### Procfile
web: gunicorn gettingstarted.wsgi
web: sh setup.sh && streamlit run app.py

### Heroku

To test the package localy
```bash
heroku local
```

heroku ps:scale web=0
heroku ps:scale web=1
heroku restart

git add . && git commit -m "Some push" && git push heroku master
heroku logs --tail
heroku builds:cache:purge -a aplast --confirm aplast

killall streamlit

python setup.py develop

git remote set-url heroku https://git.heroku.com/aplast.git