from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    
    # Este método no se ejecuta durante el POST, ya que en ese momento el objeto todavía no existe
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.author == request.user