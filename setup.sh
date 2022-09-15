mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"gt@guydegnol.net\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
[logger]\n\
# Level of logging: 'error', 'warning', 'info', or 'debug'.\n\
# Default: 'info'\n\
level = \"debug\"\n\
" > ~/.streamlit/config.toml