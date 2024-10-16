from django import template

register = template.Library()

@register.filter
def youtube_embed(url):
    if "watch?v=" in url:
        video_id = url.split("watch?v=")[-1]
        return f"https://www.youtube.com/embed/{video_id}"
    return url  # Return original if not a valid YouTube URL
