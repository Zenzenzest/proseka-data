from scripts.extract import extract_and_diff
from scripts.update_cards import update_cards
from scripts.update_banners import update_banners
from scripts.update_events import update_events
from scripts.cleanup import cleanup

def main():
    extract_and_diff("local")
    update_cards()
    update_banners()
    update_events()
    cleanup()

if __name__ == "__main__":
    main()
