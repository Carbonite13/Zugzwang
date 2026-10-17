from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from config import Config, config
import structlog as log

def create_app(config: Config) -> FastAPI:
    app = FastAPI(
        # application metadata
        title=config.APP_NAME,
        version=config.VERSION,
        description=f"The official API for {config.APP_NAME}. Developed by {config.AUTHOR}.",
        contact={
            "name": config.AUTHOR_NAME,
            "email": config.AUTHOR_EMAIL
        },

        # swaggerUI endpoint
        docs_url="/docs",

        # set failsafe, other than any epxlicit mentioning of 
        # profile as dev, the debug option will be set to false
        debug=True if config.PROFILE == "dev" else False,
    )

    app.mount(
        "/static", 
        StaticFiles(directory=Path(config.TEMPLATE_DIRECTORY)/"static"), 
        name="static"
    )

    return app