import json
from pathlib import Path
from playwright.sync_api import ViewportSize, sync_playwright
from utils.log import setup_logger, get_logger
from config.config import SCREENSHOT_HEIGHT, SCREENSHOT_WIDTH, COMMENT_LIMIT, REDDIT_PASSWORD, REDDIT_USERNAME

setup_logger()
logger = get_logger()

def __clear_cookie_by_name(context, cookie_cleared_name):
    cookies = context.cookies()
    filtered_cookies = [cookie for cookie in cookies if cookie["name"] != cookie_cleared_name]
    context.clear_cookies()
    context.add_cookies(filtered_cookies)

def __login_to_reddit(page):
    try:
        page.goto("https://www.reddit.com/login", timeout=0)
        page.set_viewport_size(ViewportSize(width=1920, height=1080))
        
        page.wait_for_load_state()
        
        page.locator('[name="username"]').fill(REDDIT_USERNAME)
        page.locator('[name="password"]').fill(REDDIT_PASSWORD)
        page.locator("button[class$='m-full-width']").click()
        page.wait_for_timeout(5000)
        
        login_error_div = page.locator(".AnimatedForm__errorMessage").first
        if login_error_div.is_visible():
            login_error_message = login_error_div.inner_text()
            if login_error_message.strip() == "":
                # The div element is empty, no error
                pass
            else:
                # The div contains an error message
                logger.error("Your reddit credentials are incorrect! Please check your credentials and try again.")
                exit()
        else:
            logger.info("Login successful!")
            pass
    except Exception as e:
        logger.error(f"Error logging in to Reddit: {e}")
        exit()
    
def __launching_browser(cookie_file, p):
    browser = p.chromium.launch(
        headless=True
    )  # headless=False will show the browser for debugging purposes
    # Device scale factor (or dsf for short) allows us to increase the resolution of the screenshots
    # When the dsf is 1, the width of the screenshot is 600 pixels
    # so we need a dsf such that the width of the screenshot is greater than the final resolution of the video
    dsf = (SCREENSHOT_WIDTH // 600) + 1
    context = browser.new_context(
        locale= "en-us",
        color_scheme="dark",
        viewport=ViewportSize(width=SCREENSHOT_WIDTH, height=SCREENSHOT_HEIGHT),
        device_scale_factor=dsf,
    )
    cookies = json.load(cookie_file)
    cookie_file.close()
    context.add_cookies(cookies)  # load preference cookies
    page = context.new_page()
    
    return page, browser, context
    
    
def __handle_redesign(page, context):
    page.wait_for_load_state()
    # Handle the redesign
    # Check if the redesign optout cookie is set
    if page.locator("#redesign-beta-optin-btn").is_visible():
        # Clear the redesign optout cookie
        __clear_cookie_by_name(context, "redesign_optout")
        # Reload the page for the redesign to take effect
        page.reload()

def __get_thread_screenshots(post, page):
    reddit_id = post['id']
    
    # Get the thread screenshot
    page.goto(post['url'], timeout=0)
    page.set_viewport_size(ViewportSize(width=SCREENSHOT_WIDTH, height=SCREENSHOT_HEIGHT))
    page.wait_for_load_state()
    page.wait_for_timeout(5000)
    if page.locator(
        "#SHORTCUT_FOCUSABLE_DIV > div:nth-child(7) > div > div > div > header > div > div._1m0iFpls1wkPZJVo38-LSh > button > i"
    ).is_visible():
        page.locator(
            "#SHORTCUT_FOCUSABLE_DIV > div:nth-child(7) > div > div > div > header > div > div._1m0iFpls1wkPZJVo38-LSh > button > i"
        ).click()  # Interest popup is showing, this code will close it
    postcontentpath = f"storage/{reddit_id}/image/title.png"
    try:
        page.locator('[data-test-id="post-content"]').screenshot(path=postcontentpath)
        logger.info(f"Post Title screenshot taken.")
        return {"name" : "title", "text" : post['title']}
    
    except Exception as e:
        logger.error('Error taking screenshot of post content: ' + str(e))
        exit()

def __get_comment_screenshots(post, page):
    reddit_id = post['id']
    screenshot_num = 1
    comment_list = []
    logger.info(f"Total comments to take screenshot: {COMMENT_LIMIT}")
    for idx, comment in enumerate(post['comments']):
        if page.locator('[data-testid="content-gate"]').is_visible():
            page.locator('[data-testid="content-gate"] button').click()
        page.goto(f'https://reddit.com{comment["comment_url"]}', timeout=0)
        try:
            image_name = f"{screenshot_num}"
            page.locator(f"#t1_{comment['comment_id']}").screenshot(
                    path=f"storage/{reddit_id}/image/{image_name}.png"
            )
            logger.info(f"Comment: {comment['comment_id']} screenshot taken.")
            
            comment_info = {'id': comment['comment_id'], 'name': image_name, 'text': comment['body']}
            comment_list.append(comment_info)
            
            screenshot_num += 1
        except TimeoutError:
            logger.error("TimeoutError: Skipping screenshot...")
            continue
        
        if screenshot_num >= COMMENT_LIMIT+1:
            break
        
    return comment_list

def get_screenshots_of_reddit_posts(reddit_post):
    result_data = []
    
    reddit_id = reddit_post['id']
        
    Path(f"storage/{reddit_id}/image").mkdir(parents=True, exist_ok=True)
    cookie_file = open("config/reddit_cookie-light-mode.json", encoding="utf-8")

    with sync_playwright() as p:
        logger.info("Launching Headless Browser...")
        page, browser, context = __launching_browser(cookie_file, p)
            
        logger.info("Login to Reddit...")
        __login_to_reddit(page)

        logger.info("Handling Redesign...")
        __handle_redesign(page, context)
            
        logger.info("Taking screenshots...")
        post_list = __get_thread_screenshots(reddit_post, page)
        comment_list = __get_comment_screenshots(reddit_post, page)
            
        data = {
            'id': reddit_id,
            'name': post_list['name'],
            'title': post_list['text'],
            'url': reddit_post['url'],
            'comments': comment_list
        }
        
        browser.close() # close browser instance when we are done using it    
        
        return data