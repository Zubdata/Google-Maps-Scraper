import argparse
from scraper.frontend import Frontend


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("value", type=str, help="""Arguments being passed to script.
                        It can be: 
                        start: To start the scraper""")

    args = parser.parse_args()
    if args.value == "start":
        app = Frontend()
        print("starting...")
        app.root.protocol("WM_DELETE_WINDOW", app.closingbrowser)
        app.root.mainloop()


if __name__ == "__main__":
    main()
