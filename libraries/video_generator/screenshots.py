import json
from playwright.async_api import ViewportSize, async_playwright, Playwright
from utils.logger import setup_logger, get_logger
from utils.data import read_reddit_json, check_ongoing, read_json, update_json
import os
from config import config
import asyncio

SCREENSHOT_HEIGHT = 800
SCREENSHOT_WIDTH = 400
COMMENT_LIMIT = 5

setup_logger()
logger = get_logger()

async def __clear_cookie_by_name(context, cookie_cleared_name):
    cookies = await context.cookies()
    filtered_cookies = [cookie for cookie in cookies if cookie["name"] != cookie_cleared_name]
    await context.clear_cookies()
    await context.add_cookies(filtered_cookies)


async def __login_to_reddit(page):
    config_data = config.load_configuration()

    try:
        await page.goto("https://www.reddit.com/login", timeout=0)
        await page.set_viewport_size(ViewportSize(width=1920, height=1080))
        
        await page.wait_for_load_state()
        
        await page.locator('[name="username"]').fill(config_data["REDDIT_USERNAME"])
        await page.locator('[name="password"]').fill(config_data["REDDIT_PASSWORD"])
        await page.locator("button[class$='m-full-width']").click()
        await page.wait_for_timeout(5000)
        
        login_error_div = page.locator(".AnimatedForm__errorMessage")
        if await login_error_div.is_visible():
            login_error_message = await login_error_div.inner_text()
            if login_error_message.strip() == "":
                # The div element is empty, no error
                pass
            else:
                logger.error("Your reddit credentials are incorrect! Please check your credentials and try again.")
        else:
            logger.info("Login successful!")
            pass
    except Exception as e:
        logger.error(f"Error logging in to Reddit: {e}")
    
async def __launching_browser(playwright):
    try:
        useragent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36"
        browser = await playwright.chromium.launch(
            headless=True,
            args=[
                f'--user-agent={useragent}',
            ]
        )  
        # Device scale factor (or dsf for short) allows us to increase the resolution of the screenshots
        # When the dsf is 1, the width of the screenshot is 600 pixels
        # so we need a dsf such that the width of the screenshot is greater than the final resolution of the video
        dsf = (SCREENSHOT_WIDTH // 600) + 1
        
        context = await browser.new_context(
            locale= "en-us",
            color_scheme="dark",
            viewport=ViewportSize(width=SCREENSHOT_WIDTH, height=SCREENSHOT_HEIGHT),
            device_scale_factor=dsf,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
        )
        try:
            cookie_file = open("config/reddit_cookie-light-mode.json", encoding="utf-8")
        except FileNotFoundError:
            print(f"Cookie file not found.")
            cookies = {}
        
        cookies = json.load(cookie_file)
        await context.add_cookies(cookies)  # load preference cookies
        page = await context.new_page()
    
        return page, browser, context
    except Exception as e:
        logger.error(f"Error launching browser: {e}")
    
    
async def __handle_redesign(page, context):
    await page.wait_for_load_state()
    # Handle the redesign
    # Check if the redesign optout cookie is set
    if await page.locator("#redesign-beta-optin-btn").is_visible():
        # Clear the redesign optout cookie
        await __clear_cookie_by_name(context, "redesign_optout")
        # Reload the page for the redesign to take effect
        await page.reload()

async def __get_thread_screenshots(post, page):
    reddit_id = post['id']
    
    # Get the thread screenshot
    await page.goto(post['url'], timeout=0)
    await page.set_viewport_size(ViewportSize(width=SCREENSHOT_WIDTH, height=SCREENSHOT_HEIGHT))
    await page.wait_for_load_state()
    await page.wait_for_timeout(5000)
    if await page.locator(
        "#SHORTCUT_FOCUSABLE_DIV > div:nth-child(7) > div > div > div > header > div > div._1m0iFpls1wkPZJVo38-LSh > button > i"
    ).is_visible():
        await page.locator(
            "#SHORTCUT_FOCUSABLE_DIV > div:nth-child(7) > div > div > div > header > div > div._1m0iFpls1wkPZJVo38-LSh > button > i"
        ).click()  # Interest popup is showing, this code will close it
    postcontentpath = f"storage/{reddit_id}/image/title.png"
    try:
        await page.locator('[data-test-id="post-content"]').screenshot(path=postcontentpath)
        logger.info(f"Post Title screenshot taken.")
        return {"name" : "title", "text" : post['title']}
    
    except Exception as e:
        logger.error('Error taking screenshot of post content: ' + str(e))
        exit()

async def __get_comment_screenshots(post, page):
    reddit_id = post['id']
    screenshot_num = 1
    comment_list = []
    logger.info(f"Total comments to take screenshot: {COMMENT_LIMIT}")
    for idx, comment in enumerate(post['comments']):
        if await page.locator('[data-testid="content-gate"]').is_visible():
            await page.locator('[data-testid="content-gate"] button').click()
        await page.goto(f'https://reddit.com{comment["url"]}', timeout=0)
        try:
            image_name = f"{screenshot_num}"
            await page.locator(f"#t1_{comment['id']}").screenshot(
                    path=f"storage/{reddit_id}/image/{image_name}.png"
            )
            logger.info(f"Comment: {comment['id']} screenshot taken.")
            
            comment_info = {'id': comment['id'], 'name': image_name, 'text': comment['body'], 'voice': False}
            comment_list.append(comment_info)
            
            screenshot_num += 1
        except TimeoutError:
            logger.error("TimeoutError: Skipping screenshot...")
            continue
        
        if screenshot_num >= COMMENT_LIMIT+1:
            break
        
    return comment_list

def __check_if_screenshot_exists(reddit_id, video_info):
    if video_info["name"] == "" or video_info["comments"] == []:
        logger.info(f"Comment screenshot is missing. Retaking screenshots...")
        return False
        
    
    title_path = f"storage/{reddit_id}/image/title.png"
    if os.path.exists(title_path):
        # Check if all comment screenshots exist
        for i in range(1, COMMENT_LIMIT+1):
            comment_path = f"storage/{reddit_id}/image/{i}.png"
            if not os.path.exists(comment_path):
                logger.info(f"Comment screenshot is missing. Retaking screenshots...")
                return False

        return True

    return False

async def get_screenshots_of_reddit_posts():
    reddit_id = check_ongoing()
    video_info = read_json(reddit_id)
    
    if __check_if_screenshot_exists(reddit_id, video_info):
        logger.info(f"Post {reddit_id} already has screenshots. Skipping...")
        return None
        
    
    reddit_post = read_reddit_json(reddit_id)
    
    
    video_info['subreddit'] = reddit_post['subreddit']
    video_info['title'] = reddit_post['title']
    video_info['url'] = reddit_post['url']

    async with async_playwright() as playwright:
        logger.info("Launching Headless Browser...")
        page, browser, context = await __launching_browser(playwright)
            
        logger.info("Login to Reddit...")
        await __login_to_reddit(page)

        logger.info("Handling Redesign...")
        await __handle_redesign(page, context)
         
        logger.info("Taking screenshots...")
        post_list = await __get_thread_screenshots(reddit_post, page)
        comment_list  = await __get_comment_screenshots(reddit_post, page)
        
        video_info['name'] = post_list['name']
        video_info['comments'] = comment_list
        update_json(video_info)
        
        await browser.close()   
        