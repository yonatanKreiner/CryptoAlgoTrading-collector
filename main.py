from src.watcher import watch_markets


def log_initialize():
    with open('./error.log', 'w', encoding='UTF-8') as log_file:
        log_file.write('')


def main():
    log_initialize()
    watch_markets()


if __name__ == '__main__':
    main()
