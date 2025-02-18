from ts_tally_integration.tally_integration.doctype.ts_tally_settings.ts_tally_settings import user_creation, role_creation, role_permission


def after_install():
    print("Dependencies Installing by Thirvusoft...")
    user_id = "tally@thirvusoft.co.in"
    role_name = "Tally User"
    role_creation(role_name)
    role_permission(role_name)
    user_creation(user_id)
