from run_parser import run_parser
from run_parser_GPT import run_parser_gpt


def main():
    # start with page 5, we get all the links to other pages on this one
    sunlight = 'https://sunlight.net/catalog/page-5/'
    run_parser(sunlight)


if __name__ == '__main__':
    main()
