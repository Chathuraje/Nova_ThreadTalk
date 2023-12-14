from libraries.reddit import get_top_reddit_post

def main():
    reddit_data = get_top_reddit_post("AskReddit")
    
if __name__ == "__main__":
    main()