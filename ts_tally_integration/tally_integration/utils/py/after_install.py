from ts_tally_integration.tally_integration.doctype.ts_tally_settings.ts_tally_settings import user_creation, role_creation, role_permission


def after_install():
    user_id = "tally@thirvusoft.co.in"
    role_name = "Tally User"
    print("Creating Role...")
    role_creation(role_name)
    print("Role Created")
    print("Creating Permissions...")
    role_permission(role_name)
    print("Permissions Created")
    print("Creating Tally User...")
    user_creation(user_id)
    print("Tally User Created")