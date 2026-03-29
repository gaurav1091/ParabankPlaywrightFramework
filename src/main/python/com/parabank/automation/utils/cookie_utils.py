class CookieUtils:
    @staticmethod
    def build_cookie_header(cookies: list[dict]) -> str:
        cookie_parts: list[str] = []

        for cookie in cookies:
            name = cookie.get("name")
            value = cookie.get("value")

            if name and value:
                cookie_parts.append(f"{name}={value}")

        return "; ".join(cookie_parts)
