from database import add_user, get_user, use_compression, grant_free_access, revoke_free_access

test_user_id = 123456789
add_user(test_user_id)
user = get_user(test_user_id)
print("User added:", user)
