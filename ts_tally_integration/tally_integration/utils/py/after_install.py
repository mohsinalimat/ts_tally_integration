from ts_tally_integration.tally_integration.utils.py.user import user_creation


def after_install():
    print("Creating Tally User...")
    user_creation()
    print("Tally User Created")
