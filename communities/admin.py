from django.contrib import admin
from communities.models import Community, CommunityPhoto, CommunityLink, Membership, CommunityTag


class CommunityPhotoInline(admin.TabularInline):
    model = CommunityPhoto
    extra = 1


class CommunityLinkInline(admin.TabularInline):
    model = CommunityLink
    extra = 1


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "created_at","subscribe_price")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [CommunityPhotoInline, CommunityLinkInline]


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "community", "is_owner", "joined_at")
    list_filter = ("is_owner",)

@admin.register(CommunityTag)
class CommunityTagAdmin(admin.ModelAdmin):
    list_display = ("name",)
