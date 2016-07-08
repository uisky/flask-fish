from {{ name }} import create_app

app = create_app('config.local.py')

if __name__ == '__main__':
    app.run(port=5000)