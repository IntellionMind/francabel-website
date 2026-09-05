"""Optional free Graph API / LinkedIn token publish. Tokens are not passwords. Failures are shown, never faked."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

FB_FEED = "https://graph.facebook.com/v19.0/me/feed"
LI_USERINFO = "https://api.linkedin.com/v2/userinfo"
LI_UGC = "https://api.linkedin.com/v2/ugcPosts"


def publish_facebook_page(token: str, message: str) -> tuple[bool, str]:
    token = (token or "").strip()
    if not token:
        return False, "No Facebook Page access token in Shop. This is not a login password — paste a Page token from Graph API Explorer (pages_manage_posts). Publishing was not attempted."
    data = urllib.parse.urlencode({"message": message, "access_token": token}).encode("utf-8")
    req = urllib.request.Request(FB_FEED, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="replace")
        return True, f"Graph API accepted the post (free Page publish).\n{body}"
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", errors="replace")
        return False, f"Facebook Graph API returned HTTP {exc.code}. The post was NOT published.\n{err}"
    except urllib.error.URLError as exc:
        return False, f"Could not reach Graph API. The post was NOT published.\n{exc}"
    except Exception as exc:
        return False, f"Publish failed. The post was NOT published.\n{exc}"


def publish_linkedin(token: str, message: str) -> tuple[bool, str]:
    token = (token or "").strip()
    if not token:
        return False, "No LinkedIn access token in Shop. This is not a login password. Publishing was not attempted."
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    try:
        req = urllib.request.Request(LI_USERINFO, headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            info = json.loads(resp.read().decode("utf-8", errors="replace"))
        sub = str(info.get("sub") or "").strip()
        if not sub:
            return False, "LinkedIn token did not return a user id (sub). The post was NOT published.\n" + json.dumps(info)[:800]
        body = {
            "author": f"urn:li:person:{sub}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": message},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }
        req2 = urllib.request.Request(
            LI_UGC,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req2, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        return True, f"LinkedIn accepted the share.\n{raw}"
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", errors="replace")
        return False, f"LinkedIn API returned HTTP {exc.code}. The post was NOT published.\n{err}"
    except urllib.error.URLError as exc:
        return False, f"Could not reach LinkedIn. The post was NOT published.\n{exc}"
    except Exception as exc:
        return False, f"Publish failed. The post was NOT published.\n{exc}"
