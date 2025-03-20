from django.conf import settings

def react_assets_path(request):
    staticfiles_base = settings.STATICFILES_BASE
    build_files = settings.REACT_BUILD_DIR

    return {
        "react_assets_ts_paths": [
            str(x.relative_to(staticfiles_base)) for x in build_files.glob(".ts")
            ],
        "react_assets_css_paths": [
            str(x.relative_to(staticfiles_base)) for x in build_files.glob("*.css")
            ],
    }