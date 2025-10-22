from rest_framework import permissions

# Allow only users with role == 'customer
class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "role", None) == "customer")
    
# Allow only users with role == 'merchant'
class IsMerchant(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "role", None) == "merchant")

# Allow only staff/admin users.
class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))

# Allow customers or merchants.
class IsCustomerOrMerchant(permissions.BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return getattr(request.user, "role", None) in ("customer", "merchant")
    

# Only customers and merchants can create a wallet.
# Admins cannot create wallets via the public endpoint.
class CanCreateWallet(permissions.BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return getattr(request.user, "role", None) in ("customer", "merchant")

# Only customers and merchants can initiate transactions (credit/debit/transfer).
# (Receiving is model logic - anyone can be a receiver if wallet exists).
class CanTransact(permissions.BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return getattr(request.user, "role", None) in ("customer", "merchant")

# Only customers can apply for loans.
class CanApplyLoan(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "role", None) == "customer")