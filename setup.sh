mkdir -p ~/.streamlit/

echo "\
[general]
email = \"gt@guydegnol.net\"
" > ~/.streamlit/credentials.toml

echo "\
[server]
headless = true
enableCORS=false
port = 8503

[logger]
# Level of logging: 'error', 'warning', 'info', or 'debug'.
level = \"info\"


[theme]
backgroundColor='#F0FDFA11'
secondaryBackgroundColor='#4F77AA11'

primaryColor='#4F77AA'
textColor = '#581845'
font ='sans serif'
" > ~/.streamlit/config.toml