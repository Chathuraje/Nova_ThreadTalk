

if __name__ == "__main__":
    from config.config import set_mode
    STAGE = "DEVELOPMENT" # PRODUCTION or DEVELOPMENT
    set_mode(STAGE)
    
    import uvicorn
    from utils.logger import setup_logger, get_logger

    setup_logger()
    logger = get_logger()
    
    logger.info(f"Starting...: MODE - {STAGE}") 
    uvicorn.run("app.main:app", host="0.0.0.0", port=1234, log_config=None)
    logger.info(f"Running...: MODE - {STAGE}")

    
